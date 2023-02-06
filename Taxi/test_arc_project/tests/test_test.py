import json
import os
from typing import Optional
from typing import Dict
import urllib.parse
import warnings

import pytest
import requests


API_TIMEOUT = 5.0
STATISTICS_URL = os.getenv(
    'API_COVERAGE_STATISTICS_URL',
    'http://eats-automation-statistics.eda.tst.yandex.net',
)
IS_ARCADIA_CI = os.getenv('IS_ARCADIA_CI')


def get_api_coverage_ratio(service_name: Optional[str] = None) -> Dict:
    params = None
    if service_name:
        params = {'service_name': service_name}
    response = _make_request(
        method='GET', url='/api/v1/coverage', params=params,
    )
    try:
        _json = response.json()
        return _json
    except json.JSONDecodeError as exc:
        raise exc


def _make_request(
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
) -> requests.Response:
    full_url = urllib.parse.urljoin(STATISTICS_URL, url)
    response = requests.request(
        method=method,
        url=full_url,
        params=params,
        json=json_data,
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()
    return response


@pytest.fixture(scope='session', autouse=True)
def finalizer():
    yield


def test_1():
    assert 2+2 == 4


def test_2(metrics):
    metrics.set('my_unique_metric', 3.14)
    metrics.set('coverage-ratio', 0.99)
    warnings.warn(f'IS_ARCADIA_CI={IS_ARCADIA_CI}')
    assert 2*2 == 4
    response = get_api_coverage_ratio()
    assert response != {}
    warnings.warn(str(response))
