import pytest


ENDPOINT = 'internal/signal-device-api/v1/device/park'


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.parametrize(
    'serial_number, expected_park',
    [('SERIAL1', 'PARK_ID1'), ('SERIAL2', 'nopark')],
)
async def test_v1_device_get_park(
        taxi_signal_device_api, serial_number, expected_park,
):
    response = await taxi_signal_device_api.get(
        ENDPOINT, params={'serial_number': serial_number},
    )

    assert response.status_code == 200, response.text
    assert response.json()['park_id'] == expected_park
