import json

ENDPOINT_URL = '/cars/brands/list'

OK_REQUEST = {'query': {'park': {'id': '228'}}}

OK_RESPONSE = {
    'brands': sorted(
        [
            {'name': 'Pagani'},
            {'name': 'Таврия'},
            {'name': 'BMW'},
            {'name': 'Daewoo'},
            {'name': 'Dadi'},
            {'name': 'Acura'},
            {'name': 'ЗАЗ'},
            {'name': 'LADA (ВАЗ)'},
            {'name': 'Mercedes-Benz'},
            {'name': 'Audi'},
        ],
        key=lambda i: i['name'],
    ),
}


def test_ok(taxi_parks):
    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(OK_REQUEST))

    assert response.status_code == 200
    assert response.json() == OK_RESPONSE
