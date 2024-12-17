import signal
import socket
import json
import re
from coms.send_to_equipment import process_json_data
from converters.astm_to_json import convert_astm_to_json
from converters.hl7_to_json import convert_hl7_to_json
from coms.send_results_to_lis import send_to_lab_endpoints



def main():
    ''''
    Will listen for incoming data, convert to hl7 then send to backend
    Purpose: Will run alongside main system, picks incoming lab results 
    from equipments, converts to json then sends to results endpoint
    '''
    host = '127.0.0.1' 
    port = 9091
    

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Listening for incoming connections on {host}:{port}...")

        while True:
            try:
                connection, address = server_socket.accept()
                print(f"Connection established from: {address}")

                try:
                    received_data = b''
                    while True:
                        data = connection.recv(1024)
                        received_data += data

                        if not data:
                            break

                    print(f"Received data from {address}: {received_data}")

                    decoded_data = received_data.decode('utf-8')
                    if decoded_data:
                        print("Data Received")

                    # Check if incoming data is HL7
                    if decoded_data.startswith('MSH'):
                        convert_hl7_to_json(decoded_data)
                        converted_data = convert_hl7_to_json(decoded_data)
                        print(f'Converted hl7 to json is: {converted_data}')

                        for test_result in converted_data:
                            send_to_lab_endpoints(converted_data, 'hl7')

                    # Check if incoming data is ASTM
                    elif decoded_data.startswith('H|'):
                        astm_message_dict = convert_astm_to_json(decoded_data)
                        print(f'Converted astm to json is: {astm_message_dict}')
                        send_to_lab_endpoints(astm_message_dict, 'astm')


                    # Check if incoming data is JSON
                        
                    elif decoded_data.startswith('{'):
                        print("Checking if incoming data is JSON...")
                        try:
                            json_data = json.loads(decoded_data)
                            print("Processing incoming JSON data...")
                            process_json_data(json_data)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON data: {e}")

                finally:
                    connection.close()

            except Exception as e:
                print(f"Exception while accepting incoming connection: {e}")


def signal_handler(signal, frame):
    print("Terminating process...")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()


