import json

import pytest


@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
    VGW_API_FORWARDING_MAX_TTL_SECONDS=90000,
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
@pytest.mark.now('2022-02-25T00:00:00')
async def test_forwarding_state_post(taxi_vgw_api, mockserver, pgsql):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        body_request = json.loads(request.get_data())[0]
        body_request.pop('id')
        assert body_request == {
            'city': 'Moscow',
            'expire': '2022-02-25T05:00:00+0300',
            'caller': '+70001110001',
            'callee': '+79991110001',
            'for': 'driver',
        }
        return [{'phone': '+79999999999', 'ext': '123'}]

    # Check forwarding is reused
    request_body = {
        'external_ref_id': 'ext_ref_id_1',
        'requester': 'driver',
        'callee': 'passenger',
        'requester_phone': '+70001110001',
        'callee_phone': '+79991110001',
        'nonce': 'new_nonce',
        'consumer': 1,
        'new_ttl': 7200,
        'min_ttl': 10,
        'call_location': [37.618423, 55.751244],
    }
    response = await taxi_vgw_api.post('/v1/forwardings', request_body)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+71111111111'
    assert response_json['ext'] == '111'
    assert response_json['expires_at'] == '2222-02-26T16:11:13+00:00'

    # Set forwarding broken
    response = await taxi_vgw_api.post(
        '/v1/forwardings/state',
        {
            'filter': {'redirection_phones': ['+71111111111', '+72222222222']},
            'state': 'broken',
        },
    )
    assert response.status_code == 200

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT state '
        'FROM forwardings.forwardings '
        'WHERE redirection_phone=\'+71111111111\' '
        'ORDER BY id',
    )
    result = cursor.fetchall()
    cursor.close()
    assert [row[0] for row in result] == ['broken', 'created', 'draft']

    # Now new forwarding should be created
    response = await taxi_vgw_api.post('/v1/forwardings', request_body)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['phone'] == '+79999999999'
    assert response_json['ext'] == '123'
    assert response_json['expires_at'] == '2022-02-25T02:00:00+00:00'
