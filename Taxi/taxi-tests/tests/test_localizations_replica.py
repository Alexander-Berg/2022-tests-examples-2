import requests


def test_ping():
    url = 'http://localizations-replica.taxi.yandex.net/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == b''


def test_keyset():
    url = 'http://localizations-replica.taxi.yandex.net/v1/keyset'
    params = {'name': 'client_messages'}
    response = requests.get(url, params=params)
    response.raise_for_status()
    assert response.json()['keys']
