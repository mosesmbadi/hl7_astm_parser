import signal
import socket
import json
import logging
from coms.send_to_equipment import process_json_data
from converters.astm_to_json import convert_astm_to_json
from converters.hl7_to_json import convert_hl7_to_json
from coms.send_results_to_lis import send_to_lab_endpoints


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def send_response(connection, message):
    """Sends a response message back to the client."""
    try:
        connection.sendall(message.encode('utf-8'))
    except Exception as e:
        print(f"Error sending response: {e}")
        

def process_full_data(decoded_data, connection, address):
    """Process the full data from a source and send the appropriate response."""
    try:
        # Send acknowledgment for the complete data from the source
        send_response(connection, f"Data received: {decoded_data}")
        logger.info(f"Acknowledgment sent to {address}: {decoded_data}")

        # Check if incoming data is HL7
        if decoded_data.startswith('MSH'):
            logger.debug("Detected HL7 data.")
            try:
                converted_data = convert_hl7_to_json(decoded_data)
                logger.info(f"Converted HL7 to JSON: {converted_data}")

                for test_result in converted_data:
                    send_to_lab_endpoints(test_result, 'hl7')
            except Exception as e:
                logger.error(f"Error processing HL7 data: {e}", exc_info=True)

        elif '{' in decoded_data:
            logger.debug("Detected JSON data.")
            try:
                # Remove any non-JSON data before the JSON object
                json_start = decoded_data.find('{')
                if json_start != -1:
                    json_part = decoded_data[json_start:]
                else:
                    json_part = decoded_data

                # Split the JSON part into individual JSON objects
                json_objects = []
                while '{' in json_part:
                    json_end = json_part.find('}') + 1
                    json_object = json_part[:json_end]
                    json_objects.append(json_object)
                    json_part = json_part[json_end:]

                # Attempt to load each JSON object
                for json_object in json_objects:
                    try:
                        json_data = json.loads(json_object, strict=False)
                        logger.info(f"Processing JSON data: {json_data}")
                        process_json_data(json_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error decoding JSON data: {e}")

            except json.JSONDecodeError as e:
                logger.warning(f"Error decoding JSON data: {e}")

            except json.JSONDecodeError as e:
                logger.warning(f"Error decoding JSON data: {e}")

    except Exception as e:
        logger.error(f"Unexpected error processing JSON data: {e}", exc_info=True)


def main():
    ''''
    Will listen for incoming data, convert to HL7 then send to backend.
    Purpose: Picks incoming lab results from equipment, converts to JSON then sends to results endpoint.
    '''
    host = '192.168.100.56' 
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

                    # Process the complete data (from the same source)
                    process_full_data(decoded_data, connection, address)

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