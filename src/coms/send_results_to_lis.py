import logging
import requests

from settings.settings import (
    RESULTS_ENDPOINT, SAMPLE_PANELS_ENDPOINT, TEST_CODE_MAP,
    BACKEND_USERNAME, BACKEND_PASSWORD, AUTH
)

logger = logging.getLogger(__name__)


def get_access_token():
    auth = requests.post(
        AUTH,
        data={'email': BACKEND_USERNAME, 'password': BACKEND_PASSWORD}
    )
    if auth.status_code != 200:
        logger.error(f"Failed to obtain access tokens. Status code: {auth.status_code}. Response: {auth.text}")
        return None

    access_token = auth.json().get('access')
    if not access_token:
        logger.error("Access token not found in response")
    return access_token


def panel_name_for(test_code):
    """The backend panel name an analyzer test code maps to."""
    return TEST_CODE_MAP.get(test_code, test_code).strip().lower()


def send_to_lab_endpoints(data_list, format_type):
    """
    For each sample in data_list, fetches its panels from the backend, matches
    each result to a panel by test name, and PATCHes the result onto that panel.
    """
    if not data_list:
        logger.info(f"No {format_type} results to send")
        return

    access_token = get_access_token()
    if not access_token:
        return

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    results_by_sample = {}
    for item in data_list:
        results_by_sample.setdefault(item['sample_id'], []).append(item)

    for sample_id, results in results_by_sample.items():
        if not sample_id:
            logger.warning(f"{len(results)} {format_type} results have no sample ID, skipping")
            continue

        response = requests.get(f"{SAMPLE_PANELS_ENDPOINT}{sample_id}/", headers=headers)
        if response.status_code != 200:
            logger.warning(f"No panels found for sample {sample_id}. Status code: {response.status_code}")
            continue

        panels = {
            (panel.get('test_panel_name') or '').strip().lower(): panel
            for panel in response.json()
        }

        for item in results:
            panel = panels.get(panel_name_for(item['test_code']))
            if not panel:
                logger.info(f"Sample {sample_id}: no panel for test {item['test_code']}, skipping")
                continue
            if panel.get('result_approved'):
                logger.info(f"Sample {sample_id}: {item['test_code']} already approved, not overwriting")
                continue

            endpoint = f"{RESULTS_ENDPOINT}{panel['id']}/"
            response = requests.patch(endpoint, headers=headers, json={'result': item['result']})

            if response.status_code == 200:
                logger.info(f"Sample {sample_id}: {item['test_code']}={item['result']} sent to {endpoint}")
            else:
                logger.error(f"Failed to send data to {endpoint}. Status code: {response.status_code}. Response: {response.text}")
