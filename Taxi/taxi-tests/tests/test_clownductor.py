import requests


CLOWNDUCTOR_HOST = 'http://clownductor.taxi.yandex.net'


def test_ping():
    url = f'{CLOWNDUCTOR_HOST}/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == b''
