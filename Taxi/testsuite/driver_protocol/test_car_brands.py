import pytest


DAEWOO = {'id': 'DAEWOO', 'text': 'Daewoo'}

VAZ = {'id': 'VAZ', 'text': 'LADA (ВАЗ)'}

BMW = {'id': 'BMW', 'text': 'BMW'}

ZAZ = {'id': 'ZAZ', 'text': 'ЗАЗ'}

DADI = {'id': 'DADI', 'text': 'Dadi'}


@pytest.mark.config(CAR_CACHE_BRANDS_UPDATE_ENABLED=True)
@pytest.mark.parametrize(
    'prefix_filter,expected_brands',
    [
        ('', [BMW, DADI, DAEWOO, VAZ, ZAZ]),
        ('b', [BMW]),
        ('З', [ZAZ]),
        ('Da', [DADI, DAEWOO]),
    ],
)
def test_car_brands(
        taxi_driver_protocol,
        prefix_filter,
        expected_brands,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'session_1', 'selfreg1')

    response = taxi_driver_protocol.get(
        '/driver/car/brands',
        params={'db': '777', 'session': 'session_1', 'filter': prefix_filter},
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_response = {'brands': expected_brands}
    assert response_json == expected_response
