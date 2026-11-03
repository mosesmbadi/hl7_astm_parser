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

```OBR|1||5|01001^Automated Count^99MRC||20241024152325|20241024152427|||||||20241024152325||||||||20250116092511||HM||||admin||||admin\r```
1. 1 is the ID of the OBR field.
2. 5 is the set ID of the OBR field.
3. 01001^Automated Count^99MRC is the observation identifier.
4. 20241024152325 is the observation date/time.
5. 20241024152427 is the observation end date/time.
6. 20241024152325 is the collection date/time.
7. 20250116092511 is the result date/time.
8. HM is the result status.

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
1. Handle handshake request -response such us:

```
--><ENQ>
<--<ACK>
--><STX>
<--<ACK>
```

This is extracted from message sent by Maglumi to LIS requesting the tests to be perfromed on the sample as shown below

```
    --><ENQ>
    <--<ACK>
    --><STX>
    <--<ACK>
    -->H|\^&||PSWD|Maglumi 600|||||Lis||P|E1394-97|20100323<CR>
    Q|1|^1234567||ALL||||||||O<CR>
    L|1|N<CR>
    <--<ACK>
    --><ETX>
    <--<ACK>
    --><EOT>
    <--<ACK>
```

Refer to ./docs/Equipment Docs/Maglumi 600/ for more details

Use ASTM 1397 and 13394 for reference
Use Hl7 2.5.1 for reference



## Build and Push to Hub
Push to hub:
```bash
docker build -t mosesmbadi/hl7-astm-parser:latest .
docker push mosesmbadi/hl7-astm-parser:latest
```


docker run -d --name hl7-astm-parser --restart unless-stopped \
  -p 9091:9091 \
  -e BACKEND_URL=http://<easymed-host>:8080 \
  -e BACKEND_USERNAME=admin@mail.com \
  -e BACKEND_PASSWORD=... \
  mosesmbadi/hl7-astm-parser:latest

```bash
# Spooled results must survive the container being recreated
docker run ... -v lis_spool:/app/spool ...
```


## How results reach EasyMed

The parser only speaks the analyzers' protocols. For each sample in a
message it posts the analyzer's raw results to EasyMed's
`/lab/analyzer-messages/`:

```json
{"sender": "HumaCount 30TS", "sample_code": "DDLR00012-2026",
 "patient_name": "RUKIA OSMAN", "raw_message": "MSH|...",
 "results": [{"code": "WBC", "value": "5.39", "unit": "10^9/l",
              "flag": "", "reference_range": "5.00-11.60"}]}
```

EasyMed does the matching:

- **Which analyzer**: `sender` (HL7 MSH-3, ASTM H-5) against each lab
  equipment's *Sender ID*.
- **Which test**: the analyzer's code through that equipment's *Test
  mappings* (Lab Settings -> Lab Equipments -> Test mappings). A code named
  exactly like a requested panel is mapped automatically the first time.
- **Which patient**: `sample_code`, the EasyMed sample code
  (`DDLR00012-2026`) entered or scanned on the analyzer. Where it is read
  from: HL7 SPM-2.1 (Maglumi X8), SAC-3 (HumaCount), OBR-3 (Dymind), OBR-2,
  then MSH-10 for HumaCount only; ASTM O-3 (Maglumi, HumaStar 600), then P-3
  (HumaStar 100/200/300SR).

Per-analyzer formats, checked against the manuals and captures in
`docs/Equipment Docs` by `tests/test_converters.py`.

Anything EasyMed can't place (no sample code, unknown sample, unmapped code,
test not requested) waits in the **Analyzer Inbox** in the Laboratory
dashboard and is posted once fixed. Nothing is dropped.

If EasyMed is unreachable, results are written to `SPOOL_DIR` and retried
every `SPOOL_RETRY_SECONDS`. The analyzer is still acknowledged (HL7 `AA`),
because the results are safe on disk. An HL7 message that can't be read at
all is answered `AE`.

Tests: `python -m pytest tests`
