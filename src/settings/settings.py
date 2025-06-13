"""
This file contains settings for the Laboratory
i.e The Equipment they have, LIS endpoint and if authentication
is needed, the auth endpoint.

NB: The Equipment name should match what we're getting fom the json
"""

from decouple import config
import ast

# Helper to parse dict-like strings from .env
def parse_equipment(prefix):
    return {
        "id": int(config(f"{prefix}_ID")),
        "ip_address": config(f"{prefix}_IP"),
        "port": int(config(f"{prefix}_PORT")),
        "data_type": config(f"{prefix}_TYPE"),
        "name": config(f"{prefix}_NAME"),
        "com_mode": config(f"{prefix}_COM_MODE"),
    }

EQUIPMENT_1 = parse_equipment("EQUIPMENT_1")
EQUIPMENT_2 = parse_equipment("EQUIPMENT_2")
EQUIPMENT_3 = parse_equipment("EQUIPMENT_3")

EQUIPMENT_LIST = [EQUIPMENT_1, EQUIPMENT_2, EQUIPMENT_3]

BACKEND_USERNAME = config("BACKEND_USERNAME")
BACKEND_PASSWORD = config("BACKEND_PASSWORD")
RESULTS_ENDPOINT = config("RESULTS_ENDPOINT")
AUTH = config("AUTH")

NETWORK_EQUIPMENT_IP = config("NETWORK_EQUIPMENT_IP", default=None)
NETWORK_INPUT_WORKLIST_FILE = config("NETWORK_INPUT_WORKLIST_FILE", default=None)
NETWORK_USER_PASSWORD = config("NETWORK_USER_PASSWORD", default=None)
NETWORK_USERNAME = config("NETWORK_USERNAME", default=None)