import requests


def test_ping():
    url = 'http://driver-eta.taxi.yandex.net/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.status_code == 200
    assert response.content == b''
