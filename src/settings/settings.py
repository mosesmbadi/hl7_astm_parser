"""
This file contains settings for the Laboratory
i.e The Equipment they have, LIS endpoint and if authentication
is needed, the auth endpoint.

Everything is read from the environment (or a .env file); see .env in the
repo root for the full list.

Which test panel an analyzer code belongs to is not configured here: it is
set per analyzer in EasyMed (Lab Settings -> Lab Equipments -> Test mappings).
"""
from decouple import config


def load_equipment_list():
    """
    Reads EQUIPMENT_1_*, EQUIPMENT_2_*, ... until a number has no NAME.
    Only used to send worklists to analyzers; receiving results needs none.
    """
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


EQUIPMENT_LIST = load_equipment_list()

BACKEND_USERNAME = config("BACKEND_USERNAME", default="admin@mail.com")
BACKEND_PASSWORD = config("BACKEND_PASSWORD", default="admin")

# Required, with no default: falling back to 127.0.0.1 inside a container
# silently sends every result to the container itself. In the EasyMed compose
# stack this is http://api:8080.
BACKEND_URL = config("BACKEND_URL").rstrip("/")

AUTH = f"{BACKEND_URL}/users/login/"
ANALYZER_MESSAGES_ENDPOINT = f"{BACKEND_URL}/lab/analyzer-messages/"

REQUEST_TIMEOUT = config("REQUEST_TIMEOUT", default=15, cast=int)

# Results EasyMed could not take yet wait here and are retried. Mount it as a
# volume so they survive the container being recreated.
SPOOL_DIR = config("SPOOL_DIR", default="/app/spool")
SPOOL_RETRY_SECONDS = config("SPOOL_RETRY_SECONDS", default=60, cast=int)
