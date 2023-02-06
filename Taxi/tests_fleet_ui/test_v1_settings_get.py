import pytest

from tests_fleet_ui import utils

ENDPOINT = '/fleet/ui/v1/settings'

OK_PARAMS = [
    (
        'park_1',
        'setting_1',
        {'value': {'val_number': 1, 'val_str': 'some_string_1'}},
    ),
    ('park_1', 'setting_2', {'value': 100}),
    (
        'park_2',
        'setting_1',
        {'value': {'val_number': 2, 'val_str': 'some_string_2'}},
    ),
]


@pytest.mark.parametrize('park_id, setting_key, expected_response', OK_PARAMS)
async def test_ok(taxi_fleet_ui, park_id, setting_key, expected_response):
    response = await taxi_fleet_ui.get(
        ENDPOINT,
        headers=utils.build_headers(park_id=park_id),
        params={'key': setting_key},
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_not_found(taxi_fleet_ui):
    response = await taxi_fleet_ui.get(
        ENDPOINT,
        headers=utils.build_headers(park_id='park_1'),
        params={'key': 'invalid_setting_key'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'setting_key_not_found',
        'message': 'Setting key not found',
    }
