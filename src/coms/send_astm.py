import socket

def send_astm_message(host='127.0.0.1', port=9091):
    '''
    Here we simulate an ASTM equipment sending results to the parser
    which will convirt to json and send to lis as json
    '''
    astm_message = (
        "H|\^&|||Sphera^V1.0|||||Host||P|1|20160920091032\n"
        "P|1||00004|Department1|Mustermann|Max|20000000|MALE|||||||||||||||||||||||||\n"
        "C|1|||\n"
        "O|1|||Alb|False||||||||||Serum|||||||||||||||\n"
        "R|1|Alb||g/dl||||-99000000000||||00010101000000|\n"
        "O|2|||Amy|False||||||||||Serum|||||||||||||||\n"
        "R|1|Amy||U/l||||-99000000000||||00010101000000|\n"
        "O|3|||Bilda|False||||||||||Serum|||||||||||||||\n"
        "R|1|Bilda||mg/dl||||-99000000000||||00010101000000|\n"
        "O|4|||Bilta|False||||||||||Serum|||||||||||||||\n"
        "R|1|Bilta||mg/dl||||-99000000000||||00010101000000|\n"
        "O|6|||Chol|False||||||||||Serum|||||||||||||||\n"
        "R|1|Chol||mg/dl||||-99000000000||||00010101000000|\n"
        "P|2||00005|Department2|Musterfrau|Minna|20010000|FEMALE|||||||||||||||||||||||||\n"
        "C|2|||\n"
        "O|1|||CK|False||||||||||Serum|||||||||||||||\n"
        "R|1|CK||U/l||||-99000000000||||00010101000000|\n"
        "O|2|||CK-MB|False||||||||||Serum|||||||||||||||\n"
        "R|1|CK-MB||U/l||||-99000000000||||00010101000000|\n"
        "O|3|||Cl|False||||||||||Serum|||||||||||||||\n"
        "R|1|Cl||mmol/L||||-99000000000||||00010101000000|\n"
        "O|4|||CreaA|False||||||||||Serum|||||||||||||||\n"
        "R|1|CreaA||mg/dl||||-99000000000||||00010101000000|\n"
        "O|6|||Glu|False||||||||||Serum|||||||||||||||\n"
        "R|1|Glu||mg/dl||||-99000000000||||00010101000000|\n"
        "P|3||00006|Department3|FamilyName|Name|20020000|MALE|||||||||||||||||||||||||\n"
        "C|3|||\n"
        "O|1|||LDH|False||||||||||Serum|||||||||||||||\n"
        "R|1|LDH||U/l||||-99000000000||||00010101000000|\n"
        "O|2|||LDL|False||||||||||Serum|||||||||||||||\n"
        "R|1|LDL||mg/dl||||-99000000000||||00010101000000|\n"
        "O|4|||C3|False||||||||||Serum|||||||||||||||\n"
        "R|1|C3||mg/dl||||-99000000000||||00010101000000|\n"
        "O|5|||C4|False||||||||||Serum|||||||||||||||\n"
        "R|1|C4||mg/dl||||-99000000000||||00010101000000|\n"
        "O|6|||Hba1C|False||||||||||Serum|||||||||||||||\n"
        "R|1|Hba1C||mmol/mol Hb||||-99000000000||||00010101000000|\n"
        "L||N\n"
    )

    try:
        # Create a socket connection to the TCP listener
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Send the HL7 message
        client_socket.sendall(astm_message.encode('utf-8'))
        print("HL7 message sent successfully.")

    except Exception as e:
        print(f"Error sending HL7 message: {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    send_astm_message()



# Below is a sample ASTM that the equipment expects
    # astm_message = (
    #     "H|\^&|||HS100^V1.0|||||Host||P|1|20160920"
    #         "P|1||00004|Department1|Mustermann|Max|20000101|MALE|||||||||||||||||||||||||"
    #             "C|1|||"
    #             "O|1|||Alb|False||||||||||Serum|||||||||||||||"
    #             "O|2|||Amy|False||||||||||Serum|||||||||||||||"
    #             "O|3|||Bilda|False||||||||||Serum|||||||||||||||"
    #             "O|4|||Bilta|False||||||||||Serum|||||||||||||||"
    #             "O|6|||Chol|False||||||||||Serum|||||||||||||||"
    #         "P|2||00005|Department2|Musterfrau|Minna|20010202|FEMALE|||||||||||||||||||||||||"
    #             "C|2|||"
    #             "O|1|||CK|False||||||||||Serum|||||||||||||||"
    #             "O|2|||CK-MB|False||||||||||Serum|||||||||||||||"
    #             "O|3|||Cl|False||||||||||Serum|||||||||||||||"
    #             "O|4|||CreaA|False||||||||||Serum|||||||||||||||"
    #             "O|6|||Glu|False||||||||||Serum|||||||||||||||"
    #         "P|3||00006|Department3|FamilyName|Name|20020303|MALE|||||||||||||||||||||||||"
    #             "C|3|||"
    #             "O|1|||LDH|False||||||||||Serum|||||||||||||||"
    #             "O|2|||LDL|False||||||||||Serum|||||||||||||||"
    #             "O|4|||C3|False||||||||||Serum|||||||||||||||"
    #             "O|5|||C4|False||||||||||Serum|||||||||||||||"
    #             "O|6|||Hba1C|False||||||||||Serum|||||||||||||||"
    #     "L||N"
    # )