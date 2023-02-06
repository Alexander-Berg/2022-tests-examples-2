# pylint: skip-file
# flake8: noqa
import argparse

import requests

from helpers.data_generation import *
from helpers.web import *


def send_event(device_id):
    query_args = {
        'device_id': device_id,
        'timestamp': generate_timestamp_now(),
    }
    url = SIGNAL_SERVICE_URL + SIGNAL_EVENT_HANDLER
    payload = generate_event_payload(None, None)
    headers = signal_events_headers(payload, query_args)
    response = requests.request(
        HTTP_POST, url, params=query_args, headers=headers, json=payload,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending event: {response.text}',
        )
    print('sent event')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('public_device_id', type=str, help='public_device_id')
    args = parser.parse_args()

    send_event(args.public_device_id)


if __name__ == '__main__':
    main()
