from converters.json_to_astm import convert_json_to_astm
from converters.json_to_hl7 import convert_json_to_hl7

from settings.settings import EQUIPMENT_LIST


EQUIPMENT_LIST = EQUIPMENT_LIST


def find_equipment_by_name(name):
    """Find equipment by name in the equipment list."""
    for equipment in EQUIPMENT_LIST:
        if equipment.get('id') == name or equipment.get('ip_address') == name:
            return equipment
    return None


def process_json_data(json_data):
    """Process JSON data based on equipment type."""
    equipment_name = json_data.get('equipment')
    if not equipment_name:
        print("Error: Equipment field is missing in the incoming JSON data.")
        return

    equipment = find_equipment_by_name(equipment_name)
    if not equipment:
        print(f"Error: Equipment '{equipment_name}' not found in the equipment list.")
        return

    data_type = equipment.get('data_type')
    print(f"Processing data for equipment: {equipment_name} with data type: {data_type}")

    # Convert to JSON based on data type of the equipment
    if data_type == 'astm':
        json_data = [json_data]
        converted_data = convert_json_to_astm(json_data)
        print(f"Converted JSON to ASTM: {converted_data}")

    elif data_type == 'hl7':
        converted_data = convert_json_to_hl7(json_data)
        print(f"Converted JSON to HL7: {converted_data}")

    else:
        print(f"Error: Unsupported data type '{data_type}' for equipment {equipment_name}.")
        return

    # Send converted data to the equipment
    send_to_equipment(converted_data, data_type)


def send_to_equipment(equipment, data):
    # Convert JSON data to ASTM format
    pass