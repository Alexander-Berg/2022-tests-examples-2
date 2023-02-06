import pytest


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result',
    [('ll=37.589569560,55.733434780', 'expected_response.json')],
)
async def test_available_zone(
        taxi_price_estimate_api,
        request_params,
        expected_result,
        load_json,
        uapi_keys_auth,
):
    response = await taxi_price_estimate_api.get(
        'zone_info?clid=test3&apikey=qwerty3&' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(expected_result)
    assert uapi_keys_auth.has_calls


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result', [('ll=34,44', {'tariffs': []})],
)
async def test_bad_zone(
        taxi_price_estimate_api,
        request_params,
        expected_result,
        uapi_keys_auth,
):
    response = await taxi_price_estimate_api.post(
        'zone_info?clid=test3&apikey=qwerty3&' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result
    assert uapi_keys_auth.has_calls
