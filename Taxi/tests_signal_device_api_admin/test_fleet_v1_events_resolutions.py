import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/events/resolutions'


@pytest.mark.parametrize(
    'public_event_id, request_to_sda, event_id',
    [
        (
            '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
            True,
            '0ef0466e6e1331b3a7d35c585983076a',
        ),
        (
            '54b3d7ec-30f6-43cf-94a8-911bc8fe404c',
            False,
            '5e94c0875963785801eed76c4322b394',
        ),
    ],
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_ok_seen(
        taxi_signal_device_api_admin,
        pgsql,
        mockserver,
        public_event_id,
        event_id,
        request_to_sda,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    @mockserver.json_handler(
        '/signalq-drivematics-api/internal/signalq-drivematics-api/v1/fleet/events/resolutions',  # noqa: E501 line too long
    )
    def _mock_signalq_drivematics_api(request):
        assert request.json['event_at'] == 1582804800
        assert request.json['serial_number'] == 'AB1'
        assert request.json['event_id'] == event_id
        return {}

    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        json={'resolution': 'wrong_event'},
        params={'event_id': public_event_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""SELECT resolution FROM signal_device_api.events
            WHERE public_event_id='{public_event_id}'""",
    )
    assert list(db)[0][0] == 'wrong_event'
    if request_to_sda:
        assert _mock_signalq_drivematics_api.times_called == 1
    else:
        assert _mock_signalq_drivematics_api.times_called == 0
