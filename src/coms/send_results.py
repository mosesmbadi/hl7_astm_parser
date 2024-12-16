import requests
from decouple import config

def send_to_lab_endpoints(data, format):
    endpoints = {
        'lab_test_results': 'http://127.0.0.1:8080/lab/lab-test-results/',
        'lab_test_results_panel': 'http://127.0.0.1:8080/lab/lab-test-requests-panel/'
    }

    email = config('BACKEND_USERNAME')
    password = config('BACKEND_PASSWORD')

    auth = requests.post('http://127.0.0.1:8080/customuser/login/', data={'email': email, 'password': password})

    if auth.status_code == 200:
        access_token = auth.json()['access']
        refresh_token = auth.json()['refresh']

        for endpoint in endpoints.values():
            response = requests.post(
                endpoint,
                headers={'Authorization': f'Bearer {access_token}'},
                json=data
            )

            if response.status_code == 200:
                print(f"Data sent successfully to {endpoint}")
            else:
                print(f"Failed to send data to {endpoint}. Status code: {response.status_code}")
    else:
        print(f"Failed to obtain access tokens. Status code: {auth.status_code}")
