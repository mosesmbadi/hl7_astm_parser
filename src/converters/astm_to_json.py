import json
import re


def convert_astm_to_json(astm_message):
    segments = astm_message.strip().split('\n')

    # Initialize variables
    results = []
    test_panel_name = ""
    lab_test_request = 1
    test_panel_id = 1
    record_id = 1
    patient_name  = ""
    patient_id = ""
    unit_of_measurement = ""
    sample_type = ""
    date_created = ""
    facility_name = ""
    patient_birthday = ""
    patient_sex = ""
    result = ""

    for segment in segments:
        # Skip empty segments which might be caused by consecutive '|'
        if not segment.strip():
            continue

        fields = segment.split('|')

        # for index, field in enumerate(fields):
        #     print(f"Field at index {index}: {field}")

        if fields[0] == 'H':
            facility_name = fields[4] if len(fields) > 4 else "Unknown"
            date_created = fields[13] if len(fields) > 13 else "Unknown"

        
        elif fields[0] == 'P':
            patient_id = fields[3] if len(fields) > 3 else "Unknown"
            patient_name = fields[5] if len(fields) > 5 else "Unknown"
            patient_birthday = fields[7] if len(fields) > 7 else "Unknown"
            patient_sex = fields[8] if len(fields) > 8 else "Unknown"

        elif fields[0] == 'O':
            test_panel_name = fields[4] if len(fields) > 4 else "Unknown"
            sample_type = fields[15] if len(fields) > 15 else "Unknown"

        elif fields[0] == "R":
            unit_of_measurement = fields[4] if len(fields) > 4 else "Unknown"
            test_completeion_date = fields[12] if len(fields) > 12 else "Unknown"
            result = fields[8] if len(fields) > 8 else "Unknown"


        result_json = {
            "id": lab_test_request,
            "test_panel_name": test_panel_name,
            "result": float(result) if result else None,
            "test_panel_id": test_panel_id,
            "record_id": record_id,
            "patient_name": patient_name,
            "patient_id": patient_id,
            "patient_sex": patient_sex,
            "sample_type": sample_type,
            "unit_of_measurement": unit_of_measurement,
            "date_created": date_created,
            "facility_name": facility_name,
            "patient_birthday": patient_birthday
        }
        results.append(result_json)
        lab_test_request += 1
        test_panel_id += 1
        record_id += 1

    return results