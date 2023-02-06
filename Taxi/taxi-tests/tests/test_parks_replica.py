import requests


def test_ping():
    url = 'http://parks-replica.taxi.yandex.net/ping'
    response = requests.get(url)
    response.raise_for_status()
    assert response.content == b''


def test_parks():
    url = 'http://parks-replica.taxi.yandex.net/v1/parks/retrieve'
    park_ids = [
        '999011',
        '999012',
        '999013',
        '111666',
        '100504',
        '111500',
        '111501',
        '111502',
        '111503',
    ]
    body = {'id_in_set': park_ids}
    response = requests.post(url, json=body)
    response.raise_for_status()
    park_ids = set(park_ids)
    response_json = response.json()
    response_parks = {
        park['park_id'] for park in response_json['parks']
    }
    assert park_ids == response_parks
