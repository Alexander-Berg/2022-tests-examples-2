import json


_EPS = 1e-5


def compare_geopoints(x, y):
    assert abs(x[0] - y[0]) < _EPS
    assert abs(x[1] - y[1]) < _EPS


async def test_v1_deptrans_cars(
        taxi_driver_regulatory_export, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/deptrans')
    def _mock_candidates(request):
        assert request.method == 'POST'
        data = json.loads(request.get_data())
        assert data == {'deptrans': {'classes_without_permission': []}}
        return load_json('answer.json')

    response = await taxi_driver_regulatory_export.post('/v1/deptrans/cars')
    assert response.status_code == 200
    data = response.json()
    answer = load_json('answer.json')['drivers']
    assert len(data) == len(answer)
    for x, y in zip(data, answer):
        assert x['direction'] == y['direction']
        assert x['free'] == y['free']
        compare_geopoints(x['geopoint'], y['geopoint'])
        assert x['id'] == y['id']
        assert x['speed'] == y['speed']
        assert x['timestamp'] == y['timestamp']


async def test_v1_deptrans_cars_extend(
        taxi_driver_regulatory_export, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/deptrans')
    def _mock_candidates(request):
        assert request.method == 'POST'
        data = json.loads(request.get_data())
        assert data == {
            'format': 'extended',
            'deptrans': {'classes_without_permission': []},
        }
        return load_json('answer_extend.json')

    response = await taxi_driver_regulatory_export.post(
        '/v1/deptrans/cars',
        headers={'Yandex-Api-Key': 'bV04GiLnCx1KOxCp4sUw0VWFjf039yoP'},
    )
    assert response.status_code == 200
    data = response.json()
    answer = load_json('answer_extend.json')['drivers']
    assert len(data) == len(answer)
    for i in range(1, len(data)):
        assert data[i]['car_number'] == answer[i]['car_number']
        assert data[i]['direction'] == answer[i]['direction']
        assert data[i]['free'] == answer[i]['free']
        assert data[i]['geopoint'] == answer[i]['geopoint']
        assert data[i]['id'] == answer[i]['id']
        assert data[i]['model'] == answer[i]['model']
        assert data[i]['parks'] == answer[i]['parks']
        assert data[i]['speed'] == answer[i]['speed']
        assert data[i]['timestamp'] == answer[i]['timestamp']


async def test_v1_deptrans_cars_api_key(
        taxi_driver_regulatory_export, mockserver, load_json,
):
    response = await taxi_driver_regulatory_export.post(
        '/v1/deptrans/cars', headers={'Yandex-Api-Key': 'wrong'},
    )
    assert response.status_code == 401
