import json

import requests


def test_ping():
    url = 'http://taxi-api-admin.taxi.yandex.net/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == b''


def test_services_info():
    url = 'http://taxi-api-admin.taxi.yandex.net/services_info'
    response = requests.get(url, headers={'X-YaTaxi-Api-Key': 'admin_token'})
    response.raise_for_status()
    services_info = json.loads(response.content)
    assert services_info.get('api_admin_errors', '') == ''
    expected_services = []
    for service in services_info['services']:
        expected_services.append({
            'service_name': service['service_name'],
            'is_valid': True,
            'errors': [],
        })
    assert services_info['services'] == expected_services
