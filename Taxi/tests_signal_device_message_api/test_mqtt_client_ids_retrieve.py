import pytest


ENDPOINT = '/internal/v1/signal-device-message-api/mqtt-client-ids/retrieve'


@pytest.mark.parametrize(
    'serial_numbers, expected_devices',
    [
        (['AB1', 'AB2'], []),
        (['AB3', 'AB4'], [{'serial_number': 'AB3', 'client_id': 'CL1'}]),
        (
            ['AB6', 'AB7', 'AB9'],
            [
                {'serial_number': 'AB6', 'client_id': 'CL2'},
                {'serial_number': 'AB7', 'client_id': 'CL3'},
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'signal_device_message_api', files=['signal_device_message_api_db.sql'],
)
async def test_mqtt_client_ids_retrieve(
        taxi_signal_device_message_api, serial_numbers, expected_devices,
):
    response = await taxi_signal_device_message_api.post(
        ENDPOINT, json={'serial_numbers': serial_numbers},
    )

    assert response.status_code == 200, response.text
    assert sorted(
        response.json()['devices'], key=lambda x: x['serial_number'],
    ) == sorted(expected_devices, key=lambda x: x['serial_number'])
