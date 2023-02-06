import pytest

from tests_fleet_ui import utils

ENDPOINT = '/fleet/ui/v1/settings'

OK_PARAMS = [
    ('1_setting_string', {'value': 'hello'}),
    ('2_setting_integer', {'value': 7}),
    ('3_setting_number', {'value': 14.5}),
]


@pytest.mark.parametrize('key, value', OK_PARAMS)
async def test_ok(taxi_fleet_ui, pgsql, key, value):
    response = await taxi_fleet_ui.put(
        ENDPOINT,
        headers=utils.build_headers(park_id='park_id'),
        params={'key': key},
        json=value,
    )

    assert response.status_code == 204, response.text

    cursor = pgsql['fleet_ui'].cursor()
    cursor.execute(
        f"""
        SELECT data
        FROM fleet_ui.user_settings
        WHERE key='{key}'
        """,
    )
    assert cursor.fetchall()[0][0] == value


async def test_bad_request(taxi_fleet_ui):
    response = await taxi_fleet_ui.put(
        ENDPOINT,
        headers=utils.build_headers(park_id='park_id'),
        params={'key': 'new_setting'},
        json={'bad': 'payload'},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'value_must_be_present',
        'message': 'Field \"value\" must be present',
    }
