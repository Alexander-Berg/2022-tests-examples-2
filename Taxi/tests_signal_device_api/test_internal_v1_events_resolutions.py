import pytest


ENDPOINT = 'internal/signal-device-api/v1/events/resolutions'

HEADERS = {
    'X-Ya-User-Ticket': 'valid_user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '54591353',
}


@pytest.mark.parametrize(
    'event_id, serial_number, expected_code, expected_message',
    [
        ('id-1', 'SERIAL1', 200, ''),
        (
            'id-2',
            'SERIAL1',
            404,
            'cant find event with event_id = id-2 for serial number = SERIAL1',
        ),
        (
            'id-1',
            'SERIAL2',
            404,
            'cant find event with event_id = id-1 for serial number = SERIAL2',
        ),
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['resolutions.sql'])
async def test_resolution(
        taxi_signal_device_api,
        pgsql,
        serial_number,
        event_id,
        expected_code,
        expected_message,
):
    body = {
        'serial_number': serial_number,
        'event_id': event_id,
        'resolution': 'hide',
    }
    response = await taxi_signal_device_api.post(
        ENDPOINT, headers=HEADERS, json=body,
    )
    assert response.status_code == expected_code
    if expected_message:
        assert response.json()['message'] == expected_message
    else:
        db = pgsql['signal_device_api_meta_db'].cursor()
        db.execute(
            f"""SELECT resolution FROM signal_device_api.events
                WHERE event_id='{event_id}'""",
        )
        assert list(db)[0][0] == 'hide'
