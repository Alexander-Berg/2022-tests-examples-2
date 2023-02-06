import pytest

DRIVER_HEADERS = {
    'X-Yandex-Login': 'vdovkin',
    'X-YaTaxi-Park-Id': 'park_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver_0',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.37 (1234)',
    'X-Request-Platform': 'android',
    'Accept-Language': 'ru',
}
ZONE_TO_COORDS = {
    'moscow': {'lon': 37.627920, 'lat': 55.744094, 'timestamp': 123},
}


@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_activate.sql'],
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'response_json',
    [
        'response_disabled.json',
        pytest.param(
            'response_enabled.json',
            marks=pytest.mark.experiments3(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='driver_promocodes_enabled',
                consumers=['driver-promocodes/driver'],
                clauses=[],
                default_value={'enabled': True},
            ),
        ),
    ],
)
async def test_driver_promocodes_count_new(
        taxi_driver_promocodes, parks, load_json, response_json,
):

    response = await taxi_driver_promocodes.get(
        'driver/v1/promocodes/v1/count-new',
        headers=DRIVER_HEADERS,
        params={
            'lat': ZONE_TO_COORDS['moscow']['lat'],
            'lon': ZONE_TO_COORDS['moscow']['lon'],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_json)
