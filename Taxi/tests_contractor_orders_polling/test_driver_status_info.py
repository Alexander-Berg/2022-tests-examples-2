import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.parametrize(
    'park_id, driver_id, expected_driver_status',
    [
        ['park_1', 'driver_is_online', {'revision': 100, 'value': 'free'}],
        ['park_1', 'driver_is_offline', {'revision': 0, 'value': 'busy'}],
        ['park_1', 'driver_is_busy', {'revision': 101, 'value': 'busy'}],
    ],
)
async def test_driver_status_info(
        taxi_contractor_orders_polling,
        park_id,
        driver_id,
        expected_driver_status,
):

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers={
            **utils.HEADERS,
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
        },
    )

    assert response.status_code == 200
    assert response.json().get('driver_status_info') == expected_driver_status
