import socket

def send_hl7_message(host='127.0.0.1', port=9091):
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

    except Exception as e:
        print(f"Error sending HL7 message: {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    send_hl7_message()
