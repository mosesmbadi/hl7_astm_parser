import re


# ASTM result status codes (R-9). HumaStar file mode puts the value in R-9.
RESULT_STATUSES = {'', 'C', 'P', 'F', 'X', 'I', 'S', 'M', 'R', 'N', 'Q', 'V', 'W'}


def test_code_from(field):
    """'^^^TSH' -> 'TSH', 'CREA' -> 'CREA'"""
    parts = [part for part in field.split('^') if part]
    return parts[-1] if parts else ""


def component_first(field):
    """'1234567^1^1' -> '1234567'"""
    return field.split('^')[0]


def convert_astm_to_json(astm_message):
    """
    Converts an ASTM transmission into one run per order (one sample), each
    with the results of its R records -- the same shape convert_hl7_to_json
    returns:

        [{"sender": "HumaStar 100", "sample_id": "DDLR00012-2026",
          "patient_name": ..., "patient_id": ...,
          "results": [{"code": "CREA", "value": "1.02", "unit": "mg/dl",
                       "flag": "N", "reference_range": "0.6-1.2"}]}]

    One transmission can carry many patients; each P/O pair starts a run.
    """
    segments = re.split(r'[\r\n]+', astm_message.strip())

    runs = []
    run = None
    sender = ""
    patient_name = ""
    patient_id = ""
    order_code = ""

    def start_run(sample_id):
        new = {
            "sender": sender,
            "sample_id": sample_id,
            "patient_name": patient_name,
            "patient_id": patient_id,
            "results": [],
        }
        runs.append(new)
        return new

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        fields = segment.split('|')
        # Frame numbers sometimes survive in front of the record type ('1H')
        kind = fields[0][-1:] if fields[0] else ""

        if kind == 'H':
            # H-5 sender name or ID
            sender = component_first(fields[4]).strip() if len(fields) > 4 else ""

        elif kind == 'P':
            patient_id = fields[3].strip() if len(fields) > 3 else ""
            patient_name = " ".join(p for p in fields[5].split('^') if p) if len(fields) > 5 else ""
            # HumaStar sends the sample ID in P-3 and leaves O-3 empty
            run = start_run(patient_id)
            # HumaStar 300SR marks QC material with P-9 'Control'; not a patient
            run["qc"] = len(fields) > 8 and fields[8].strip().upper() == 'CONTROL'

        elif kind == 'O':
            order_code = test_code_from(fields[4]) if len(fields) > 4 else ""
            # O-3 specimen ID, used by Maglumi
            specimen_id = component_first(fields[2]).strip() if len(fields) > 2 else ""
            # A new specimen ID after results starts the next sample; the same
            # ID again is just another order on it.
            if run is None or (specimen_id and run["results"] and specimen_id != run["sample_id"]):
                qc = bool(run and run.get("qc"))
                run = start_run(specimen_id or patient_id)
                run["qc"] = qc
            elif specimen_id:
                run["sample_id"] = specimen_id

        elif kind == 'R':
            code = (test_code_from(fields[2]) if len(fields) > 2 else "") or order_code
            # Standard ASTM puts the value in R-4; HumaStar puts it in R-9
            value = fields[3].strip() if len(fields) > 3 and fields[3].strip() else ""
            # R-9 is the result status elsewhere (F, P, X...), never a value
            if not value and len(fields) > 8 and fields[8].strip().upper() not in RESULT_STATUSES:
                value = fields[8].strip()
            value = component_first(value).strip()
            # HumaStar writes -99000000000 for a test that was not measured
            if not code or not value or re.fullmatch(r'-9{2,}0*', value):
                continue
            if run is None:
                run = start_run(patient_id)

            run["results"].append({
                "code": code,
                "value": value,
                "unit": fields[4].strip() if len(fields) > 4 else "",
                "reference_range": fields[5].strip() if len(fields) > 5 else "",
                "flag": fields[6].strip() if len(fields) > 6 else "",
            })

    return [
        {key: value for key, value in run.items() if key != "qc"}
        for run in runs if run["results"] and not run.get("qc")
    ]
