import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/device/park-bindings'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'serial, park_id, is_binded_other_park, code, resp',
    [
        ('313021120003B', 'park_2', False, 200, {}),
        ('212021120001F', 'park_2', True, 200, {}),
        (
            '414021120003B',
            'park_2',
            False,
            400,
            {'code': 'invalid_serial', 'message': 'Bad serial number'},
        ),
        (
            '914021122303B',
            'park_2',
            False,
            400,
            {'code': 'invalid_serial', 'message': 'Bad serial number'},
        ),
        ('212021120001F', 'park_1', False, 200, {}),
    ],
)
async def test_park_device_binding_delete(
        taxi_signal_device_api_admin,
        pgsql,
        serial,
        park_id,
        is_binded_other_park,
        code,
        resp,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.delete(
        ENDPOINT,
        params={'serial_number': serial},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == code, response.text
    assert response.json() == resp

    if code == 200 and not is_binded_other_park:
        db = pgsql['signal_device_api_meta_db'].cursor()
        db.execute(
            'SELECT is_active, group_id '
            'FROM signal_device_api.park_device_profiles '
            'WHERE device_id=(SELECT id FROM signal_device_api.devices '
            f'WHERE serial_number=\'{serial}\') '
            f'AND park_id = \'{park_id}\' ',
        )
        assert list(db)[0] == (False, None)
