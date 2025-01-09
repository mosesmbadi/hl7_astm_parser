
"""
This file contains settings for the Laboratory
i.e The Equipment they have, LIS endpoint and if authentication
is needed, the auth endpoint.
"""

EQUIPMENT_1 = {
    "id": 1,
    "ip_address": "127.0.0.1",
    "port": 9091,
    "data_type": "hl7",
    "name": "HumaCount 5D",
    "com_mode": "tcp"
}

EQUIPMENT_2 = {
    "id": 2,
    "ip_address": "127.0.0.1",
    "port": 9092,
    "data_type": "astm",
    "name": "HumaStar 100",
    "com_mode": "shared_directory"
}

EQUIPMENT_3 = { 
    "id": 3,
    "ip_address": "127.0.0.1",
    "port": 9093,
    "data_type": "astm",
    "name": "Maglumi 800",
    "com_mode": "serial"  
}

EQUIPMENT_LIST = [EQUIPMENT_1, EQUIPMENT_2, EQUIPMENT_3]

BACKEND_USERNAME= "admin@mail.com"
BACKEND_PASSWORD = "admin"

RESULTS_ENDPOINT = "http://127.0.0.1:8080/lab/lab-test-requests-panel/"
AUTH = "http://127.0.0.1:8080/customuser/login/"