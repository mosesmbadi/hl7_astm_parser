import requests
from decouple import config

from settings.settings import RESULTS_ENDPOINT, BACKEND_USERNAME, BACKEND_PASSWORD, AUTH

def send_to_lab_endpoints(data_list, format_type):
    # Endpoint base URL
    base_url = RESULTS_ENDPOINT

    # Get email and password from environment variables
    email = BACKEND_USERNAME
    password = BACKEND_PASSWORD

    # Authenticate and obtain tokens
    auth = requests.post(
        AUTH, 
        data={'email': email, 'password': password}
    )

    if auth.status_code == 200:
        access_token = auth.json().get('access')
        
        if not access_token:
            print("Access token not found in response")
            return
        
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

        # Iterate over each item in the list and send it individually
        for item in data_list:
            # Construct the endpoint using the item's `id`
            endpoint = f"{base_url}{item['id']}/"
            response = requests.put(endpoint, headers=headers, json=item)

            # Log success or failure
            if response.status_code == 200:
                print(f"Data sent successfully to {endpoint}")
            else:
                print(f"Failed to send data to {endpoint}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
    else:
        print(f"Failed to obtain access tokens. Status code: {auth.status_code}")
        print(f"Response: {auth.text}")
