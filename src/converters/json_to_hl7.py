import json

def convert_json_to_hl7(json_data):
    # Ensure `json_data` is properly loaded
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input: {e}")

    # If input is a dictionary, wrap it in a list
    if isinstance(json_data, dict):
        json_data = [json_data]

    if not isinstance(json_data, list) or not all(isinstance(record, dict) for record in json_data):
        raise TypeError("Input JSON data must be a list of dictionaries or a single dictionary.")

    # Initialize HL7 message
    hl7_message = []

    # Process each record
    for record in json_data:
        # Create the MSH segment
        msh_segment = f"MSH|^~\\&|Chem-Labs|{record.get('facility_name', 'Unknown')}|||||ORU^R01|||2.5"
        hl7_message.append(msh_segment)

        # Create the PID segment
        pid_segment = (
            f"PID|||{record.get('patient_id', 'Unknown')}||"
            f"{record.get('patient_name', 'Unknown')}||"
            f"{record.get('patient_birthday', 'Unknown')}|"
            f"{record.get('patient_sex', 'Unknown')}|||"
        )
        hl7_message.append(pid_segment)

        # Create the OBR segment (Observation Request)
        obr_segment = (
            f"OBR|1|{record.get('id', '')}||"
            f"{record.get('test_panel_name', 'Unknown')}|||"
        )
        hl7_message.append(obr_segment)

        # Create the OBX segment (Observation Result)
        obx_segment = (
            f"OBX|1|NM|{record.get('test_panel_id', 'Unknown')}||"
            f"{record.get('result', 'Unknown')}|{record.get('unit_of_measurement', 'Unknown')}|"
        )
        hl7_message.append(obx_segment)

    # Combine all segments into a single HL7 message with newline separators
    return "\n".join(hl7_message)

