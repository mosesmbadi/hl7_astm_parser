
"""
This file contains settings for the Laboratory
i.e The Equipment they have, LIS endpoint and if authentication
is needed, the auth endpoint.

Everything is read from the environment (or a .env file); see .env in the
repo root for the full list.
"""
from decouple import config


def load_equipment_list():
    """Reads EQUIPMENT_1_*, EQUIPMENT_2_*, ... until a number has no NAME."""
    equipment_list = []
    n = 1
    while config(f"EQUIPMENT_{n}_NAME", default=""):
        equipment_list.append({
            "id": config(f"EQUIPMENT_{n}_ID", default=n, cast=int),
            "ip_address": config(f"EQUIPMENT_{n}_IP", default=""),
            "port": config(f"EQUIPMENT_{n}_PORT", default=0, cast=int),
            "data_type": config(f"EQUIPMENT_{n}_TYPE", default="hl7"),
            "name": config(f"EQUIPMENT_{n}_NAME"),
            "com_mode": config(f"EQUIPMENT_{n}_COM_MODE", default="tcp"),
        })
        n += 1
    return equipment_list


def load_test_code_map():
    """'CREA=Creatinine,UREA=Urea' -> {'CREA': 'Creatinine', 'UREA': 'Urea'}"""
    pairs = config("TEST_CODE_MAP", default="")
    return dict(
        (code.strip(), name.strip())
        for code, _, name in (pair.partition("=") for pair in pairs.split(",") if "=" in pair)
    )


EQUIPMENT_LIST = load_equipment_list()

BACKEND_USERNAME = config("BACKEND_USERNAME", default="admin@mail.com")
BACKEND_PASSWORD = config("BACKEND_PASSWORD", default="admin")

BACKEND_URL = config("BACKEND_URL", default="http://127.0.0.1:8080").rstrip("/")

RESULTS_ENDPOINT = f"{BACKEND_URL}/lab/lab-test-requests-panel/"
# Panels for a sample, looked up by the sample code the analyzer sends back
SAMPLE_PANELS_ENDPOINT = f"{BACKEND_URL}/lab/labtestrequestpanels/sample/"
AUTH = f"{BACKEND_URL}/users/login/"

# Analyzer test code -> backend test panel name, for codes that differ.
# Codes not listed here are matched to the panel name as-is (case-insensitive).
TEST_CODE_MAP = load_test_code_map()
