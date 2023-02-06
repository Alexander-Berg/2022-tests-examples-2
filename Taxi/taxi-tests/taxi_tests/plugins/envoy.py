from typing import Dict
from typing import List

import pytest
import requests


ALPHA_URL = 'http://envoy-exp-alpha.taxi.yandex.net'


@pytest.fixture
def envoy_v2_visit():
    def wrapper(dest: List[str]) -> Dict:
        resp = requests.post(f'{ALPHA_URL}/v2/visit', json={'dest': dest})

        assert resp.status_code == 200, resp
        assert 'X-Taxi-EnvoyProxy-DstVhost' not in resp.headers

        json = resp.json()

        assert 'info' in json
        info = json.pop('info')

        assert not json

        return info

    return wrapper
