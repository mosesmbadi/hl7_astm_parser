import json

from converters.json_to_astm import convert_json_to_astm
from converters.json_to_hl7 import convert_json_to_hl7

from settings.settings import EQUIPMENT_LIST

# TODO: i don't know why I wrote this, but it's ugky. To be fixed.
EQUIPMENT_LIST = EQUIPMENT_LIST


# Get's JSON from incoming data, processes it then sends to the equipment in the json
# this return equipment object
def find_equipment_by_name(name):
    """Find equipment by name in the equipment list."""
    for equipment in EQUIPMENT_LIST:
        if equipment["name"] == name:
            return equipment
    return None


def process_json_data(json_data):
    """Process JSON data based on equipment type."""
    equipment_name = json_data['equipment']
    print(f'JSON Equipment name is: {equipment_name}')

    if not equipment_name:
        print("Error: Equipment field is missing in the incoming JSON data.")
        return

    equipment = find_equipment_by_name(equipment_name)
    if not equipment:
        print(f"Error: Equipment '{equipment_name}' not found in the equipment list.")
        return
    
    equipment_data_type = equipment["data_type"] if equipment else None
    equipment_com_mode = equipment["com_mode"] if equipment else None

    # Convert to JSON based on data type of the equipment
    if equipment_data_type == 'astm':
        json_data = [json_data]
        converted_data = convert_json_to_astm(json_data)
        print(f"Converted JSON to ASTM : \n{converted_data}")


    elif equipment_data_type == 'hl7':
        converted_data = convert_json_to_hl7(json_data)
        print(f"Converted JSON to HL7 : \n{converted_data}")

    

    else:
        print(f"Error: Unsupported data type '{equipment_data_type}' for equipment {equipment_name}.")
        return

    # Send converted data to the equipment
    send_to_equipment.last_equipment = equipment
    send_to_equipment(converted_data, equipment_data_type)


def send_to_equipment(converted_data, equipment_data_type):
    """
    Send the converted data (ASTM or HL7) to the equipment's IP and port via TCP.
    """
    import socket

    if not hasattr(send_to_equipment, 'last_equipment') or send_to_equipment.last_equipment is None:
        print("Error: Equipment details not provided to send_to_equipment.")
        return
    equipment = send_to_equipment.last_equipment
    ip = equipment.get("ip_address")
    port = equipment.get("port")
    if not ip or not port:
        print(f"Error: Equipment IP or port missing for {equipment.get('name')}")
        return
    try:
        with socket.create_connection((ip, port), timeout=10) as sock:
            if isinstance(converted_data, list):
                # ASTM conversion may return a list of messages
                for msg in converted_data:
                    sock.sendall(msg.encode('utf-8'))
            else:
                sock.sendall(converted_data.encode('utf-8'))
            print(f"Sent {equipment_data_type} data to {equipment.get('name')} at {ip}:{port}")
    except Exception as e:
        print(f"Error sending data to equipment {equipment.get('name')} at {ip}:{port}: {e}")