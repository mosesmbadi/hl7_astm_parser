def convert_hl7_to_json(hl7_str):
    # Add explicit segment delimiters if missing (for testing purposes)
    hl7_str = hl7_str.replace("PID", "\rPID").replace("NTE", "\rNTE").replace("SPM", "\rSPM") \
                     .replace("SAC", "\rSAC").replace("OBR", "\rOBR").replace("OBX", "\rOBX")
    
    # Split the HL7 message by segments
    segments = hl7_str.strip().split('\r')
    
    # Initialize variables
    results = []
    test_panel_name = ""
    lab_test_request = 1
    test_panel_id = 1  # Replace this with logic to dynamically assign if needed
    record_id = 1
    patient_name  = ""
    patient_id = ""
    
    # Parse segments
    for segment in segments:
        fields = segment.split('|')

        if fields[0] == 'MSH':
            # Extract facility name or any other data from MSH if needed
            facility_name = fields[2] if len(fields) > 2 else "Unknown"
        
        elif fields[0] == 'PID':
            # Extract patient information
            patient_id = fields[3] if len(fields) > 3 else "Unknown"
            patient_name = fields[5] if len(fields) > 5 else "Unknown"
            print(f"Patient ID: {patient_id}, Name: {patient_name}")
        
        elif fields[0] == 'OBR':
            # Get the test panel name
            test_panel_name = fields[4] if len(fields) > 4 else "Unknown"
            print(f"Test Panel Name: {test_panel_name}")
        
        elif fields[0] == 'OBX':
            # "OBX|13|TX|MCHC||28.2|$g/dl|29.7-36.8|L|||P"
            # Process OBX segments for test results
            print(f'Test Panel Name, Field[3]: {fields[3]}') #MCHC
            test_code = fields[3] if len(fields) > 3 else "Unknown"
            result_value = fields[5] if len(fields) > 5 else None
            test_panel_name = fields[3] if len(fields) > 4 else "Unknown"

            # Create JSON object for each result
            result_json = {
                "id": record_id,
                "result": float(result_value) if result_value else None,
                "test_panel": test_panel_id,
                "test_panel_name": test_panel_name,
                "lab_test_request": lab_test_request,
                "patient_name": patient_name,
                "patient_id": patient_id
            }
            results.append(result_json)
            record_id += 1  # Increment record ID for each test result
    
    return results