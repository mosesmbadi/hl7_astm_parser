import json

from converters.json_to_astm import convert_json_to_astm
from converters.json_to_hl7 import convert_json_to_hl7

from settings.settings import EQUIPMENT_LIST


EQUIPMENT_LIST = EQUIPMENT_LIST

from coms.send_to_net_dir import send_to_network_folder


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

    if equipment_data_type == 'astm' and equipment_com_mode == 'network_directory':
        json_data = [json_data]
        converted_data = convert_json_to_astm(json_data)
        send_to_network_folder(converted_data)    

    elif equipment_data_type == 'hl7':
        converted_data = convert_json_to_hl7(json_data)
        print(f"Converted JSON to HL7 : \n{converted_data}")

    # Send converted data to the equipment
    send_to_equipment(converted_data, equipment_data_type)


def send_to_equipment(equipment, data):
    # Convert JSON data to ASTM format
    pass