import pytest


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.parametrize(
    'point, expected',
    [pytest.param([32.151, 51.121], 1.0), pytest.param([29.151, 51.121], 2.0)],
)
async def test_get_surge(taxi_surge_calculator, mockserver, point, expected):
    @mockserver.json_handler('/pin-storage/v1/graph-map/get-value')
    def _handle_request(request):
        params = dict(request.query)

        lon = float(params['point'].split(',')[0])
        if lon < 30.0:
            response = {'values': {'econom': 2.0}}
        else:
            response = {'values': {'econom': 1.0}}

        return mockserver.make_response(json=response)

    request = {'point_a': point}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.json()
    data = response.json()
    actual = data['classes'][0]
    assert actual['value_raw'] == expected
    assert actual['surge']['value'] == expected
