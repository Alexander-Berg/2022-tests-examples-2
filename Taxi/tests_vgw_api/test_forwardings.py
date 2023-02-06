# pylint: disable=too-many-lines
import datetime
import json

import dateutil.parser
import pytest
import pytz


def mark_vgw_configs():
    return pytest.mark.config(
        VGW_API_CLIENT_TIMEOUT=2000,
        VGW_API_CONSUMER_CLIENT_TYPE_MAP={
            '__default__': {
                'forwarding_types': [
                    {
                        'src_type': 'passenger',
                        'dst_type': 'driver',
                        'phone_pool_name': 'mobile',
                    },
                    {
                        'src_type': 'driver',
                        'dst_type': 'passenger',
                        'phone_pool_name': 'driver',
                    },
                    {
                        'src_type': 'dispatcher',
                        'dst_type': 'passenger',
                        'phone_pool_name': 'driver',
                    },
                ],
            },
        },
    )


def param_use_vgw_enable_settings():
    return pytest.mark.parametrize(
        [],
        (
            pytest.param(
                id='old settings',
                marks=pytest.mark.config(
                    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=False,
                ),
            ),
            pytest.param(
                id='new settings',
                marks=pytest.mark.config(
                    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
                ),
            ),
        ),
    )


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_normal(taxi_vgw_api, mockserver):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': '2018-02-25T05:00:00+0300',
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T02:00:00+00:00'


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.parametrize(
    'request_data',
    [
        # Non existing region
        (
            {
                'external_ref_id': '<ref_id>',
                'requester': 'passenger',
                'callee': 'driver',
                'callee_phone': '+79000000000',
                'requester_phone': '+79100000000',
                'nonce': '<nonce>',
                'consumer': 1,
                'new_ttl': 7200,
                'min_ttl': 7200,
                'call_location': [129.6755, 62.0355],  # Yakutsk
            }
        ),
        # Disabled for callee type in region
        (
            {
                'external_ref_id': '<ref_id>',
                'requester': 'driver',
                'callee': 'passenger',
                'callee_phone': '+79000000000',
                'requester_phone': '+79100000000',
                'nonce': '<nonce>',
                'consumer': 1,
                'new_ttl': 7200,
                'min_ttl': 7200,
                'call_location': [30.3351, 59.9343],  # Saint Petersburg
            }
        ),
        # Gateway disabled for region
        (
            {
                'external_ref_id': '<ref_id>',
                'requester': 'passenger',
                'callee': 'driver',
                'callee_phone': '+79000000000',
                'requester_phone': '+79100000000',
                'nonce': '<nonce>',
                'consumer': 1,
                'new_ttl': 7200,
                'min_ttl': 7200,
                'call_location': [36.587223, 50.59566],  # Belgorod
            }
        ),
    ],
)
@param_use_vgw_enable_settings()
async def test_forwarding_post_region_not_supported(
        taxi_vgw_api, request_data,
):
    response = await taxi_vgw_api.post('v1/forwardings', request_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == 'RegionIsNotSupported'
    assert response_json['error']['code'] == 'RegionIsNotSupported'


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.parametrize(
    'request_data',
    [
        # Non existing consumer
        (
            {
                'external_ref_id': '<ref_id>',
                'requester': 'passenger',
                'callee': 'driver',
                'callee_phone': '+79000000000',
                'requester_phone': '+79100000000',
                'nonce': '<nonce>',
                'consumer': 20,
                'new_ttl': 7200,
                'min_ttl': 7200,
                'call_location': [37.618423, 55.751244],
            }
        ),
        # Disabled consumer
        (
            {
                'external_ref_id': '<ref_id>',
                'requester': 'passenger',
                'callee': 'driver',
                'callee_phone': '+79000000000',
                'requester_phone': '+79100000000',
                'nonce': '<nonce>',
                'consumer': 2,
                'new_ttl': 7200,
                'min_ttl': 7200,
                'call_location': [37.618423, 55.751244],
            }
        ),
    ],
)
@param_use_vgw_enable_settings()
async def test_forwarding_post_consumer_not_supported(
        taxi_vgw_api, request_data,
):
    response = await taxi_vgw_api.post('v1/forwardings', request_data)
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == 'ConsumerIsNotSupported'
    assert response_json['error']['code'] == 'ConsumerIsNotSupported'


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_idempotency_conflict(taxi_vgw_api, mockserver):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': '2018-02-25T05:00:00+0300',
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response1 = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response1.status_code == 200
    response_json = response1.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T02:00:00+00:00'

    response2 = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response2.status_code == 400
    response_json = response2.json()
    assert response_json['code'] == 'IdempotencyConflict'
    assert response_json['error']['code'] == 'IdempotencyConflict'


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_bad_location(taxi_vgw_api):
    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [900000, 900000],
        },
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == 'RegionIsNotSupported'
    assert response_json['error']['code'] == 'RegionIsNotSupported'


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_check_forwarding_id(taxi_vgw_api, mockserver):
    call_count = 0

    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        nonlocal call_count
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        id_ = body_request.pop('id')
        assert id_ == (
            '000000000000000000000000000000000200000' + str(call_count)
        )
        assert body_request == {
            'city': 'Moscow',
            'expire': '2018-02-25T05:00:00+0300',
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        call_count += 1
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response1 = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '00000000000000000000000000000000',
            'caller': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'caller_phone': '+79100000000',
            'nonce': '<nonce1>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response1.status_code == 200
    response_json = response1.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T02:00:00+00:00'

    response2 = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '00000000000000000000000000000000',
            'caller': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'caller_phone': '+79100000000',
            'nonce': '<nonce2>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response2.status_code == 200
    response_json = response2.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T02:00:00+00:00'


@pytest.mark.parametrize(
    ('params', 'response_data'),
    [
        (
            {'external_ref_id': 'ext_ref_id_1'},
            [
                {
                    'forwarding_id': 'fwd_id_1',
                    'gateway_id': 'gateway_id_1',
                    'state': 'created',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '888',
                    'external_ref_id': 'ext_ref_id_1',
                    'talks': [
                        {
                            'id': 'talk_id_1',
                            'length': 10,
                            'started_at': '2018-02-26T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79000000000',
                        },
                    ],
                },
            ],
        ),
        (
            {'external_ref_id': 'ext_ref_id_2'},
            [
                {
                    'forwarding_id': 'fwd_id_2',
                    'gateway_id': 'gateway_id_2',
                    'state': 'broken',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [],
                },
                {
                    'forwarding_id': 'fwd_id_3',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '999',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [
                        {
                            'id': 'talk_id_2',
                            'length': 20,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                        {
                            'id': 'talk_id_3',
                            'length': 30,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                    ],
                },
            ],
        ),
        (
            {'redirection_phone': '+71111111111'},
            [
                {
                    'forwarding_id': 'fwd_id_1',
                    'gateway_id': 'gateway_id_1',
                    'state': 'created',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '888',
                    'external_ref_id': 'ext_ref_id_1',
                    'talks': [
                        {
                            'id': 'talk_id_1',
                            'length': 10,
                            'started_at': '2018-02-26T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79000000000',
                        },
                    ],
                },
                {
                    'forwarding_id': 'fwd_id_3',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '999',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [
                        {
                            'id': 'talk_id_2',
                            'length': 20,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                        {
                            'id': 'talk_id_3',
                            'length': 30,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                    ],
                },
                {
                    'forwarding_id': 'fwd_id_4',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
                {
                    'forwarding_id': 'fwd_id_5',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
            ],
        ),
        (
            {'redirection_phone': '+71111111111,888'},
            [
                {
                    'forwarding_id': 'fwd_id_1',
                    'gateway_id': 'gateway_id_1',
                    'state': 'created',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '888',
                    'external_ref_id': 'ext_ref_id_1',
                    'talks': [
                        {
                            'id': 'talk_id_1',
                            'length': 10,
                            'started_at': '2018-02-26T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79000000000',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'redirection_phone': '+71111111111',
                'created_before': '2018-02-26T17:00:00+00:00',
            },
            [
                {
                    'forwarding_id': 'fwd_id_1',
                    'gateway_id': 'gateway_id_1',
                    'state': 'created',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '888',
                    'external_ref_id': 'ext_ref_id_1',
                    'talks': [
                        {
                            'id': 'talk_id_1',
                            'length': 10,
                            'started_at': '2018-02-26T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79000000000',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'redirection_phone': '+71111111111',
                'created_after': '2018-02-26T17:00:00+00:00',
            },
            [
                {
                    'forwarding_id': 'fwd_id_3',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '999',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [
                        {
                            'id': 'talk_id_2',
                            'length': 20,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                        {
                            'id': 'talk_id_3',
                            'length': 30,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                    ],
                },
                {
                    'forwarding_id': 'fwd_id_4',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
                {
                    'forwarding_id': 'fwd_id_5',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
            ],
        ),
        (
            {
                'redirection_phone': '+71111111111',
                'created_after': '2018-02-28T19:00:00+0300',
                'created_before': '2018-02-28T20:00:00+0300',
            },
            [
                {
                    'forwarding_id': 'fwd_id_3',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '999',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [
                        {
                            'id': 'talk_id_2',
                            'length': 20,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                        {
                            'id': 'talk_id_3',
                            'length': 30,
                            'started_at': '2018-02-28T16:11:13+00:00',
                            'caller_phone_id': '<null>',
                            'caller_phone': '+79100000000',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'external_ref_id': 'ext_ref_id_2',
                'created_before': '2018-02-28T00:00:00+0300',
            },
            [
                {
                    'forwarding_id': 'fwd_id_2',
                    'gateway_id': 'gateway_id_2',
                    'state': 'broken',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [],
                },
            ],
        ),
        (
            {
                'external_ref_id': 'ext_ref_id_2',
                'created_before': '2018-02-26T16:11:13+00:00',
                'created_after': '2018-02-26T16:11:13+00:00',
            },
            [
                {
                    'forwarding_id': 'fwd_id_2',
                    'gateway_id': 'gateway_id_2',
                    'state': 'broken',
                    'created_at': '2018-02-26T16:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'external_ref_id': 'ext_ref_id_2',
                    'talks': [],
                },
            ],
        ),
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
async def test_forwarding_get_normal(taxi_vgw_api, params, response_data):
    response = await taxi_vgw_api.get('v1/forwardings', params=params)
    assert response.status_code == 200
    sorted_forwardings = sorted(
        response.json(), key=lambda k: k['forwarding_id'],
    )
    assert sorted_forwardings == response_data


@pytest.mark.parametrize(
    'params',
    [
        {'external_ref_id': 'ext_ref_id_1'},
        {'redirection_phone': '+71111111111'},
    ],
)
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_talk_results.sql'])
async def test_forwarding_call_result(taxi_vgw_api, params):
    response = await taxi_vgw_api.get(
        'v1/forwardings', params={'external_ref_id': 'ext_ref_id_1'},
    )
    assert response.status_code == 200
    sorted_forwardings = sorted(
        response.json(), key=lambda k: k['forwarding_id'],
    )

    assert sorted_forwardings == [
        {
            'forwarding_id': 'fwd_id_1',
            'external_ref_id': 'ext_ref_id_1',
            'gateway_id': 'gateway_id_1',
            'state': 'created',
            'created_at': '2018-02-26T16:11:13+00:00',
            'requester': 'driver',
            'callee': 'passenger',
            'phone': '+71111111111',
            'ext': '888',
            'requester_phone_id': '<null>',
            'callee_phone_id': '<null>',
            'requester_phone': '+70001112233',
            'callee_phone': '+79998887766',
            'talks': [
                {
                    'id': 'talk_id_1',
                    'started_at': '2018-02-26T16:11:14+00:00',
                    'length': 10,
                    'caller_phone_id': '<null>',
                    'caller_phone': '+79000000001',
                    'call_result': {
                        'succeeded': True,
                        'status': 'test_status_1',
                        'dial_time': 10,
                    },
                },
                {
                    'id': 'talk_id_2',
                    'started_at': '2018-02-28T16:11:15+00:00',
                    'length': 20,
                    'caller_phone_id': '<null>',
                    'caller_phone': '+79100000002',
                },
            ],
        },
    ]


@pytest.mark.parametrize(
    ['request_params', 'is_new_replica'],
    [
        pytest.param(
            {'external_ref_id': 'yt_id', 'consumer_id': 0},
            False,
            id='by ref_id, old replica',
        ),
        pytest.param(
            {'external_ref_id': 'yt_id'},
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_ref_id': {
                        'index_optimize_for': 'scan',
                        'force_new_replication': True,
                        'new_replication_since': '2019-05-20T00:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by ref_id, new replica scan',
        ),
        pytest.param(
            {'external_ref_id': 'yt_id'},
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_ref_id': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': True,
                        'new_replication_since': '2019-05-20T00:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'lookup'},
                },
            ),
            id='by ref_id, new replica lookup',
        ),
        pytest.param(
            {
                'external_ref_id': 'yt_id',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T00:00:00+0000',
            },
            False,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_ref_id': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': False,
                        'new_replication_since': '2019-05-20T20:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by ref_id, with time filter, old replica 1',
        ),
        pytest.param(
            {
                'external_ref_id': 'yt_id',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T00:00:00+0000',
            },
            False,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_ref_id': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': False,
                        'new_replication_since': '2019-05-21T20:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by ref_id, with time filter, old replica 2',
        ),
        pytest.param(
            {
                'external_ref_id': 'yt_id',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T00:00:00+0000',
            },
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_ref_id': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': False,
                        'new_replication_since': '2019-05-20T12:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by ref_id, with time filter, new replica 1',
        ),
        pytest.param(
            {
                'external_ref_id': 'yt_id',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T00:00:00+0000',
            },
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_ref_id': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': False,
                        'new_replication_since': '2019-05-19T12:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by ref_id, with time filter, new replica 2',
        ),
        pytest.param(
            {'redirection_phone': '88005553535'},
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_redirection_phone': {
                        'index_optimize_for': 'scan',
                        'force_new_replication': True,
                        'new_replication_since': '2019-05-20T00:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by phone, new replica scan',
        ),
        pytest.param(
            {'redirection_phone': '88005553535,12345', 'consumer_id': 0},
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_redirection_phone': {
                        'index_optimize_for': 'scan',
                        'force_new_replication': True,
                        'new_replication_since': '2019-05-20T00:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'lookup'},
                },
            ),
            id='by phone ext, new replica lookup',
        ),
        pytest.param(
            {
                'redirection_phone': '88005553535',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T12:00:00+0000',
            },
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_redirection_phone': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': False,
                        'new_replication_since': '2019-05-20T12:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by phone, with time filter, new replica 1',
        ),
        pytest.param(
            {
                'redirection_phone': '88005553535',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-20T23:00:00+0000',
            },
            True,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_fwd_by_redirection_phone': {
                        'index_optimize_for': 'lookup',
                        'force_new_replication': False,
                        'new_replication_since': '2019-05-19T12:00:00+00:00',
                    },
                    'get_talk_by_fwd_id': {'index_optimize_for': 'scan'},
                },
            ),
            id='by phone, with time filter, new replica 2',
        ),
    ],
)
@pytest.mark.now('2019-05-22T00:00:00+00:00')
@pytest.mark.yt(dyn_table_data=['yt_vgw_api_data.yaml'])
async def test_forwarding_get_yt_request(
        taxi_vgw_api,
        mockserver,
        testpoint,
        yt_apply,
        request_params,
        is_new_replica,
):
    @testpoint('yt-get-forwardings')
    def _yt_get_forwardings(data):
        pass

    response = await taxi_vgw_api.get('v1/forwardings', params=request_params)
    assert response.status_code == 200
    assert _yt_get_forwardings.times_called
    response_json = response.json()
    assert len(response_json) == 1
    requester_phone_pd_id = 'phone_pd_id_1' if is_new_replica else '<null>'
    callee_phone_pd_id = 'phone_pd_id_2' if is_new_replica else '<null>'
    assert response.json() == [
        {
            'callee': 'passenger',
            'callee_phone': '+79222222222',
            'callee_phone_id': callee_phone_pd_id,
            'created_at': '2019-05-20T18:19:48.131456+00:00',
            'external_ref_id': 'yt_id',
            'forwarding_id': 'forwarding_id_1',
            'gateway_id': 'gateway_id_1',
            'phone': '88005553535',
            'ext': '12345',
            'requester': 'passenger',
            'requester_phone': '+79111111111',
            'requester_phone_id': requester_phone_pd_id,
            'state': 'created',
            'talks': [
                {
                    'id': 'talk_1',
                    'started_at': '2019-03-20T09:40:00+00:00',
                    'length': 10,
                    'caller_phone_id': requester_phone_pd_id,
                    'caller_phone': '+79111111111',
                    'call_result': {
                        'succeeded': True,
                        'status': 'test status',
                        'dial_time': 5,
                    },
                },
                {
                    'id': 'talk_2',
                    'started_at': '2019-03-20T09:40:00+00:00',
                    'length': 10,
                    'caller_phone_id': requester_phone_pd_id,
                    'caller_phone': '+79111111111',
                },
                {
                    'id': 'talk_3',
                    'started_at': '2019-03-20T09:40:00+00:00',
                    'length': 10,
                    'caller_phone_id': '<null>',
                    'caller_phone': '',
                },
            ],
        },
    ]


@pytest.mark.parametrize(
    ('params', 'response_code', 'yt_called'),
    [
        pytest.param({'wrong_param_name': 'ext_ref_id_1'}, 400, 0),
        pytest.param({'external_ref_id': 'yt_id'}, 200, 1),
        pytest.param(
            {'external_ref_id': 'yt_id'},
            200,
            1,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 36,
                    'limit': 100,
                },
            ),
        ),
        pytest.param(
            {
                'redirection_phone': '88005553535',
                'created_after': '2019-05-21T00:00:00+0000',
                'created_before': '2019-05-20T00:00:00+0000',
            },
            400,
            0,
        ),
        pytest.param(
            {
                'redirection_phone': '88005553535',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T00:00:00+0000',
            },
            200,
            1,
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 36,
                    'limit': 100,
                },
            ),
        ),
        pytest.param(
            {
                'redirection_phone': '88005553535',
                'created_after': '2019-05-20T00:00:00+0000',
                'created_before': '2019-05-21T00:00:00+0000',
            },
            200,
            1,
            marks=pytest.mark.yt(dyn_table_data=['yt_vgw_api_data.yaml']),
        ),
    ],
)
@pytest.mark.now('2019-05-22T00:00:00+00:00')
@pytest.mark.config(
    VGW_API_YT_REQUESTS_SETTINGS={
        'db_rows_ttl_h': 36,
        'limit': 100,
        'get_fwd_by_redirection_phone': {
            'index_optimize_for': 'lookup',
            'force_new_replication': True,
            'new_replication_since': '2019-05-20T00:00:00+00:00',
        },
        'get_fwd_by_ref_id': {
            'index_optimize_for': 'lookup',
            'force_new_replication': True,
            'new_replication_since': '2019-05-20T00:00:00+00:00',
        },
    },
)
async def test_forwarding_get_errors(
        taxi_vgw_api,
        params,
        response_code,
        yt_called,
        mockserver,
        testpoint,
        yt_apply,
):
    @testpoint('yt-get-forwardings')
    def _yt_get_forwardings(data):
        pass

    response = await taxi_vgw_api.get('v1/forwardings', params=params)
    assert response.status_code == response_code
    assert _yt_get_forwardings.times_called == yt_called
    if response_code == 200:
        assert not response.json()


@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_gateway_without_region.sql'])
@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_gateway_without_region(taxi_vgw_api, mockserver):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': '2018-02-25T05:00:00+0300',
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'caller': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'caller_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T02:00:00+00:00'


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T01:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_check_timezone_shift(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': '2018-02-25T06:00:00+0300',
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute('TRUNCATE forwardings.forwardings CASCADE')

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T03:00:00+00:00'
    cursor.execute(
        'SELECT created_at, expires_at FROM forwardings.forwardings',
    )
    result = cursor.fetchall()
    cursor.close()

    assert result[0][0].astimezone(pytz.utc) == datetime.datetime(
        2018, 2, 25, 1, 0, 0, tzinfo=pytz.utc,
    )
    assert result[0][1].astimezone(pytz.utc) == datetime.datetime(
        2018, 2, 25, 3, 0, 0, tzinfo=pytz.utc,
    )

    # Call
    get_response = await taxi_vgw_api.get(
        'v1/forwardings', params={'external_ref_id': '<ref_id>'},
    )

    response_json = get_response.json()
    created_at = dateutil.parser.parse(response_json[0]['created_at'])
    assert created_at.astimezone(pytz.utc) == datetime.datetime(
        2018, 2, 25, 1, 0, 0, tzinfo=pytz.utc,
    )


@mark_vgw_configs()
@pytest.mark.parametrize('external_ref_id_length', [20, 32])
@param_use_vgw_enable_settings()
async def test_forwarding_id(taxi_vgw_api, mockserver, external_ref_id_length):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        requests_bodies = json.loads(request.get_data())
        request_body = requests_bodies[0]
        protocol_forwarding_id = external_ref_id_length * 'x' + '02000000'
        if external_ref_id_length == 32:
            assert request_body['id'] == protocol_forwarding_id
        else:
            assert request_body['id'] != protocol_forwarding_id
        return [{'phone': '+75557775522', 'ext': '007'}]
        # Call

    ref_id = external_ref_id_length * 'x'
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': ref_id,
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200


@mark_vgw_configs()
@pytest.mark.config(VGW_USE_VGW_API=True)
@param_use_vgw_enable_settings()
async def test_forwarding_id_with_config(taxi_vgw_api, mockserver):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        requests_bodies = json.loads(request.get_data())
        request_body = requests_bodies[0]
        assert request_body['id'] != 32 * 'x' + '02000000'
        return [{'phone': '+75557775522', 'ext': '007'}]
        # Call

    ref_id = 32 * 'x'
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': ref_id,
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200


@mark_vgw_configs()
@pytest.mark.parametrize(
    'new_ttl, response_code, final_expires_at',
    [(8000, 400, None), (3600, 200, '2018-02-25T04:00:00+0300')],
)
@pytest.mark.config(VGW_API_FORWARDING_MAX_TTL_SECONDS=7200)
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_ttl_exceeded(
        taxi_vgw_api, mockserver, new_ttl, response_code, final_expires_at,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': final_expires_at,
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': new_ttl,
            'min_ttl': new_ttl,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == response_code


# pylint: disable=invalid-name
@mark_vgw_configs()
@pytest.mark.parametrize(
    'min_ttl, response_code, expected_redirections_call_count, '
    'change_available_gateway',
    [(200, 200, 1, False), (8000, 200, 2, False), (200, 200, 2, True)],
)
@pytest.mark.parametrize('requester_phone', ['+79100000000', None])
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_reuse_forwarding.sql'])
@param_use_vgw_enable_settings()
async def test_forwarding_reuse(
        taxi_vgw_api,
        mockserver,
        min_ttl,
        response_code,
        expected_redirections_call_count,
        change_available_gateway,
        requester_phone,
):

    redirections_call_count = 0

    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        nonlocal redirections_call_count
        redirections_call_count += 1
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': requester_phone,
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 5000,
            'min_ttl': min_ttl,
            'call_location': [37.618423, 55.751244],
        },
    )

    if change_available_gateway:
        params = {'id': 'gateway_id_1'}
        data = {'enabled': False}
        await taxi_vgw_api.put(
            'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
        )
        assert not (
            await taxi_vgw_api.get('v1/voice_gateways/enabled', params=params)
        ).json()['enabled']
        params = {'id': 'gateway_id_2'}
        data = {'enabled': True}
        await taxi_vgw_api.put(
            'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
        )
        assert (
            await taxi_vgw_api.get('v1/voice_gateways/enabled', params=params)
        ).json()['enabled']
        await taxi_vgw_api.invalidate_caches(clean_update=False)

    # Call
    reuse_response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': requester_phone,
            'nonce': '<nonce2>',
            'consumer': 1,
            'new_ttl': 5000,
            'min_ttl': min_ttl,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert reuse_response.status_code == response_code
    assert expected_redirections_call_count == redirections_call_count


@mark_vgw_configs()
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_reuse_forwarding.sql'])
@param_use_vgw_enable_settings()
async def test_forwarding_reuse_draft_error(taxi_vgw_api, mockserver, pgsql):

    redirections_call_count = 0

    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        nonlocal redirections_call_count
        redirections_call_count += 1
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 5000,
            'min_ttl': 100,
            'call_location': [37.618423, 55.751244],
        },
    )

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'UPDATE forwardings.forwardings '
        'SET state = \'draft\', redirection_phone = NULL, '
        'ext = NULL ',
    )
    cursor.close()

    # Call
    reuse_response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce2>',
            'consumer': 1,
            'new_ttl': 5000,
            'min_ttl': 100,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert reuse_response.status_code == 200
    assert redirections_call_count == 2

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '00000000000000000000000000000000',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce4>',
            'consumer': 1,
            'new_ttl': 5000,
            'min_ttl': 100,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 500


@mark_vgw_configs()
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_zero_weight.sql'])
@param_use_vgw_enable_settings()
async def test_forwarding_post_zero_weigth_gateways(taxi_vgw_api, mockserver):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'


@pytest.mark.parametrize(
    ('params', 'response_data'),
    [
        (
            {'external_ref_id': 'ext_ref_id_3', 'consumer_id': 2},
            [
                {
                    'forwarding_id': 'fwd_id_5',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
            ],
        ),
        (
            {'redirection_phone': '+71111111111,777', 'consumer_id': 2},
            [
                {
                    'forwarding_id': 'fwd_id_5',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
            ],
        ),
        (
            {'redirection_phone': '+71111111111', 'consumer_id': 2},
            [
                {
                    'forwarding_id': 'fwd_id_5',
                    'gateway_id': 'gateway_id_2',
                    'state': 'created',
                    'created_at': '2018-02-28T18:11:13+00:00',
                    'requester': 'driver',
                    'callee': 'passenger',
                    'requester_phone_id': '<null>',
                    'callee_phone_id': '<null>',
                    'requester_phone': '+70001112233',
                    'callee_phone': '+79998887766',
                    'phone': '+71111111111',
                    'ext': '777',
                    'external_ref_id': 'ext_ref_id_3',
                    'talks': [],
                },
            ],
        ),
    ],
)
async def test_forwarding_get_by_consumer(taxi_vgw_api, params, response_data):
    response = await taxi_vgw_api.get('v1/forwardings', params=params)
    assert response.status_code == 200
    sorted_forwardings = sorted(
        response.json(), key=lambda k: k['forwarding_id'],
    )
    assert sorted_forwardings == response_data


@mark_vgw_configs()
@pytest.mark.config(VGW_API_FORWARDING_EXPERIMENTS3_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_provider.json')
@pytest.mark.now('2019-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_experiments(taxi_vgw_api, mockserver, pgsql):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Saint petersburg',
            'expire': '2019-04-25T05:00:00+0300',
            'callee': '+79000000000',
            'caller': '+79100000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
        },
    )

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT gateway_id, caller_phone, redirection_phone '
        'FROM forwardings.forwardings '
        'WHERE redirection_phone=\'+75557775522\'',
    )
    result = cursor.fetchall()
    cursor.close()

    assert response.status_code == 200
    assert result[0][0] == 'gateway_id_2'
    assert result[0][1] == '+79100000000'

    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2019-04-25T02:00:00+00:00'


@mark_vgw_configs()
@pytest.mark.config(VGW_API_FORWARDING_EXPERIMENTS3_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_provider.json')
@pytest.mark.now('2019-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_gateway_from_exp_no_pd(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('personal/v1/phones/bulk_store')
    def _personal_phone_retrieve(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
        },
    )

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT gateway_id, caller_phone, redirection_phone '
        'FROM forwardings.forwardings '
        'WHERE redirection_phone=\'+75557775522\'',
    )
    result = cursor.fetchall()
    cursor.close()

    assert response.status_code == 200
    assert result[0][0] == 'gateway_id_2'
    assert result[0][1] == '+79100000000'

    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2019-04-25T02:00:00+00:00'


@pytest.mark.config(
    VGW_API_BLACKLIST_SETTINGS={
        'enabled': True,
        'experiment_name': 'vgw_api_black_listed_phones',
        'consumer': 'vgw-api/blacklisted',
    },
)
@mark_vgw_configs()
@pytest.mark.experiments3(filename='exp3_blacklisted.json')
@pytest.mark.now('2020-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_blacklisted(taxi_vgw_api, mockserver, pgsql):

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
            'check_blacklisted': True,
        },
    )

    assert response.status_code == 400
    response = response.json()
    assert response['code'] == 'PassengerBlackListed'
    assert response['message'] == 'Passenger phone number is blacklisted'

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' external_ref_id, consumer_id,'
        ' caller, callee, caller_phone,'
        ' callee_phone, call_location, region_id, dry_run'
        ' FROM vgw_api.blacklisted_drafts;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == '<ref_id>'
    assert row[1] == 1
    assert row[2] == 'passenger'
    assert row[3] == 'driver'
    assert row[4] == '+79100000000'
    assert row[5] == '+79000000000'
    assert row[6] == '(30.337971,59.933113)'
    assert row[7] == 2
    assert not row[8]


@pytest.mark.config(
    VGW_API_BLACKLIST_SETTINGS={
        'enabled': True,
        'experiment_name': 'vgw_api_black_listed_phones',
        'consumer': 'vgw-api/blacklisted',
    },
)
@mark_vgw_configs()
@pytest.mark.experiments3(filename='exp3_blacklisted_2consumer.json')
@pytest.mark.now('2020-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_blacklisted_2exp3consumers(
        taxi_vgw_api, mockserver, pgsql,
):
    await taxi_vgw_api.tests_control()

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
            'check_blacklisted': True,
        },
    )

    assert response.status_code == 400
    response = response.json()
    assert response['code'] == 'PassengerBlackListed'
    assert response['message'] == 'Passenger phone number is blacklisted'

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' external_ref_id, consumer_id,'
        ' caller, callee, caller_phone,'
        ' callee_phone, call_location, region_id, dry_run'
        ' FROM vgw_api.blacklisted_drafts;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == '<ref_id>'
    assert row[1] == 1
    assert row[2] == 'passenger'
    assert row[3] == 'driver'
    assert row[4] == '+79100000000'
    assert row[5] == '+79000000000'
    assert row[6] == '(30.337971,59.933113)'
    assert row[7] == 2
    assert not row[8]


@pytest.mark.config(
    VGW_API_BLACKLIST_SETTINGS={
        'enabled': True,
        'experiment_name': 'vgw_api_black_listed_phones',
        'consumer': 'vgw-api/blacklisted',
        'dryrun': True,
    },
)
@mark_vgw_configs()
@pytest.mark.experiments3(filename='exp3_blacklisted.json')
@pytest.mark.now('2020-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_blacklisted_dryrun(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    await taxi_vgw_api.tests_control()

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2020-04-25T02:00:00+00:00'

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' external_ref_id, consumer_id,'
        ' caller, callee, caller_phone,'
        ' callee_phone, call_location, region_id, dry_run'
        ' FROM vgw_api.blacklisted_drafts;',
    )
    assert cursor.rowcount == 0


@pytest.mark.config(
    VGW_API_BLACKLIST_SETTINGS={
        'enabled': True,
        'experiment_name': 'vgw_api_black_listed_phones',
        'consumer': 'vgw-api/blacklisted',
        'dryrun': True,
    },
)
@mark_vgw_configs()
@pytest.mark.experiments3(filename='exp3_blacklisted.json')
@pytest.mark.now('2020-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_blacklisted_dryrun_check(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    await taxi_vgw_api.tests_control()

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
            'check_blacklisted': True,
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2020-04-25T02:00:00+00:00'

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' external_ref_id, consumer_id,'
        ' caller, callee, caller_phone,'
        ' callee_phone, call_location, region_id, dry_run'
        ' FROM vgw_api.blacklisted_drafts;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == '<ref_id>'
    assert row[1] == 1
    assert row[2] == 'passenger'
    assert row[3] == 'driver'
    assert row[4] == '+79100000000'
    assert row[5] == '+79000000000'
    assert row[6] == '(30.337971,59.933113)'
    assert row[7] == 2
    assert row[8]


@pytest.mark.config(
    VGW_API_BLACKLIST_SETTINGS={
        'enabled': True,
        'experiment_name': 'vgw_api_black_listed_phones',
        'consumer': 'vgw-api/blacklisted',
        'check_anyway': True,
    },
)
@mark_vgw_configs()
@pytest.mark.experiments3(filename='exp3_blacklisted.json')
@pytest.mark.now('2020-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_blacklisted_check_anyway(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    await taxi_vgw_api.tests_control()

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2020-04-25T02:00:00+00:00'

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' external_ref_id, consumer_id,'
        ' caller, callee, caller_phone,'
        ' callee_phone, call_location, region_id, dry_run'
        ' FROM vgw_api.blacklisted_drafts;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == '<ref_id>'
    assert row[1] == 1
    assert row[2] == 'passenger'
    assert row[3] == 'driver'
    assert row[4] == '+79100000000'
    assert row[5] == '+79000000000'
    assert row[6] == '(30.337971,59.933113)'
    assert row[7] == 2
    assert row[8]


@pytest.mark.config(
    VGW_API_BLACKLIST_SETTINGS={
        'enabled': True,
        'experiment_name': 'vgw_api_black_listed_phones',
        'consumer': 'vgw-api/blacklisted',
    },
)
@mark_vgw_configs()
@pytest.mark.experiments3(filename='exp3_blacklisted.json')
@pytest.mark.now('2020-04-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_blacklisted_no_personal(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('personal/v1/phones/bulk_store')
    def _personal_phone_retrieve(request):
        return mockserver.make_response('', 500)

    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    await taxi_vgw_api.tests_control()

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [30.337971, 59.933113],
            'service_level': 'econom',
            'check_blacklisted': True,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2020-04-25T02:00:00+00:00'

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' external_ref_id, consumer_id,'
        ' caller, callee, caller_phone,'
        ' callee_phone, call_location, region_id, dry_run'
        ' FROM vgw_api.blacklisted_drafts;',
    )
    assert cursor.rowcount == 0


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_no_requester_phone(taxi_vgw_api, mockserver):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_requests = json.loads(request.get_data())
        assert len(body_requests) == 1
        body_request = body_requests[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': '2018-02-25T05:00:00+0300',
            'callee': '+79000000000',
            'for': 'mobile',
        }
        return [{'phone': '+75557775522', 'ext': '007'}]

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+75557775522'
    assert response_json['ext'] == '007'
    assert response_json['expires_at'] == '2018-02-25T02:00:00+00:00'

    response = await taxi_vgw_api.get(
        'v1/forwardings', params={'external_ref_id': '<ref_id>'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    del response_json[0]['forwarding_id']
    assert response_json == [
        {
            'external_ref_id': '<ref_id>',
            'gateway_id': 'gateway_id_1',
            'state': 'created',
            'created_at': '2018-02-25T00:00:00+00:00',
            'requester': 'passenger',
            'callee': 'driver',
            'phone': '+75557775522',
            'ext': '007',
            'requester_phone_id': '<null>',
            'callee_phone_id': 'id-+79000000000',
            'requester_phone': '<null>',
            'callee_phone': '+79000000000',
            'talks': [],
        },
    ]


@mark_vgw_configs()
@param_use_vgw_enable_settings()
async def test_forwarding_non_json_response(taxi_vgw_api, mockserver):
    @mockserver.handler('/redirections')
    def _mock_redirections(request):
        return mockserver.make_response(
            response='Whoops!', status=200, content_type='application/json',
        )

    # Call
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone': '+79000000000',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == 500
    response_json = response.json()
    assert (
        response_json['message']
        == 'JSON parse error at line 1 column 1: Invalid value.'
    )


@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
@pytest.mark.parametrize(
    [
        'consumer_id',
        'requester',
        'callee',
        'phone_pool_name',
        'expected_status',
    ],
    (
        pytest.param(
            1, 'passenger', 'driver', 'mobile', 200, id='consumer 1 settings',
        ),
        pytest.param(
            1, 'driver', 'passenger', None, 400, id='consumer 1 unknown type',
        ),
        pytest.param(
            2,
            'passenger',
            'driver',
            'default_mobile',
            200,
            id='default settings mobile',
        ),
        pytest.param(
            2,
            'driver',
            'passenger',
            'default_driver',
            200,
            id='default settings driver',
        ),
    ),
)
@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_CONSUMER_CLIENT_TYPE_MAP={
        '__default__': {
            'forwarding_types': [
                {
                    'src_type': 'driver',
                    'dst_type': 'passenger',
                    'phone_pool_name': 'default_driver',
                },
                {
                    'src_type': 'passenger',
                    'dst_type': 'driver',
                    'phone_pool_name': 'default_mobile',
                },
            ],
        },
        '1': {
            'forwarding_types': [
                {
                    'src_type': 'passenger',
                    'dst_type': 'driver',
                    'phone_pool_name': 'mobile',
                },
            ],
        },
    },
)
async def test_forwarding_post_client_types(
        taxi_vgw_api,
        mockserver,
        pgsql,
        consumer_id,
        requester,
        callee,
        phone_pool_name,
        expected_status,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        body_requests = json.loads(request.get_data())
        assert body_requests[0]['for'] == phone_pool_name
        return [{'phone': '+75557775522', 'ext': '007'}]

    if consumer_id == 2:
        response = await taxi_vgw_api.put(
            'v1/consumers/enabled', params={'id': 2}, json={'enabled': True},
        )
        assert response.status_code == 200
        await taxi_vgw_api.invalidate_caches()

    order_id = '14444-44444'  # len(order_id) != 32
    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': order_id,
            'requester': requester,
            'callee': callee,
            'callee_phone': '+79000000000',
            'requester_phone': '+79100000000',
            'nonce': '<nonce>',
            'consumer': consumer_id,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.618423, 55.751244],
        },
    )
    assert response.status_code == expected_status


@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_CONSUMER_CLIENT_TYPE_MAP={
        '__default__': {
            'forwarding_types': [
                {
                    'src_type': 'passenger',
                    'dst_type': 'driver',
                    'phone_pool_name': 'mobile',
                },
                {
                    'src_type': 'passenger',
                    'dst_type': 'passenger',
                    'phone_pool_name': 'driver',
                },
                {
                    'src_type': 'passenger',
                    'dst_type': 'dispatcher',
                    'phone_pool_name': 'driver',
                },
                {
                    'src_type': 'driver',
                    'dst_type': 'driver',
                    'phone_pool_name': 'mobile',
                },
                {
                    'src_type': 'driver',
                    'dst_type': 'passenger',
                    'phone_pool_name': 'driver',
                },
                {
                    'src_type': 'driver',
                    'dst_type': 'dispatcher',
                    'phone_pool_name': 'mobile',
                },
                {
                    'src_type': 'dispatcher',
                    'dst_type': 'driver',
                    'phone_pool_name': 'mobile',
                },
                {
                    'src_type': 'dispatcher',
                    'dst_type': 'passenger',
                    'phone_pool_name': 'driver',
                },
                {
                    'src_type': 'dispatcher',
                    'dst_type': 'dispatcher',
                    'phone_pool_name': 'mobile',
                },
            ],
        },
    },
)
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_all_client_types(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    order_id = 'b8b6152f9da92921b1edf8061af63376'  # len(order_id) == 32
    client_types = ['driver', 'passenger', 'dispatcher']
    forwardings_types = [
        (requester, callee)
        for requester in client_types
        for callee in client_types
    ]
    for i, (requester, callee) in enumerate(forwardings_types):
        response = await taxi_vgw_api.post(
            'v1/forwardings',
            {
                'external_ref_id': order_id,
                'requester': requester,
                'callee': callee,
                'callee_phone': '+79000000000',
                'requester_phone': '+79100000000',
                'nonce': f'<nonce_{i}>',
                'consumer': 1,
                'new_ttl': 7200,
                'min_ttl': 7200,
                'call_location': [37.618423, 55.751244],
            },
        )
        assert response.status_code == 200

    # check that forwarding_id is not random
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT 1 '
        'FROM forwardings.forwardings '
        f'  WHERE id LIKE \'{order_id}%000000\'',
    )
    assert cursor.rowcount == 9
    cursor.close()


@mark_vgw_configs()
@pytest.mark.now('2018-02-25T00:00:00')
@param_use_vgw_enable_settings()
async def test_forwarding_post_statistics(
        taxi_vgw_api, mockserver, statistics,
):
    quota = 10

    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        nonlocal quota
        if quota > 0:
            quota -= 1
            return [{'phone': '+75557775522', 'ext': '007'}]
        return mockserver.make_response(status=500)

    async with statistics.capture(taxi_vgw_api) as capture:
        for i in range(7):
            for requester, callee in [
                    ('driver', 'passenger'),
                    ('passenger', 'driver'),
                    ('dispatcher', 'passenger'),
            ]:
                await taxi_vgw_api.post(
                    'v1/forwardings',
                    {
                        'external_ref_id': f'ref_id_{i}',
                        'requester': requester,
                        'callee': callee,
                        'callee_phone': '+79000000000',
                        'requester_phone': '+79100000000',
                        'nonce': f'nonce_{i}_{requester}',
                        'consumer': 1,
                        'new_ttl': 7200,
                        'min_ttl': 7200,
                        'call_location': [37.618423, 55.751244],
                    },
                )

    expected_statistics = {
        'gateway.gateway_id_1.handle.redirections.post.error': 11,
        'gateway.gateway_id_1.handle.redirections.post.ok': 10,
        'forwardings.created.gateway.gateway_id_1.region.1': 10,
        'forwardings.created.type.driver_to_passenger': 4,
        'forwardings.created.type.passenger_to_driver': 3,
        'forwardings.created.type.dispatcher_to_passenger': 3,
    }
    for key, value in expected_statistics.items():
        assert capture.statistics[key] == value
