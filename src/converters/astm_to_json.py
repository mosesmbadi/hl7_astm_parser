import re


def test_code_from(field):
    """'^^^TSH' -> 'TSH', 'CREA' -> 'CREA'"""
    parts = [part for part in field.split('^') if part]
    return parts[-1] if parts else ""


def convert_astm_to_json(astm_message):
    """
    Converts an ASTM message into one result per R record.
    sample_id is what the backend uses to find the patient's panels.
    """
    segments = re.split(r'[\r\n]+', astm_message.strip())

    results = []
    test_panel_name = ""
    patient_name = ""
    patient_id = ""
    sample_id = ""
    sample_type = ""
    date_created = ""
    facility_name = ""
    patient_birthday = ""
    patient_sex = ""

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        fields = segment.split('|')

        if fields[0] == 'H':
            facility_name = fields[4] if len(fields) > 4 else ""
            date_created = fields[13] if len(fields) > 13 else ""

        elif fields[0] == 'P':
            patient_id = fields[3] if len(fields) > 3 else ""
            patient_name = fields[5] if len(fields) > 5 else ""
            patient_birthday = fields[7] if len(fields) > 7 else ""
            patient_sex = fields[8] if len(fields) > 8 else ""
            # HumaStar sends the sample ID in P-3 and leaves O-3 empty
            sample_id = patient_id

        elif fields[0] == 'O':
            test_panel_name = test_code_from(fields[4]) if len(fields) > 4 else ""
            sample_type = fields[15] if len(fields) > 15 else ""
            # O-3 specimen ID, used by Maglumi
            if len(fields) > 2 and fields[2]:
                sample_id = component_first(fields[2])

        elif fields[0] == 'R':
            test_code = test_code_from(fields[2]) if len(fields) > 2 else test_panel_name
            # Standard ASTM puts the value in R-4; HumaStar puts it in R-9
            result = fields[3] if len(fields) > 3 and fields[3] else ""
            if not result and len(fields) > 8:
                result = fields[8]
            if not result:
                continue

            results.append({
                "sample_id": sample_id,
                "test_code": test_code or test_panel_name,
                "result": result,
                "unit_of_measurement": fields[4] if len(fields) > 4 else "",
                "patient_name": patient_name,
                "patient_id": patient_id,
                "patient_sex": patient_sex,
                "sample_type": sample_type,
                "date_created": date_created,
                "facility_name": facility_name,
                "patient_birthday": patient_birthday
            })

    return results


def component_first(field):
    """'1234567^1^1' -> '1234567'"""
    return field.split('^')[0]
