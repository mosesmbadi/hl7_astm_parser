import socket

def send_hl7_message(host='192.168.100.56', port=9091):
    '''
    Here we simulate an HL7 Equipment sending results to the parser
    which will convirt to json and send to lis as json
    '''
    # Sample HL7 data as a string (you would replace this with your actual HL7 data)
    # See README.md for more info
    # TODO: Test with HL7 from different equipment
    hl7_message = (
        "b'\\x0bMSH|^~\\&|DF5x|Dymind|||20250116101949||ORU^R01|20241024_152427_617|P|2.3.1||||||UNICODE\\r'"
        "PID|1\\rPV1|1\\r"
        "OBR|1||5|01001^Automated Count^99MRC||20241024152325|20241024152427|||||||20241024152325||||||||20250116092511||HM||||admin||||admin\\r"
        "OBX|1|IS|02001^Take Mode^99MRC||O||||||F\\r"
        "OBX|2|IS|02002^Blood Mode^99MRC||W||||||F\\rOBX|3|IS|02003^Test Mode^99MRC||CBC+DIFF||||||F\\rOBX|4|NM|30525-0^Age^LN|||yr|||||F\\r"
        "OBX|5|IS|09001^Remark^99MRC||||||||F\\rOBX|6|IS|03001^Ref Group^99MRC||General||||||F\\r"
        "OBX|7|NM|6690-2^WBC^LN||0.01|10*9/L|4.00-10.00|L~A|||F\\rOBX|8|NM|770-8^NEU%^LN||**.*|%|50.0-70.0|~A|||F\\r"
        "OBX|9|NM|736-9^LYM%^LN||**.*|%|20.0-40.0|~A|||F\\rOBX|10|NM|5905-5^MON%^LN||**.*|%|3.0-12.0|~A|||F\\r"
        "OBX|11|NM|713-8^EOS%^LN||**.*|%|0.5-5.0|~A|||F\\rOBX|12|NM|706-2^BAS%^LN||**.*|%|0.0-1.0|~A|||F\\r"
        "OBX|13|NM|751-8^NEU#^LN||***.**|10*9/L|2.00-7.00|~A|||F\\r"
        "OBX|14|NM|731-0^LYM#^LN||***.**|10*9/L|0.80-4.00|~A|||F\\r"
        "OBX|15|NM|742-7^MON#^LN||***.**|10*9/L|0.12-1.20|~A|||F\\r"
        "OBX|16|NM|711-2^EOS#^LN||***.**|10*9/L|0.02-0.50|~A|||F\\r"
        "OBX|17|NM|704-7^BAS#^LN||***.**|10*9/L|0.00-0.10|~A|||F\\r"
        "OBX|18|NM|26477-0^*ALY#^LN||***.**|10*9/L|0.00-0.20|~A|||F\\r"
        "OBX|19|NM|13046-8^*ALY%^LN||**.*|%|0.0-2.0|~A|||F\\r"
        "OBX|20|NM|11001^*LIC#^99MRC||***.**|10*9/L|0.00-0.20|~A|||F\\r"
        "OBX|21|NM|11002^*LIC%^99MRC||**.*|%|0.0-2.5|~A|||F\\r"
        "OBX|22|NM|789-8^RBC^LN||0.00|10*6/uL|3.50-5.50|L~A|||F\\r"
        "OBX|23|NM|718-7^HGB^LN||0.0|g/dL|11.0-16.0|L~A|||F\\r"
        "OBX|24|NM|4544-3^HCT^LN||0.0|%|37.0-54.0|L~A|||F\\r"
        "OBX|25|NM|787-2^MCV^LN||***.*|fL|80.0-100.0|~A|||F\\r"
        "OBX|26|NM|785-6^MCH^LN||***.*|pg|27.0-34.0|~A|||F\\r"
        "OBX|27|NM|786-4^MCHC^LN||****|g/L|320-360|~A|||F\\r"
        "OBX|28|NM|788-0^RDW-CV^LN||**.*|%|11.0-16.0|~A|||F\\r"
        "OBX|29|NM|21000-5^RDW-SD^LN||***.*|fL|35.0-56.0|~A|||F\\r"
        "OBX|30|NM|777-3^PLT^LN||0|10*3/uL|100-300|L~A|||F\\r"
        "OBX|31|NM|32623-1^MPV^LN||**.*|fL|6.5-12.0|~A|||F\\r"
        "OBX|32|NM|32207-3^PDW^LN||**.*|fL|9.0-17.0|~A|||F\\r"
        "OBX|33|NM|11003^PCT^99MRC||.***|%|0.108-0.282|~A|||Fr\\x1c\\r'"

    )

    try:
        # Create a socket connection to the TCP listener
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Send the HL7 message
        client_socket.sendall(hl7_message.encode('utf-8'))
        print("HL7 message sent successfully.")

    except Exception as e:
        print(f"Error sending HL7 message: {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    send_hl7_message()



# Below is an example HL7 message from HumaCount 5D
# b'\x0bMSH|^~\\&|DF5x|Dymind|||20250116101949||ORU^R01|20241024_152427_617|P|2.3.1||||||UNICODE\r
# PID|1\rPV1|1\r
# OBR|1||5|01001^Automated Count^99MRC||20241024152325|20241024152427|||||||20241024152325||||||||20250116092511||HM||||admin||||admin\r
# OBX|1|IS|02001^Take Mode^99MRC||O||||||F\r
# OBX|2|IS|02002^Blood Mode^99MRC||W||||||F\rOBX|3|IS|02003^Test Mode^99MRC||CBC+DIFF||||||F\rOBX|4|NM|30525-0^Age^LN|||yr|||||F\r
# OBX|5|IS|09001^Remark^99MRC||||||||F\rOBX|6|IS|03001^Ref Group^99MRC||General||||||F\r
# OBX|7|NM|6690-2^WBC^LN||0.01|10*9/L|4.00-10.00|L~A|||F\rOBX|8|NM|770-8^NEU%^LN||**.*|%|50.0-70.0|~A|||F\r
# OBX|9|NM|736-9^LYM%^LN||**.*|%|20.0-40.0|~A|||F\rOBX|10|NM|5905-5^MON%^LN||**.*|%|3.0-12.0|~A|||F\r
# OBX|11|NM|713-8^EOS%^LN||**.*|%|0.5-5.0|~A|||F\rOBX|12|NM|706-2^BAS%^LN||**.*|%|0.0-1.0|~A|||F\r
# OBX|13|NM|751-8^NEU#^LN||***.**|10*9/L|2.00-7.00|~A|||F\r
# OBX|14|NM|731-0^LYM#^LN||***.**|10*9/L|0.80-4.00|~A|||F\r
# OBX|15|NM|742-7^MON#^LN||***.**|10*9/L|0.12-1.20|~A|||F\r
# OBX|16|NM|711-2^EOS#^LN||***.**|10*9/L|0.02-0.50|~A|||F\r
# OBX|17|NM|704-7^BAS#^LN||***.**|10*9/L|0.00-0.10|~A|||F\r
# OBX|18|NM|26477-0^*ALY#^LN||***.**|10*9/L|0.00-0.20|~A|||F\r
# OBX|19|NM|13046-8^*ALY%^LN||**.*|%|0.0-2.0|~A|||F\r
# OBX|20|NM|11001^*LIC#^99MRC||***.**|10*9/L|0.00-0.20|~A|||F\r
# OBX|21|NM|11002^*LIC%^99MRC||**.*|%|0.0-2.5|~A|||F\r
# OBX|22|NM|789-8^RBC^LN||0.00|10*6/uL|3.50-5.50|L~A|||F\r
# OBX|23|NM|718-7^HGB^LN||0.0|g/dL|11.0-16.0|L~A|||F\r
# OBX|24|NM|4544-3^HCT^LN||0.0|%|37.0-54.0|L~A|||F\r
# OBX|25|NM|787-2^MCV^LN||***.*|fL|80.0-100.0|~A|||F\r
# OBX|26|NM|785-6^MCH^LN||***.*|pg|27.0-34.0|~A|||F\r
# OBX|27|NM|786-4^MCHC^LN||****|g/L|320-360|~A|||F\r
# OBX|28|NM|788-0^RDW-CV^LN||**.*|%|11.0-16.0|~A|||F\r
# OBX|29|NM|21000-5^RDW-SD^LN||***.*|fL|35.0-56.0|~A|||F\r
# OBX|30|NM|777-3^PLT^LN||0|10*3/uL|100-300|L~A|||F\r
# OBX|31|NM|32623-1^MPV^LN||**.*|fL|6.5-12.0|~A|||F\r
# OBX|32|NM|32207-3^PDW^LN||**.*|fL|9.0-17.0|~A|||F\r
# OBX|33|NM|11003^PCT^99MRC||.***|%|0.108-0.282|~A|||F\r\x1c\r