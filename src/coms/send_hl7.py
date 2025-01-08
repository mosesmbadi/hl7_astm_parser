import socket

def send_hl7_message(host='127.0.0.1', port=9091):
    '''
    Here we simulate an HL7 Equipment sending results to the parser
    which will convirt to json and send to lis as json
    '''
    # Sample HL7 data as a string (you would replace this with your actual HL7 data)
    # See README.md for more info
    # TODO: Test with HL7 from different equipment
    hl7_message = (
        "MSH|$~\&|A3CPC||||20130816154927||ORU_R01|SAMPLE001|P|2.5.1||||||UNICODE UTF-8|||"
        "PID|||PATIENT_ID001||Thomas A.||19621119000000|F"
        "NTE|1||Dr. Smith"
        "SPM|1|||WB|||||||P"
        "SAC|||SAMPLE001"
        "OBR||AWOS_ID001"
        "OBX|1|TX|WBC||14.80|10^9/l|5.00-10.00|H"
        "OBX|13|TX|MCHC||28.2|$g/dl|29.7-36.8|L|||P"
        "OBX|22|TX|P-LCR||30.78|$%|13.00-43.00||||P"
    )

    try:
        # Create a socket connection to the TCP listener
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Send the HL7 message
        client_socket.sendall(hl7_message.encode('utf-8'))
        print("HL7 message sent successfully.")

        # Wait for response
        response = client_socket.recv(1024).decode('utf-8')
        print("Received response:")
        print(response)

    except Exception as e:
        print(f"Error sending HL7 message: {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    send_hl7_message()



# Below is an example HL7 message from HumaCount 5D
# MSH|^~\&|BC-
# 6800|Mindray|||20140927131905||ORU^R01|2849dc32654641d2b5c8ae229cf4f061|P|2.3.1||||||UNICODE
# PID|1||05012006^^^^MR||^Miller Andrew||19991001000000|Male
# PV1|1|Inpatient|Internal medicine^1^2|||||||||||||||||Self-paid
# OBR|1||5|00001^Automated Count^99MRC||20140918091000|20140918105930|||Dr.
# Wang||||20140918103000||||||||||HM||||||||develop
# OBX|1|IS|08001^Loading Mode^99MRC||O||||||F
# OBX|2|IS|08002^Blood Mode^99MRC||W||||||F
# OBX|3|IS|08003^Test Mode^99MRC||CBC+DIFF||||||F
# OBX|4|NM|30525-0^Age^LN||15|yr|||||F
# OBX|5|IS|01001^Remark^99MRC||||||||F
# OBX|6|IS|01002^Ref Group^99MRC||Adult male||||||F
# OBX|7|NM|6690-2^WBC^LN||5.51|10*9/L|4.00-10.00||||F
# OBX|8|NM|770-8^NEU%^LN||66.1|%|50.0-70.0||||F
# OBX|9|NM|736-9^LYM%^LN||28.1|%|20.0-40.0||||F
# OBX|10|NM|5905-5^MON%^LN||4.4|%|3.0-12.0||||F
# OBX|11|NM|713-8^EOS%^LN||1.2|%|0.5-5.0||||F
# OBX|12|NM|706-2^BAS%^LN||0.2|%|0.0-1.0||||F
# OBX|13|NM|751-8^NEU#^LN||3.65|10*9/L|2.00-7.00||||F
# OBX|14|NM|731-0^LYM#^LN||1.55|10*9/L|0.80-4.00||||F
# OBX|15|NM|742-7^MON#^LN||0.24|10*9/L|0.12-1.20||||F
# OBX|16|NM|711-2^EOS#^LN||0.06|10*9/L|0.02-0.50||||F
# OBX|17|NM|704-7^BAS#^LN||0.01|10*9/L|0.00-0.10||||F
# OBX|18|NM|26477-0^*ALY#^LN||0.02|10*9/L|0.00-0.20||||F
# OBX|19|NM|13046-8^*ALY%^LN||0.3|%|0.0-2.0||||F
# OBX|20|NM|10000^*LIC#^99MRC||0.00|10*9/L|0.00-0.20||||F
# OBX|21|NM|10001^*LIC%^99MRC||0.0|%|0.0-2.5||||F
# OBX|22|NM|789-8^RBC^LN||4.57|10*12/L|4.00-5.50||||F
# OBX|23|NM|718-7^HGB^LN||156|g/L|120-160||||F
# OBX|24|NM|4544-3^HCT^LN||47.8|%|40.0-54.0||||F
# OBX|44|ED|15200^WBC DIFF Scattergram. LS-MS BMP^99MRC||^Image^BMP^Base64^……Diff scattergram bitmap
# LS-MS data…||||||F
# OBX|45|ED|15201^WBC DIFF Scattergram. LS-HS BMP^99MRC||^Image^BMP^Base64^……Diff scattergram bitmap
# LS-HS data…||||||F
# OBX|46|ED|15202^WBC DIFF Scattergram. HS-MS BMP^99MRC||^Image^BMP^Base64^……Diff scattergram bitmap
# HS-MS data…||||||F
# OBR|2||5|00002^Manual Count^99MRC