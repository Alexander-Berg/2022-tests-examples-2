# pylint: disable=import-error
import pytest

from tests_dispatch_airport import common


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'reason_code, expected_push',
    [
        (None, None),
        ('unknown_code', None),
        (
            'known_code',
            {
                'client_id': 'dbid-uuid1',
                'data': {'code': 1300},
                'intent': 'PersonalOffer',
                'notification': {
                    'text': {'key': 'some_key', 'keyset': 'some_keyset'},
                },
                'service': 'taximeter',
            },
        ),
    ],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_RELOCATION_STOP_PUSH_SETTINGS={
        'known_code': {'key': 'some_key', 'keyset': 'some_keyset'},
    },
)
async def test_relocate_stop(
        taxi_dispatch_airport, mockserver, reason_code, expected_push,
):
    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        assert request.json == {
            'driver_profile_id': 'uuid1',
            'park_id': 'dbid',
            'type': 'driver',
        }
        return {}

    @mockserver.json_handler('/client-notify/v2/push')
    def client_push(request):
        assert request.json == expected_push
        return {'notification_id': '1'}

    resp = await taxi_dispatch_airport.post(
        '/v1/relocate/stop',
        {'session_id': 'dbid_uuid1_reposition-id', 'reason_code': reason_code},
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )

    assert resp.json() == {}
    if expected_push is not None:
        assert client_push.times_called == 1


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('stop_disabled', [True, False])
async def test_relocate_stop_bad_id(
        taxi_dispatch_airport, taxi_config, stop_disabled,
):
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_RELOCATION_PARTNER_STOP_DISABLED': stop_disabled},
    )
    await taxi_dispatch_airport.invalidate_caches()

    resp = await taxi_dispatch_airport.post(
        '/v1/relocate/stop',
        {'session_id': 'dbid-uuid1_reposition-id'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )

    etalon = {}
    if not stop_disabled:
        etalon = {
            'code': 'MALFORMED_OFFER_ID',
            'message': 'Malformed offer id',
        }
    r_json = resp.json()
    assert r_json == etalon


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'push_status, expected_code',
    [(400, 'SEND_INFO_PUSH_INVALID_ARGS'), (502, 'SEND_INFO_PUSH_ERROR')],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_RELOCATION_STOP_PUSH_SETTINGS={
        'known_code': {'key': 'some_key', 'keyset': 'some_keyset'},
    },
)
async def test_relocate_stop_push_error(
        taxi_dispatch_airport, mockserver, push_status, expected_code,
):
    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        assert request.json == {
            'driver_profile_id': 'uuid1',
            'park_id': 'dbid',
            'type': 'driver',
        }
        return {}

    @mockserver.json_handler('/client-notify/v2/push')
    def _client_push(request):
        return mockserver.make_response(
            json={'code': 'some_code', 'message': 'some_message'},
            status=push_status,
        )

    resp = await taxi_dispatch_airport.post(
        '/v1/relocate/stop',
        {
            'session_id': 'dbid_uuid1_reposition-id',
            'reason_code': 'known_code',
        },
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )

    assert resp.status_code == 500
    assert resp.json()['code'] == expected_code
