import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/device/park-bindings'
HEADERS = {**web_common.PARTNER_HEADERS_1}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'serial, imei, park_id, code, resp, add_spec',
    [
        ('212021120002D', 'kek_lol', 'park_1', 200, {}, False),
        ('212021120001F', 'top_kek', 'park_1', 200, {}, False),
        ('212021120003B', 'just_kek', 'park_1', 200, {}, False),
        ('212021120003B', 'just_kek', 'park_3', 200, {}, True),
        (
            '212021120002D',
            'ne_kek_ne_lol',
            'park_1',
            400,
            {
                'code': 'invalid_imei',
                'message': 'IMEI does not match known for device',
            },
            False,
        ),
        (
            '313021120003B',
            'another_kek',
            'park_1',
            400,
            {'code': 'registered_in_other_park', 'message': 'park_2'},
            False,
        ),
        (
            '88005553535',
            'ochen_plohie_dannie',
            'park_3',
            400,
            {'code': 'invalid_serial', 'message': 'Bad serial number'},
            False,
        ),
        (
            '414021120003B',
            'rano_polezli',
            'park_1',
            400,
            {
                'code': 'device_not_registered',
                'message': 'Device not yet registered (no IMEI)',
            },
            False,
        ),
    ],
)
async def test_park_device_binding_put(
        taxi_signal_device_api_admin,
        mockserver,
        pgsql,
        stq,
        stq_runner,
        serial,
        imei,
        park_id,
        add_spec,
        code,
        resp,
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

    @mockserver.json_handler('fleet-parks/v1/parks/specifications')
    def post(request):
        request_parsed = request.json
        assert request_parsed['created_by'] == {
            'passport_uid': HEADERS['X-Yandex-UID'],
        }
        assert request_parsed['specifications'] == ['signalq']
        assert request.query == {'park_id': park_id}
        return mockserver.make_response(json={}, status=200)

    HEADERS['X-Park-Id'] = park_id
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        params={'serial_number': serial, 'imei': imei},
        headers=HEADERS,
    )
    assert response.status_code == code, response.text
    assert response.json() == resp

    if add_spec:
        assert stq.signal_device_api_admin_add_specification.times_called == 1
        stq_call = stq.signal_device_api_admin_add_specification.next_call()
        await stq_runner.signal_device_api_admin_add_specification.call(
            task_id=stq_call['id'],
            args=stq_call['args'],
            kwargs=stq_call['kwargs'],
        )
        assert post.times_called == 1
    else:
        assert stq.signal_device_api_admin_add_specification.times_called == 0

    if code == 200:
        db = pgsql['signal_device_api_meta_db'].cursor()
        db.execute(
            'SELECT park_id '
            'FROM signal_device_api.park_device_profiles '
            'WHERE device_id=(SELECT id FROM signal_device_api.devices '
            f'WHERE serial_number=\'{serial}\') '
            'AND is_active',
        )
        assert list(db)[0][0] == park_id
