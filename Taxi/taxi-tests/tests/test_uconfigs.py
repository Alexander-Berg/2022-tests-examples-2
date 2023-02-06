import json

import requests

BASE_URL = 'http://uconfigs.taxi.yandex.net'


def test_ping():
    url = f'{BASE_URL}/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.status_code == 200
    assert response.content == b''


def test_get_configs_info():
    url = f'{BASE_URL}/configs/values'
    response = requests.post(
        url, data=json.dumps({'ids': ['LOOKUP_IS_CARGO_MISC_ENABLED']}),
    )
    response.raise_for_status()
    assert response.status_code == 200
    response_body = response.json()
    assert 'configs' in response_body and response_body['configs'] == {
        'LOOKUP_IS_CARGO_MISC_ENABLED': True,
    }
