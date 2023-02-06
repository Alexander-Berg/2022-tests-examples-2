# TODO: remove after https://st.yandex-team.ru/TAXIDUTY-32383

import copy
import datetime

import pytest


def in_n_hours(n_hours):
    now = datetime.datetime.now() + datetime.timedelta(hours=n_hours)
    return now.strftime('%Y-%m-%dT%H:%M:%SZ')


@pytest.fixture(name='mock_vgw_default')
def _mock_vgw_default(mockserver):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }

    return _vgw_request


@pytest.mark.config(
    CARGO_CLAIMS_VOICEFORWARDING_SETTINGS_BY_CLIENT={
        '01234567890123456789012345678912': {
            'min_ttl': 30,
            'new_ttl': 200,
            'consumer_id': 3,
        },
    },
)
@pytest.mark.parametrize(
    'url',
    [
        '/api/integration/v1/driver-voiceforwarding',
        '/api/integration/v1/driver-voiceforwarding',
    ],
)
@pytest.mark.now('2020-04-01T10:35:00+0000')
async def test_integration_voiceforwarding(
        taxi_cargo_claims, mockserver, create_claim_with_performer, url,
):
    claim_uuid = create_claim_with_performer.claim_id

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        vgw_req = request.json
        del vgw_req['nonce']
        assert vgw_req == {
            'call_location': [37.5, 55.7],
            'callee': 'driver',
            'callee_phone': '+70000000000',
            'consumer': 3,
            'external_ref_id': 'taxi_order_id_1',
            'min_ttl': 30,
            'new_ttl': 200,
            'requester': 'passenger',
        }
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }

    response = await taxi_cargo_claims.post(url, json={'claim_id': claim_uuid})
    assert response.status_code == 200
    assert response.json() == {
        'phone': '+71234567890',
        'ext': '100',
        'ttl_seconds': 3600,
    }
    assert _vgw_request.times_called == 1


@pytest.mark.parametrize(
    'url',
    [
        '/api/integration/v1/driver-voiceforwarding',
        '/api/integration/v1/driver-voiceforwarding',
    ],
)
async def test_integration_voiceforwarding409(
        taxi_cargo_claims, state_controller, url,
):
    claim_info = await state_controller.apply(target_status='delivered_finish')
    claim_uuid = claim_info.claim_id

    response = await taxi_cargo_claims.post(url, json={'claim_id': claim_uuid})
    assert response.status_code == 409


@pytest.mark.parametrize(
    'url',
    [
        '/api/integration/v1/driver-voiceforwarding',
        '/api/integration/v1/driver-voiceforwarding',
    ],
)
async def test_integration_voiceforwarding404(
        taxi_cargo_claims, create_default_claim, url,
):
    response = await taxi_cargo_claims.post(
        url, json={'claim_id': create_default_claim.claim_id},
    )
    assert response.status_code == 404


@pytest.mark.now('2020-04-01T10:35:00+0000')
async def test_sharedroute_voiceforwarding(
        taxi_cargo_claims,
        mockserver,
        pgsql,
        state_controller,
        get_sharing_keys,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_uuid = claim_info.claim_id

    sharing_key = get_sharing_keys(claim_uuid=claim_uuid)[0]

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        vgw_req = request.json
        del vgw_req['nonce']
        assert vgw_req == {
            'call_location': [37.2, 55.8],
            'callee': 'driver',
            'callee_phone': '+70000000000',
            'consumer': 2,
            'external_ref_id': 'taxi_order_id_1',
            'min_ttl': 20,
            'new_ttl': 100,
            'requester': 'passenger',
        }
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }

    response = await taxi_cargo_claims.get(
        '/api/integration/noauth/v1/sharing-route/driver-voiceforwarding',
        params={'sharing_key': sharing_key},
    )
    assert response.status_code == 200
    assert response.json() == {
        'phone': '+71234567890',
        'ext': '100',
        'ttl_seconds': 3600,
    }
    assert _vgw_request.times_called == 1


async def test_sharedroute_voiceforwarding_inappropriate_point(
        taxi_cargo_claims, pgsql, state_controller, get_sharing_keys,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_uuid = claim_info.claim_id

    sharing_key = get_sharing_keys(claim_uuid=claim_uuid)[1]
    response = await taxi_cargo_claims.get(
        '/api/integration/noauth/v1/sharing-route/driver-voiceforwarding',
        params={'sharing_key': sharing_key},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'inappropriate_point',
        'message': 'current point is not equal to this',
    }

    claim_info = await state_controller.apply(
        target_status='delivered_finish', fresh_claim=False,
    )

    sharing_key = get_sharing_keys(claim_uuid=claim_uuid)[0]
    response = await taxi_cargo_claims.get(
        '/api/integration/noauth/v1/sharing-route/driver-voiceforwarding',
        params={'sharing_key': sharing_key},
    )
    assert response.status_code == 404


async def test_sharedroute_voiceforwarding404(
        taxi_cargo_claims, state_controller,
):
    state_controller.use_create_version('v2')
    await state_controller.apply(target_status='performer_found')

    response = await taxi_cargo_claims.get(
        '/api/integration/noauth/v1/sharing-route/driver-voiceforwarding',
        params={'sharing_key': 'abcabcabcabcabcabcabcabcabcabcabc'},
    )
    assert response.status_code == 404


@pytest.mark.config(
    CARGO_CLAIMS_VOICEFORWARDING_SETTINGS={
        'consumer': 2,
        'new_ttl': 100,
        'min_ttl': 20,
        'max_claim_age_hours': 1,
    },
)
@pytest.mark.parametrize(
    'old',
    [
        pytest.param(True, marks=pytest.mark.now(in_n_hours(2))),
        pytest.param(False),
    ],
)
async def test_old_claim404(
        taxi_cargo_claims, state_controller, mockserver, old, mock_vgw_default,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')

    response = await taxi_cargo_claims.post(
        '/api/integration/v1/driver-voiceforwarding',
        json={'claim_id': claim_info.claim_id},
    )
    if old:
        assert response.status_code == 404
        assert mock_vgw_default.times_called == 0
    else:
        assert response.status_code == 200
        assert mock_vgw_default.times_called == 1


@pytest.mark.now('2020-04-01T10:35:00+0000')
async def test_sharedroute_voiceforwarding_c2c(
        taxi_cargo_claims,
        mockserver,
        pgsql,
        mock_create_event,
        state_controller,
        get_sharing_keys,
):
    mock_create_event()
    state_controller.use_create_version('v2_cargo_c2c')
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_uuid = claim_info.claim_id

    sharing_key = get_sharing_keys(claim_uuid=claim_uuid)[0]

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        assert 'requester_phone' not in request.json
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }

    response = await taxi_cargo_claims.get(
        '/api/integration/noauth/v1/sharing-route/driver-voiceforwarding',
        params={'sharing_key': sharing_key},
    )
    assert response.status_code == 200
    assert response.json() == {
        'phone': '+71234567890',
        'ext': '100',
        'ttl_seconds': 3600,
    }
    assert _vgw_request.times_called == 1


@pytest.mark.now('2020-04-01T10:35:00+0000')
async def test_integration_voiceforwarding_point_id_sender_is_picker(
        taxi_cargo_claims, get_default_request, state_controller, mockserver,
):
    request = copy.deepcopy(get_default_request(with_brand_id=False))
    request['custom_context']['sender_is_picker'] = True

    state_controller.handlers().create.request = request
    claim_info = claim_info = await state_controller.apply(
        target_status='performer_found',
    )
    claim_uuid = claim_info.claim_id

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        vgw_req = request.json
        del vgw_req['nonce']
        assert vgw_req['requester_phone'] == '+72222222222'
        assert vgw_req['requester'] == 'driver'
        return {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }

    response = await taxi_cargo_claims.post(
        '/api/integration/v1/driver-voiceforwarding',
        json={'claim_id': claim_uuid, 'point_id': 2},
    )
    assert response.status_code == 200
