import signal
import socket
from converters.hl7_to_json import convert_hl7_to_json
from coms.send_results import send_to_lab_endpoints

''''
Will listen for incoming data, convert to hl7 then send to backend
Purpose: Will run alongside main system, picks incoming lab results 
from equipments, converts to json then sends to results endpoint
'''

import json
import re


def main():
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

                    decoded_data = received_data.decode('utf-8')
                    print(f"Received data: {decoded_data}")

                    if decoded_data.startswith('MSH'):
                        convert_hl7_to_json(decoded_data)
                        converted_data = convert_hl7_to_json(decoded_data)
                        print(f'Converted json is: {converted_data}')

                        send_to_lab_endpoints(decoded_data, 'hl7')
                        sent_data = send_to_lab_endpoints(decoded_data, 'hl7')
                        print(f'Sent data is: {sent_data}')



                    elif decoded_data.startswith('H|^&'):
                        astm_message_dict = astm_to_json(decoded_data)
                        send_to_lab_endpoints(astm_message_dict, 'astm')

                finally:
                    connection.close()

            except Exception as e:
                print(f"Exception while accepting incoming connection: {e}")


def astm_to_json(astm_data):
    pass


def signal_handler(signal, frame):
    print("Terminating process...")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()


