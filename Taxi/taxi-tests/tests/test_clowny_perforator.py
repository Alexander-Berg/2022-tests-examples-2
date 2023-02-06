import requests


CLOWNY_PERFORATOR_HOST = 'http://clowny-perforator.taxi.yandex.net'


def test_ping():
    url = f'{CLOWNY_PERFORATOR_HOST}/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == b''
