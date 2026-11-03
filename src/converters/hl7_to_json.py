import re


def component(field, index):
    """Returns the ^-separated component at index, or the whole field if it has none."""
    parts = field.split('^')
    return parts[index] if len(parts) > index else parts[0]


def is_reportable(value):
    # Analyzers send '**.*' style masks when a value couldn't be measured
    return bool(value) and not re.fullmatch(r'[*.]+', value)


def convert_hl7_to_json(hl7_str):
    """
    Converts an HL7 ORU message into one result per OBX.
    sample_id is what the backend uses to find the patient's panels.
    """
    segments = re.split(r'[\r\n]+', hl7_str.strip())

    results = []
    sample_id = ""
    patient_name = ""
    patient_id = ""

    for segment in segments:
        fields = segment.strip().split('|')

        if fields[0] == 'PID':
            patient_id = fields[3] if len(fields) > 3 else ""
            patient_name = fields[5] if len(fields) > 5 else ""

        elif fields[0] == 'SAC':
            # SAC-3 container identifier holds the sample ID on HumaCount 30TS
            if len(fields) > 3 and fields[3]:
                sample_id = sample_id or fields[3]

        elif fields[0] == 'OBR':
            # OBR-3 filler order number holds the sample ID on Dymind/HumaCount 5D,
            # OBR-2 placer order number is the fallback
            if len(fields) > 3 and fields[3]:
                sample_id = fields[3]
            elif len(fields) > 2 and fields[2]:
                sample_id = sample_id or fields[2]

        elif fields[0] == 'OBX':
            # "OBX|7|NM|6690-2^WBC^LN||0.01|10*9/L|4.00-10.00|L~A|||F"
            value_type = fields[2] if len(fields) > 2 else ""
            # IS rows are analyzer settings (Take Mode, Blood Mode...), not results
            if value_type not in ('NM', 'TX', 'ST'):
                continue

            test_code = component(fields[3], 1) if len(fields) > 3 else ""
            result_value = fields[5] if len(fields) > 5 else ""
            if not test_code or not is_reportable(result_value):
                continue

            results.append({
                "sample_id": sample_id,
                "test_code": test_code,
                "result": result_value,
                "unit_of_measurement": fields[6] if len(fields) > 6 else "",
                "reference_range": fields[7] if len(fields) > 7 else "",
                "patient_name": patient_name,
                "patient_id": patient_id
            })

    return results
