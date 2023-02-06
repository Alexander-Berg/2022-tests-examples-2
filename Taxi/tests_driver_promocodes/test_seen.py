import pytest

from . import utils

DRIVER_HEADERS = {
    'X-Yandex-Login': 'vdovkin',
    'X-YaTaxi-Park-Id': 'park_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver_0',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.37 (1234)',
    'X-Request-Platform': 'android',
    'Accept-Language': 'ru',
}


@pytest.mark.pgsql(
    'driver_promocodes', files=['series.sql', 'promocodes_to_activate.sql'],
)
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'promocodes,response_list',
    [
        # ok
        (['promocode_ok', 'promocode_activated'], 'response_list_after.json'),
        # wrong id
        (['promocode_wrong'], None),
    ],
)
async def test_driver_promocodes_seen(
        taxi_driver_promocodes,
        parks,
        load_json,
        mockserver,
        promocodes,
        response_list,
):

    response = await taxi_driver_promocodes.post(
        'driver/v1/promocodes/v1/seen',
        json={'seen_ids': promocodes},
        headers=DRIVER_HEADERS,
    )
    assert response.status_code == 200
    if response_list:
        response = await taxi_driver_promocodes.get(
            'admin/v1/promocodes/list',
            params={'entity_id': 'park_0_driver_0'},
        )
        assert utils.remove_not_testable_promocodes(
            response.json(),
        ) == utils.remove_not_testable_promocodes(load_json(response_list))
