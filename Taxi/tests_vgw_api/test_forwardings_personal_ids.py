import pytest


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


@mark_vgw_configs()
@pytest.mark.now('2020-04-25T00:00:00')
async def test_post_forwardings_personal(taxi_vgw_api, mockserver, pgsql):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

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
            'call_location': [37.3224, 55.4447],
            'service_level': 'econom',
        },
    )

    assert response.status_code == 200
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' caller_phone_id, callee_phone_id'
        ' FROM forwardings.forwardings '
        'WHERE external_ref_id=\'<ref_id>\';',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == 'id-+79100000000'
    assert row[1] == 'id-+79000000000'


@mark_vgw_configs()
@pytest.mark.now('2020-04-25T00:00:00')
async def test_post_forwardings_personal_empty(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    @mockserver.json_handler('personal/v1/phones/bulk_store')
    def _personal_phone_retrieve(request):
        return {'items': []}

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
            'call_location': [37.3224, 55.4447],
            'service_level': 'econom',
        },
    )

    assert response.status_code == 200
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' caller_phone_id, callee_phone_id'
        ' FROM forwardings.forwardings '
        'WHERE external_ref_id=\'<ref_id>\';',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert not row[0]
    assert not row[1]


@mark_vgw_configs()
@pytest.mark.now('2020-04-25T00:00:00')
async def test_post_forwardings_personal_error(
        taxi_vgw_api, mockserver, pgsql,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    @mockserver.json_handler('personal/v1/phones/bulk_store')
    def _personal_phone_retrieve(request):
        return mockserver.make_response('', 500)

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
            'call_location': [37.3224, 55.4447],
            'service_level': 'econom',
        },
    )

    assert response.status_code == 200
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' caller_phone_id, callee_phone_id'
        ' FROM forwardings.forwardings '
        'WHERE external_ref_id=\'<ref_id>\';',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert not row[0]
    assert not row[1]


@pytest.mark.config(VGW_API_RETURN_REAL_PHONE_NUMBERS=True)
@mark_vgw_configs()
@pytest.mark.now('2020-04-25T00:00:00')
async def test_get_forwardings_with_pd_id(taxi_vgw_api, mockserver, pgsql):
    response = await taxi_vgw_api.get(
        'v1/forwardings', params={'external_ref_id': 'ext_ref_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'callee': 'passenger',
            'callee_phone': '+79998887766',
            'callee_phone_id': 'id-+79998887766',
            'created_at': '2018-02-26T16:00:00+00:00',
            'external_ref_id': 'ext_ref_id_1',
            'forwarding_id': 'fwd_id_1',
            'gateway_id': 'gateway_id_1',
            'phone': '+71111111111',
            'ext': '888',
            'requester': 'driver',
            'requester_phone': '+70001112233',
            'requester_phone_id': 'id-+70001112233',
            'state': 'created',
            'talks': [
                {
                    'caller_phone': '+79000000000',
                    'caller_phone_id': 'id-+79000000000',
                    'id': 'talk_id_1',
                    'length': 10,
                    'started_at': '2018-02-26T16:11:13+00:00',
                },
            ],
        },
    ]


@pytest.mark.config(VGW_API_RETURN_REAL_PHONE_NUMBERS=False)
@mark_vgw_configs()
@pytest.mark.now('2020-04-25T00:00:00')
async def test_get_forwardings_pd_id_only(taxi_vgw_api, mockserver, pgsql):
    response = await taxi_vgw_api.get(
        'v1/forwardings', params={'external_ref_id': 'ext_ref_id_1'},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'callee': 'passenger',
            'callee_phone_id': 'id-+79998887766',
            'created_at': '2018-02-26T16:00:00+00:00',
            'external_ref_id': 'ext_ref_id_1',
            'forwarding_id': 'fwd_id_1',
            'gateway_id': 'gateway_id_1',
            'phone': '+71111111111',
            'ext': '888',
            'requester': 'driver',
            'requester_phone_id': 'id-+70001112233',
            'state': 'created',
            'talks': [
                {
                    'caller_phone_id': 'id-+79000000000',
                    'id': 'talk_id_1',
                    'length': 10,
                    'started_at': '2018-02-26T16:11:13+00:00',
                },
            ],
        },
    ]


@mark_vgw_configs()
@pytest.mark.now('2020-04-25T00:00:00')
async def test_post_forwardings_with_personal(taxi_vgw_api, mockserver, pgsql):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [{'phone': '+75557775522', 'ext': '007'}]

    @mockserver.json_handler('personal/v1/phones/bulk_retrieve')
    def _personal_phone_retrieve(request):
        return {
            'items': [
                {'id': 'random_id_1', 'value': '+79998887766'},
                {'id': 'random_id_2', 'value': '+70001112233'},
            ],
        }

    response = await taxi_vgw_api.post(
        'v1/forwardings',
        {
            'external_ref_id': '<ref_id>',
            'requester': 'passenger',
            'callee': 'driver',
            'callee_phone_id': 'random_id_1',
            'requester_phone_id': 'random_id_2',
            'nonce': '<nonce>',
            'consumer': 1,
            'new_ttl': 7200,
            'min_ttl': 7200,
            'call_location': [37.3224, 55.4447],
            'service_level': 'econom',
        },
    )

    assert response.status_code == 200
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        ' caller_phone, callee_phone'
        ' FROM forwardings.forwardings '
        'WHERE external_ref_id=\'<ref_id>\';',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == '+70001112233'
    assert row[1] == '+79998887766'
