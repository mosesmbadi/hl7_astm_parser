# hl7_astm_parser

This is a program designed to work with: https://github.com/PROTO-TYPE-SOLUTIONS/easymed

Will listen for incoming data, convert to hl7 then send to backend
Purpose: Will run alongside main system, picks incoming lab results 
from equipments, converts to json then sends to results endpoint

## How to run
1. Clone the repo: git clone https://github.com/mosesmbadi/hl7_astm_parser
2. Change directory: cd hl7_astm_parser
3. Create a virtual environment: python3 -m venv venv
4. Activate virtual environment: source venv/bin/activate (Linux) or venv\Scripts\activate (Windows)
5. Install dependencies: pip install -r requirements.txt
6. Run the program: python main.py

From there, you can try send sample data using scripts in ./coms

Testing Manually
There are three scripts you can use to test manually

1. `send_hl7.py` - This script sends a sample HL7 message to the HL7 endpoint
2. `send_astm.py` - This script sends a sample ASTM message to the ASTM endpoint
3. `send_json.py` - This script sends a sample JSON message to the JSON endpoint


!["System Design"](docs/LIS_Interfacing_Chart.drawio.png)


An lab test request endpoint might GET us this reponse 
    
    ```
    {
        "id": 1,
        "equipment": "HumaCount 5D",
        "result": Null,
        "result_approved": false,
        "test_panel": 1,
        "test_panel_name": "RBC",
        "item": "3",
        "sale_price": 3445.0,
        "patient_name": "Patient1 Patient1",
        "patient_age": 4,
        "patient_sex": "F",
        "reference_values": null,
        "lab_test_request": 1,
        "is_billed": false,
        "is_quantitative": true,
        "is_qualitative": false
    }
    ```

But from the incoming hl7 message from the equipment, we're only interested in the fields below:
    
    ```
    {
        "id": 1,
        "result": 23.2,
        "test_panel": 1,
        "test_panel_name": "RBC",
        "lab_test_request": 1
        
    }
    ```   

Here's a sample HL7 message

```
"MSH|$~\&|A3CPC||||20130816154927||ORU_R01|SAMPLE001|P|2.5.1||||||UNICODE UTF-8|||"
"PID|||PATIENT_ID001||Thomas A.||19621119000000|F"
"NTE|1||Dr. Smith"
"SPM|1|||WB|||||||P"
"SAC|||SAMPLE001"
"OBR||AWOS_ID001"
"OBX|1|TX|WBC||14.80|10^9/l|5.00-10.00|H"
"OBX|13|TX|MCHC||28.2|$g/dl|29.7-36.8|L|||P"
"OBX|22|TX|P-LCR||30.78|$%|13.00-43.00||||P"
```

The HL7 will pass through the parser, get cnvirted to json, we extract the fields we need and send a PUT request to the results endpoint as shown below:  

    ```
    curl --request PUT \
    --url http://127.0.0.1:8080/lab/lab-test-requests-panel/1/ \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NjU5MzI3LCJpYXQiOjE3MzM0OTkzMjcsImp0aSI6Ijk0MDhmM2JmYWM2YzQzODNhYWM3MTczYzUxZjQzNWNhIiwidXNlcl9pZCI6MSwiZW1haWwiOiJhZG1pbkBtYWlsLmNvbSIsImZpcnN0X25hbWUiOiJzeXNhZG1pbiIsInJvbGUiOiJzeXNhZG1pbiJ9.tgFIbkarWJFis8Y7O2cpeaUkr7q1Xq-e3o0ZPcH3J6I' \
    --header 'Content-Type: application/json' \
    --header 'User-Agent: insomnia/8.6.1' \
    --data '	{
            "id": 1,
            "result": 23.2,
            "test_panel": 1,
            "test_panel_name": "RBC",
            "lab_test_request": 1
            
        }'
    ```

and we get the updated response from the LIS/HMIS
   
    ```
    {
        "id": 1,
        "result": "23.2",
        "result_approved": false,
        "test_panel": 1,
        "test_panel_name": "RBC",
        "item": "3",
        "sale_price": 3445.0,
        "patient_name": "Patient1 Patient1",
        "patient_age": 4,
        "patient_sex": "F",
        "reference_values": null,
        "lab_test_request": 1,
        "is_billed": false,
        "is_quantitative": true,
        "is_qualitative": false
    }
    ```

The same principle will apply to ASTM messages, but the format is different.

Here's  a breakdown of an HL7 format
```MSH|$~\&|A3CPC||||20130816154927||ORU_R01|SAMPLE001|P|2.5.1||||||UNICODE UTF-8|||```
1. | is the field separator.
2. $~\& are the encoding characters.
3. A3CPC is the sending application.
4. 20130816154927 is the date/time of the message.
5. ORU_R01 is the message type.
6. SAMPLE001 is the message control ID, which contains the sample ID
of the measurement.
7. P means preliminary, which is the processing ID.
8. 2.5.1 is the version ID.
9. UNICODE UTF-8 is the character set.

```PID|||PATIENT_ID001||Thomas A.||19621119000000|F```
1. PATIENT_ID001 is the ID number of the patient identifier list.
2. Thomas A. is the patient name.
3. 19621119000000 is the date/time of birth.
4. F is the administrative sex.

```SPM|1|||WB|||||||P```
1. 1 is the ID of the SPM field.
2. WB is the specimen type. Means whole blood.
3. P is the specimen role. Means preliminary.

```SAC|||SAMPLE001```
1. SAMPLE001 is the container identifier, which contains the
sample ID.
OBR||AWOS_ID001
1. AWOS_ID001 is a unique ID, which refers to a record of the EMR.

```OBX|1|TX|WBC||14.80|10^9/l|5.00-10.00|H```
1. 1 is the ID of the OBX field. It is an increscent value.
2. TX is the value type. It means text data.
3. WBC is the observation identifier.
4. 14.80 is the observation value.
5. 10^9/l is the unit.
6. 5.00-10.00 is the reference range (normal range).
7. H means high. It is the abnormal flag.

The hl7 format above is for HumaCOunt 30TS, a Hematology Analyzer. The HL7 version is HL7V2.5.
The work here is to get the HL7 message, extract the segments and map out the fields to our corresponding fields in the JSON payload, like below
```
# Add explicit segment delimiters if missing (for testing purposes)
hl7_str = hl7_str.replace("PID", "\rPID").replace("NTE", "\rNTE").replace("SPM", "\rSPM") \
                    .replace("SAC", "\rSAC").replace("OBR", "\rOBR").replace("OBX", "\rOBX")

# Split the HL7 message by segments
segments = hl7_str.strip().split('\r')

for segment in segments:
    fields = segment.split('|')

    if fields[0] == 'PID':
        # Extract patient information
        patient_id = fields[3] if len(fields) > 3 else "Unknown"
        patient_name = fields[5] if len(fields) > 5 else "Unknown"
        print(f"Patient ID: {patient_id}, Name: {patient_name}")
```    


The unique identifier that can be used across systems to sync records is the patient ID. From the generated json, record ID are different from tests sent, but the patient ID is the same.




## TODO
1. ~~ RECEIVE HL7 MESSAGE FROM EQUIPMENT CONVIRT TO JSON AND SEND TO RESULTS ENDPOINT~~
2. ~~RECEIVE ASTM MESSAGE FROM EQUIPMENT CONVIRT TO JSON AND SEND TO RESULTS ENDPOINT~~

3. RECEIVE JSON MESSAGE FROM HMIS CONVIRT TO HL7 AND SEND HL7 EQUIPMENT
4. RECEIVE JSON MESSAGE FROM HMIS CONVIRT TO ASTM AND SEND ASTM EQUIPMENT

5. STORE LIST OF HL7 EQUIPMENT IN A VARIABLE
6. STORE LIST OF ASTM EQUIPMENT IN A VARIABLE


