import datetime

import pytest


ORDER_ID = '9b0ef3c5398b3e07b59f03110563479d'
USER_ID = '10d258597b033d1b0560056b4a42b930'
PHONE_ID = '5ae3312c3057e155f7e46995'


def _update_order(mongodb, orderid, order_status, order_taxi_status):
    mongodb.order_proc.update(
        {'_id': orderid},
        {
            '$set': {
                'order.status': order_status,
                'order.taxi_status': order_taxi_status,
            },
        },
    )


@pytest.mark.parametrize(
    'order_status,order_taxi_status,expected_status',
    [
        ('assigned', None, 'driving'),
        ('assigned', 'driving', 'driving'),
        ('assigned', 'waiting', 'waiting'),
        ('assigned', 'transporting', 'transporting'),
        ('assigned', 'complete', 'complete'),
        ('assigned', 'failed', 'failed'),
        ('assigned', 'cancelled', 'cancelled'),
        ('assigned', 'preexpired', 'preexpired'),
        ('assigned', 'expired', 'expired'),
        ('pending', None, 'search'),
        ('pending', 'driving', 'search'),
        ('pending', 'waiting', 'search'),
        ('pending', 'transporting', 'search'),
        ('pending', 'complete', 'search'),
        ('pending', 'failed', 'search'),
        ('pending', 'cancelled', 'search'),
        ('pending', 'preexpired', 'search'),
        ('pending', 'expired', 'search'),
    ],
)
async def test_active_orders_basic(
        taxi_order_core,
        mongodb,
        order_status,
        order_taxi_status,
        expected_status,
):
    _update_order(mongodb, ORDER_ID, order_status, order_taxi_status)
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {
        'orders': [
            {
                'due': '2019-09-10T03:30:00+0000',
                'orderid': ORDER_ID,
                'pending_changes': [
                    {
                        'change_id': '5860cf1419d24c4e99f5ecc83709cca6',
                        'name': 'user_ready',
                        'status': 'pending',
                    },
                    {
                        'change_id': 'd455b7ecff6f4c51830253131fdab98f',
                        'name': 'user_ready',
                        'status': 'processing',
                    },
                ],
                'service_level': 17,
                'status': expected_status,
            },
        ],
    }


async def test_active_orders_multiple(taxi_order_core, mongodb):
    orderid_1 = ORDER_ID
    orderid_2 = '8b0ef3c5398b3e07b59f03110563479d'
    _update_order(mongodb, orderid_1, 'pending', 'driving')
    _update_order(mongodb, orderid_2, 'assigned', 'expired')
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response['orders']) == 2
    status_0 = response['orders'][0]['status']
    status_1 = response['orders'][1]['status']
    assert set((status_0, status_1)) == set(('search', 'expired'))


@pytest.mark.parametrize('order_status', ['draft', 'finished', 'cancelled'])
async def test_active_orders_not_found_by_status(
        taxi_order_core, mongodb, order_status,
):
    mongodb.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.status': order_status}},
    )
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {'orders': []}


@pytest.mark.parametrize('crossdevice_enabled', [True, False])
@pytest.mark.parametrize('use_user_id', [True, False])
@pytest.mark.parametrize('use_yandex_uid', [True, False])
async def test_active_orders_yandex_uid(
        taxi_order_core,
        mongodb,
        taxi_config,
        crossdevice_enabled,
        use_user_id,
        use_yandex_uid,
):
    x_yandex_uid = '243469005'
    taxi_config.set(CROSSDEVICE_ENABLED=crossdevice_enabled)
    _update_order(mongodb, ORDER_ID, 'pending', 'driving')

    query_params = {'phone_id': PHONE_ID}
    if use_user_id:
        query_params['userid'] = USER_ID

    header_params = {}
    if use_yandex_uid:
        header_params['X-Yandex-UID'] = x_yandex_uid

    response = await taxi_order_core.get(
        '/v1/tc/active-orders', params=query_params, headers=header_params,
    )

    if use_user_id or crossdevice_enabled and use_yandex_uid:
        assert response.status_code == 200
        response = response.json()
        assert len(response['orders']) == 1
    else:
        assert response.status_code == 400


async def test_active_orders_code_dispatch(taxi_order_core, mongodb):
    mongodb.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'extra_data.code_dispatch.code': '716\u2013081',
                'order.status': 'assigned',
                'order.taxi_status': 'driving',
            },
        },
    )
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response['orders']) == 1
    assert response == {
        'orders': [
            {
                'due': '2019-09-10T03:30:00+0000',
                'orderid': ORDER_ID,
                'pending_changes': [
                    {
                        'change_id': '5860cf1419d24c4e99f5ecc83709cca6',
                        'name': 'user_ready',
                        'status': 'pending',
                    },
                    {
                        'change_id': 'd455b7ecff6f4c51830253131fdab98f',
                        'name': 'user_ready',
                        'status': 'processing',
                    },
                ],
                'service_level': 17,
                'status': 'boarding',
            },
        ],
    }


async def test_active_orders_reorder(taxi_order_core, mongodb):
    reorder_id = '0b0ef3c5398b3e07b59f03110563479d'
    _update_order(mongodb, ORDER_ID, 'assigned', 'driving')
    mongodb.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.status': 'assigned',
                'order.taxi_status': 'driving',
                'reorder.id': reorder_id,
            },
        },
    )
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['orders'][0]['orderid'] == reorder_id


@pytest.mark.parametrize(
    'unset_obj,key,new_val',
    [
        ({'changes': ''}, 'pending_changes', []),
        ({'changes.objects': ''}, 'pending_changes', []),
        ({'extra_data': ''}, '', ''),
        ({'extra_data.code_dispatch': ''}, '', ''),
        ({'reorder': ''}, '', ''),
        ({'reorder.id': ''}, '', ''),
        ({'order.request.service_level': ''}, 'service_level', 0),
    ],
)
async def test_active_orders_no_optional_fields(
        taxi_order_core, mongodb, unset_obj, key, new_val,
):
    mongodb.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.status': 'assigned', 'order.taxi_status': 'driving'}},
    )
    mongodb.order_proc.update({'_id': ORDER_ID}, {'$unset': unset_obj})
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    expected_order = {
        'due': '2019-09-10T03:30:00+0000',
        'orderid': ORDER_ID,
        'pending_changes': [
            {
                'change_id': '5860cf1419d24c4e99f5ecc83709cca6',
                'name': 'user_ready',
                'status': 'pending',
            },
            {
                'change_id': 'd455b7ecff6f4c51830253131fdab98f',
                'name': 'user_ready',
                'status': 'processing',
            },
        ],
        'service_level': 17,
        'status': 'driving',
    }
    if key:
        expected_order[key] = new_val
    assert response['orders'][0] == expected_order


async def test_active_orders_multiorder(taxi_order_core, mongodb):
    orderid_1 = ORDER_ID
    orderid_2 = '8b0ef3c5398b3e07b59f03110563479d'
    orderid_3 = '7b0ef3c5398b3e07b59f03110563479d'
    _update_order(mongodb, orderid_1, 'assigned', 'driving')
    _update_order(mongodb, orderid_2, 'assigned', 'driving')
    _update_order(mongodb, orderid_3, 'assigned', 'driving')
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={
            'userid': USER_ID,
            'phone_id': PHONE_ID,
            'is_multiorder': True,
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response['orders']) == 3
    assert response['orders_state']
    # Order is important! Orders are sorted by 'order.created', ascending
    assert response['orders_state'] == {
        'orders': [
            {
                'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                'status': 'driving',
            },
            {
                'orderid': '7b0ef3c5398b3e07b59f03110563479d',
                'status': 'driving',
            },
            {
                'orderid': '8b0ef3c5398b3e07b59f03110563479d',
                'status': 'driving',
            },
        ],
    }


@pytest.mark.parametrize(
    'filter_enabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                ORDER_CORE_ORDER_SOURCES_TO_FILTER=['other_one'],
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ORDER_CORE_ORDER_SOURCES_TO_FILTER=['cargo'],
            ),
        ),
    ],
)
async def test_active_orders_filter_cargo(
        taxi_order_core, mongodb, filter_enabled,
):
    _update_order(mongodb, ORDER_ID, 'assigned', 'driving')
    mongodb.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.source': 'cargo'}},
    )
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    if filter_enabled:
        assert not response['orders']
    else:
        assert response['orders']


@pytest.mark.config(ORDER_CORE_ORDER_SOURCES_TO_FILTER=['cargo'])
async def test_active_orders_with_filter(taxi_order_core, mongodb):
    _update_order(mongodb, ORDER_ID, 'assigned', 'driving')
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={'userid': USER_ID, 'phone_id': PHONE_ID},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['orders']


@pytest.mark.parametrize(
    'check_in_order_proc_state, order_status, '
    'allow_check_in_status, expected_status',
    [
        # case 1: happy path
        ({'check_in_time': None}, 'pending', True, 'check_in'),
        # case 2: already checked-in
        (
            {'check_in_time': datetime.datetime(2020, 7, 7, 0, 0, 0)},
            'pending',
            True,
            'search',
        ),
        # case 3: not check-in order
        (None, 'pending', True, 'search'),
        # case 4: not in search state
        ({'check_in_time': None}, 'assigned', True, 'driving'),
        # case 5: check_in state adjusting is not enabled
        ({'check_in_time': None}, 'pending', False, 'search'),
    ],
)
async def test_active_orders_check_in(
        taxi_order_core,
        mongodb,
        check_in_order_proc_state,
        order_status,
        allow_check_in_status,
        expected_status,
):
    mongodb.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'dispatch_check_in': check_in_order_proc_state,
                'order.status': order_status,
                'order.taxi_status': None,
            },
        },
    )
    response = await taxi_order_core.get(
        '/v1/tc/active-orders',
        params={
            'userid': USER_ID,
            'phone_id': PHONE_ID,
            'allow_check_in_status': allow_check_in_status,
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response['orders']) == 1
    assert response == {
        'orders': [
            {
                'due': '2019-09-10T03:30:00+0000',
                'orderid': ORDER_ID,
                'pending_changes': [
                    {
                        'change_id': '5860cf1419d24c4e99f5ecc83709cca6',
                        'name': 'user_ready',
                        'status': 'pending',
                    },
                    {
                        'change_id': 'd455b7ecff6f4c51830253131fdab98f',
                        'name': 'user_ready',
                        'status': 'processing',
                    },
                ],
                'service_level': 17,
                'status': expected_status,
            },
        ],
    }
