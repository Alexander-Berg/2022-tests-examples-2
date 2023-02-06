# pylint: skip-file
# flake8: noqa
import argparse

import requests

from helpers.data_generation import *
from helpers.web import *


def send_status(device_id):
    body = generate_status_payload(device_id)
    headers = signal_status_headers(body)
    response = requests.request(
        HTTP_POST,
        SIGNAL_SERVICE_URL + SIGNAL_STATUS_HANDLER,
        headers=headers,
        json=body,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(
            f'status code {response.status_code} for sending status: {response.text}',
        )
    print('sent status')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('public_device_id', type=str, help='public_device_id')
    args = parser.parse_args()

    send_status(args.public_device_id)


if __name__ == '__main__':
    main()
