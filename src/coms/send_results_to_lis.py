"""
Delivers analyzer results to EasyMed.

Each run (one sample's results) is posted as it came from the analyzer to
/lab/analyzer-messages/. EasyMed works out which analyzer it is, which test
each code is, and which patient the sample belongs to; whatever it cannot
place waits in its Analyzer Inbox. So once EasyMed has answered 201 the
results are safe, matched or not.

When EasyMed cannot be reached the run is written to SPOOL_DIR and retried in
the background, so results survive a backend restart or outage -- the
analyzer has already been told they were received.
"""
import json
import logging
import os
import threading
import time
import uuid
from collections import Counter

import requests

from settings.settings import (
    ANALYZER_MESSAGES_ENDPOINT, AUTH, BACKEND_PASSWORD, BACKEND_USERNAME, REQUEST_TIMEOUT,
    SPOOL_DIR, SPOOL_RETRY_SECONDS,
)

logger = logging.getLogger(__name__)

_token = None
_token_lock = threading.Lock()
_spool_lock = threading.Lock()


class DeliveryError(Exception):
    """EasyMed did not store the message; it should be retried."""


# ------------------------------------------------------------------ auth

def get_access_token(refresh=False):
    """A cached access token, fetched again when missing or rejected."""
    global _token
    with _token_lock:
        if _token and not refresh:
            return _token
        try:
            response = requests.post(
                AUTH, data={'email': BACKEND_USERNAME, 'password': BACKEND_PASSWORD},
                timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            raise DeliveryError(f"EasyMed unreachable at {AUTH}: {exc}") from exc
        if response.status_code != 200:
            # Wrong credentials won't fix themselves by retrying, but spooling
            # keeps the results until someone corrects BACKEND_USERNAME/PASSWORD.
            raise DeliveryError(f"Login refused ({response.status_code}): {response.text[:200]}")
        _token = response.json().get('access')
        if not _token:
            raise DeliveryError("Login response had no access token")
        return _token


# -------------------------------------------------------------- delivery

def payload_for(run, raw_message):
    return {
        'sender': run.get('sender', ''),
        'sample_code': run.get('sample_id', ''),
        'patient_name': run.get('patient_name', ''),
        'raw_message': raw_message,
        'results': run['results'],
    }


def post_message(payload):
    """Posts one run; raises DeliveryError unless EasyMed stored it."""
    for attempt in (1, 2):
        headers = {'Authorization': f'Bearer {get_access_token(refresh=attempt == 2)}'}
        try:
            response = requests.post(
                ANALYZER_MESSAGES_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            raise DeliveryError(f"EasyMed unreachable: {exc}") from exc
        if response.status_code == 401 and attempt == 1:
            continue  # token expired; log in again once
        if response.status_code == 201:
            return response.json()
        raise DeliveryError(f"EasyMed answered {response.status_code}: {response.text[:300]}")


def log_outcome(stored):
    """One line per run, without patient details; problems listed by code."""
    counts = Counter(result['status'] for result in stored.get('results', []))
    analyzer = stored.get('equipment_name') or f"unrecognised analyzer '{stored.get('sender', '')}'"
    sample = stored.get('sample_code') or 'no sample code'
    summary = ', '.join(f"{count} {status}" for status, count in sorted(counts.items()))
    logger.info(f"EasyMed stored message {stored.get('id')} from {analyzer}, sample {sample}: {summary}")
    for result in stored.get('results', []):
        if result['status'] not in ('posted', 'ignored'):
            logger.warning(f"  {result['analyzer_code']}: {result['status']} - {result['detail']}")


def send_to_lab_endpoints(runs, raw_message, format_type):
    """
    Delivers every run of a message. Runs EasyMed cannot take right now are
    spooled for retry, so this never loses results; it returns False when
    anything had to be spooled.
    """
    if not runs:
        logger.info(f"No {format_type} results to send")
        return True

    delivered_all = True
    for run in runs:
        payload = payload_for(run, raw_message)
        try:
            log_outcome(post_message(payload))
        except DeliveryError as exc:
            delivered_all = False
            path = spool(payload)
            logger.error(f"Could not deliver {len(run['results'])} {format_type} results "
                         f"(sample {run.get('sample_id') or 'none'}): {exc}. Saved to {path} for retry.")
    return delivered_all


# ----------------------------------------------------------------- spool

def spool(payload):
    os.makedirs(SPOOL_DIR, exist_ok=True)
    name = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.json"
    path = os.path.join(SPOOL_DIR, name)
    with open(f"{path}.tmp", 'w', encoding='utf-8') as handle:
        json.dump(payload, handle)
    os.replace(f"{path}.tmp", path)  # never leave a half-written file to retry
    return path


def flush_spool():
    """Delivers spooled runs, oldest first; stops at the first failure."""
    if not os.path.isdir(SPOOL_DIR):
        return
    with _spool_lock:
        for name in sorted(n for n in os.listdir(SPOOL_DIR) if n.endswith('.json')):
            path = os.path.join(SPOOL_DIR, name)
            try:
                with open(path, encoding='utf-8') as handle:
                    payload = json.load(handle)
            except (OSError, ValueError) as exc:
                logger.error(f"Unreadable spool file {path}: {exc}; moving it aside")
                os.replace(path, f"{path}.bad")
                continue
            try:
                stored = post_message(payload)
            except DeliveryError as exc:
                logger.warning(f"Spool retry failed ({exc}); {name} and later files wait")
                return
            log_outcome(stored)
            os.remove(path)
            logger.info(f"Delivered spooled {name}")


def start_spool_worker():
    """Retries spooled runs in the background for as long as the server runs."""
    def worker():
        while True:
            try:
                flush_spool()
            except Exception:
                logger.exception("Spool worker error")
            time.sleep(SPOOL_RETRY_SECONDS)

    threading.Thread(target=worker, name='spool-retry', daemon=True).start()
