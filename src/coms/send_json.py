import socket
import json

def send_sample_json(host, port, sample_data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Connecting to server at {host}:{port}...")
            client_socket.connect((host, port))
            print("Connected to server.")

            # Convert dictionary to JSON string
            json_data = json.dumps(sample_data)
            print(f"Sending JSON data: {json_data}")

            # Send data
            client_socket.sendall(json_data.encode('utf-8'))

            client_socket.settimeout(1)  # 5-second timeout

            try:
                # Receive response (optional, depending on your server setup)
                response = client_socket.recv(1024)
                if response:
                    print(f"Response from server: {response.decode('utf-8')}")
            except socket.timeout:
                print("No response received from server within 5 seconds.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Server details
    HOST = '127.0.0.1'  # Server host
    PORT = 9091         # Server port

    # Sample JSON data to test
    sample_json = {
        "equipment": "HumaCount 5D",
        "id":3,
        "test_panel_name":"",
        "result":"None",
        "test_panel_id":3,
        "record_id":3,
        "patient_name":"Mustermann",
        "patient_id":"00004",
        "patient_sex":"MALE",
        "sample_type":"",
        "unit_of_measurement":"",
        "date_created":"20160920091032",
        "facility_name":"Sphera^V1.0",
        "patient_birthday":"20000000"
    }

    # Send the JSON data
    send_sample_json(HOST, PORT, sample_json)
