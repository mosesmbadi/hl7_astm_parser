import json

def convert_json_to_astm(json_data):
    print(f'Json Data is: {json_data}')
    # Ensure `json_data` is a list of dictionaries
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input: {e}")

    # Initialize ASTM message as a list to store each segment
    astm_message = []

    # Proceed with the rest of the function logic
    if isinstance(json_data, list) and json_data:
        first_record = json_data[0]
        header_segment = (
            f"H|\\^&|||{first_record.get('equipment', 'Unknown')}|||||||||"
            f"{first_record.get('date_created', 'Unknown')}||||||||"
        )
        astm_message.append(header_segment)

    for record in json_data:
        if not isinstance(record, dict):
            raise ValueError(f"Invalid record format: expected a dictionary, got {type(record)}")

        patient_segment = (
            f"P|1|||{record.get('patient_id', 'Unknown')}|"
            f"{record.get('patient_name', 'Unknown')}|"
            f"||{record.get('patient_birthday', 'Unknown')}|"
            f"{record.get('patient_sex', 'Unknown')}|"
        )
        astm_message.append(patient_segment)

        order_segment = (
            f"O|1|{record.get('id', '')}||"
            f"{record.get('test_panel_name', 'Unknown')}|||||||||||"
            f"{record.get('sample_type', 'Unknown')}|"
        )
        astm_message.append(order_segment)

        result_segment = (
            f"R|1|||{record.get('unit_of_measurement', 'Unknown')}|||"
            f"{record.get('result', '')}|||||||||"
        )
        astm_message.append(result_segment)

    return "\n".join(astm_message)

