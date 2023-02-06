import pytest

from . import utils as test_utils

CODEGEN_HANDLER_URL = 'driver/v1/loyalty/v1/status'

# pylint: disable=too-many-arguments
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {
                'loyalty': '8.80',
                'taximeter_xs': '8.80 (12345678)',
            },
        },
    },
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    'position,unique_driver_id,user_agent,expected_code,' 'expected_response',
    [
        (
            [37.590533, 55.733863],
            '000000000000000000000001',
            'Taximeter 8.80 (562)',
            200,
            'expected_response1.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000001',
            'Taximeter-AZ 8.80 (562)',
            200,
            'expected_response1.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000011',
            'Taximeter 8.80 (562)',
            200,
            'expected_response2.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000012',
            'Taximeter 8.80 (562)',
            200,
            'expected_response3.json',
        ),
        (
            [37.485333, 54.122222],
            '000000000000000000000011',
            'Taximeter 8.80 (562)',
            200,
            'expected_response4.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000003',
            'Taximeter 8.80 (562)',
            200,
            'expected_response5.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            'Taximeter 8.80 (562)',
            200,
            'expected_response6.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000015',
            'Taximeter 8.80 (562)',
            200,
            'expected_response7.json',
        ),
        (
            [37.590533, 59.733863],
            '000000000000000000000012',
            'Taximeter 8.80 (562)',
            200,
            'expected_response8.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000001',
            'Taximeter 8.80 (12345678)',
            200,
            'expected_response9.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000014',
            'Taximeter 8.80 (12345678)',
            200,
            'expected_response10.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000012',
            'Taximeter 8.80 (12345678)',
            200,
            'expected_response11.json',
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000015',
            'Taximeter 8.80 (12345678)',
            200,
            'expected_response12.json',
        ),
        (
            [37.590533, 59.733863],
            '000000000000000000000011',
            'Taximeter 8.80 (562)',
            200,
            'expected_response13.json',
        ),
        (
            [37.590533, 59.733863],
            '000000000000000000000001',
            'Taximeter 8.80 (12345678)',
            200,
            'expected_response14.json',
        ),
        (
            [37.485333, 54.122222],
            '000000000000000000000001',
            'Taximeter 8.80 (12345678)',
            200,
            'expected_response15.json',
        ),
    ],
)
@pytest.mark.now('2019-03-10T08:35:00+0300')
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
@pytest.mark.experiments3(filename='loyalty_ui_statuses.json')
async def test_driver_loyalty_status(
        taxi_loyalty,
        unique_drivers,
        load_json,
        pgsql,
        position,
        unique_driver_id,
        user_agent,
        expected_code,
        expected_response,
        mock_fleet_parks_list,
):
    unique_drivers.set_unique_driver(
        'driver_db_id1', 'driver_uuid1', unique_driver_id,
    )

    def select(unique_driver_id):
        cursor = pgsql['loyalty'].cursor()
        cursor.execute(
            'SELECT send_notification FROM loyalty.loyalty_accounts '
            'WHERE unique_driver_id = \'{}\''.format(unique_driver_id),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', user_agent,
        ),
    )

    assert response.status_code == expected_code
    response = response.json()

    if 'menu_items' in response['ui']:
        for item in response['ui']['menu_items']:
            if 'tooltip_params' in item:
                item['tooltip_params'].pop('id')

    assert response == load_json('response/' + expected_response)

    account = select(unique_driver_id)
    assert account == [(False,)]
