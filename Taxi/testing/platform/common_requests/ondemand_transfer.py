import json
import re
import requests
import os


PLATFORM_TRANSFER_URL = 'http://logistic-platform.taxi.tst.yandex.net/api/b2b/external_platform/'

AUTHORIZATION = 'ndd-test-employer'


def get_activation_landing(platform_request_id):
    r = requests.get(
    os.path.join(PLATFORM_TRANSFER_URL, 'activation/landing'),
        headers={
            'Authorization': AUTHORIZATION
        },
        params={
            'request_id' : platform_request_id,
            'is_go_app_installed': 'false',
            'need_redirect':'false'
        }
    )
    r.raise_for_status()
    transfer_url = r.json()['urls'][0]['url']
    transfer_id = transfer_url[transfer_url.rfind('/')+1:]
    return transfer_id


def get_activation_transfer(platform_request_id, transfer_id):
    r = requests.get(
        os.path.join(PLATFORM_TRANSFER_URL, 'transfer/activate'),
        headers={
            'Authorization': AUTHORIZATION
        },
        params={
            'transfer_id': transfer_id,
            'request_id': platform_request_id
        }
    )
    r.raise_for_status()


def get_transfer_info(transfer_id):
    r = requests.get(
        os.path.join(PLATFORM_TRANSFER_URL, 'transfer/info'),
        headers={
            'Authorization': AUTHORIZATION
        },
        params={
            'transfer_id': transfer_id,
        }
    )
    r.raise_for_status()
