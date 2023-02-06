# pylint: skip-file
# flake8: noqa
import argparse
import json

import requests

from helpers.data_generation import *
from helpers.web import *
from helpers.jwt_generation import *

SIGNAL_CONFIGS_HANDLER = '/v1/config'


def make_headers(body):
    return {
        'Content-Type': 'application/json',
        'X-JWT-Signature': generate_jwt(SIGNAL_CONFIGS_HANDLER, {}, body),
    }


def get_config(device_id):
    body = {
        'device_id': device_id,
        'timestamp': generate_timestamp_now(),
        'serial_number': 'AAAAA',
        'software_version': '1.1.2-3',
    }
    headers = make_headers(body)
    print(
        f'curl -X{HTTP_POST} {SIGNAL_SERVICE_URL + SIGNAL_CONFIGS_HANDLER} -d \'{json.dumps(body)}\' '
        + ' '.join([f'-H \'{k}: {v}\'' for k, v in headers.items()]),
    )
    response = requests.request(
        HTTP_POST,
        SIGNAL_SERVICE_URL + SIGNAL_CONFIGS_HANDLER,
        headers=headers,
        json=body,
    )
    if response.status_code != HTTP_CODE_SUCCESS:
        raise RuntimeError(f'got {response.status_code}, {response.text}')
    print('response: ', response.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('public_device_id', type=str, help='public_device_id')
    args = parser.parse_args()

    get_config(args.public_device_id)


if __name__ == '__main__':
    main()
