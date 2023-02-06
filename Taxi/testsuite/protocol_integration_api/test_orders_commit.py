import datetime
import json

import pytest

from taxi_tests import utils

COMMON_USER_ID = 'good'


CC_HEADERS = {'User-Agent': 'call_center'}


PARTNER_ORDERS_API_TVM_TICKET = (
    '3:serv:CBAQ__________9_IgQIexAX:Pz6rEHFgRT2AO2zGiBtmM63-k1uQW7aszfGy6l7d'
    'VPk8DhhM6WBIAlGRdZUIVP8rG5STuXkS6fFq_x7pYzgYEHRa9i2ak-8Q0R1cQerNtgpjTfZe6'
    'q7hoRIUpk6RUZhQkGLFSHZARzsSDgvnIDnk_K6sBMAdOHTWGdV6evyOqEs'
)

OTHER_SERVICE_TVM_TICKET = (
    '3:serv:CBAQ__________9_IgUIlAEQFw:PH8b7-4r_Ush8d5ie-x2tklJtQtjSS5CFrWol4x'
    'd_xU0pmnCq28mQP8QxCOxQ8piw8cGco5hBma3kP73Z0Hg0yyzblhvpkfnpMKOMZYr7CRNao3F'
    'Ul_juY8IqfYtQUCkPHrw0Ebyw6UO9rvzyqFAnNe88AfQqDT-lGjqOVwPNLg'
)


@pytest.fixture
def ordercommit_services(mockserver, load_binary):
    class context:
        surge_value = 1
        experiments = ['fixed_price', 'forced_surge']
        client = {
            'name': 'iphone',
            'version': [3, 61, 4830],
            'platform_version': [10, 1, 1],
        }
        payment_type = 'cash'
        user_id = COMMON_USER_ID
        orders_complete = 83

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route.protobuf'),
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        data = json.loads(request.get_data())
        assert data['user_id'] == context.user_id
        assert data['payment_type'] == context.payment_type
        assert data['tariffs'] == ['econom']
        assert data['experiments'] == context.experiments
        assert data['client'] == context.client
        assert data['orders_complete'] == context.orders_complete
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': context.surge_value,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    return context


MAX_CALLCENTER_ORDERS = 'MAX_CALLCENTER_ORDERS'
MAX_UNFINISHED_ORDERS = 'MAX_UNFINISHED_ORDERS'
INTEGRATION_ORDER_LIMIT_PER_USER = 'INTEGRATION_ORDER_LIMIT_PER_USER'
MAX_CONCURRENT_CARD_ORDERS = 'MAX_CONCURRENT_CARD_ORDERS'
VGW_DRIVER_VOICE_FORWARDING_SOURCES = 'VGW_DRIVER_VOICE_FORWARDING_SOURCES'


def check_support_commit(order_id, order_config_commit, mock_stq_agent):

    support_commit_tasks = mock_stq_agent.get_tasks('support_commit')
    ids = set([t.id for t in support_commit_tasks])
    assert len(ids) == 1

    support_commit = support_commit_tasks[0]
    assert support_commit.id == order_id

    (
        first_order_id,
        log_extra,
        second_order_id,
        force_coupon,
        max_orders_per_phone,
        max_orders_per_device,
        max_unpaid_orders,
    ) = support_commit.args

    assert first_order_id == order_id
    assert 'log_extra' in log_extra
    assert second_order_id == order_id
    assert force_coupon is True

    # check for config keys in protocol/lib/src/orderkit/check_limits.cpp
    # with order_creator_type == OrderCreatorType::INTEGRATION_API
    assert max_orders_per_phone == order_config_commit[MAX_UNFINISHED_ORDERS]
    assert (
        max_orders_per_device
        == order_config_commit[INTEGRATION_ORDER_LIMIT_PER_USER]
    )
    assert max_unpaid_orders == order_config_commit[MAX_CONCURRENT_CARD_ORDERS]

    assert 'log_extra' in support_commit.kwargs
    assert support_commit.is_postponed


def check_processing(order_id, mock_stq_agent):
    tasks = mock_stq_agent.get_tasks('processing')
    ids = set(task.id for task in tasks)
    assert len(ids) == 0


def check_created_order_in_stq(order_id, mock_stq_agent, cfg):
    check_support_commit(order_id, cfg, mock_stq_agent)
    check_processing(order_id, mock_stq_agent)


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
def test_ordercommit_is_idempotent(
        taxi_integration,
        ordercommit_services,
        mock_stq_agent,
        config,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    # setting some values to check they have been stored
    order_commit_config = {
        MAX_CALLCENTER_ORDERS: 5,
        MAX_UNFINISHED_ORDERS: 6,
        INTEGRATION_ORDER_LIMIT_PER_USER: 7,
        MAX_CONCURRENT_CARD_ORDERS: 1,
    }
    config.set_values(order_commit_config)

    order_id = 'good'
    req = {
        'userid': COMMON_USER_ID,
        'orderid': order_id,
        'chainid': 'chainid_1',
    }

    # at least some experiment must be set
    ordercommit_services.experiments = ['forced_surge']

    # checking several same requests with support commit in stq
    for _ in range(2):
        resp = taxi_integration.post(
            'v1/orders/commit', req, headers=CC_HEADERS,
        )
        assert resp.status_code == 200
        assert resp.json()['orderid'] == order_id
        assert resp.json()['status'] == 'search'
        check_created_order_in_stq(
            order_id, mock_stq_agent, order_commit_config,
        )


@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
@pytest.mark.config(
    FORCED_REQUIREMENTS={'__default__': {'econom': {'yellowcarnumber': True}}},
)
def test_ordercommit_courier(
        taxi_integration,
        ordercommit_services,
        mock_stq_agent,
        db,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'good'
    req = {
        'userid': COMMON_USER_ID,
        'orderid': order_id,
        'chainid': 'chainid_1',
    }
    ordercommit_services.experiments = ['forced_surge']
    resp = taxi_integration.post('v1/orders/commit', req, headers=CC_HEADERS)
    assert resp.status_code == 200, resp.text
    order_proc = db.order_proc.find_one({'_id': order_id})
    assert order_proc['order']['request']['requirements'] == {
        'yellowcarnumber': True,
    }


@pytest.mark.parametrize(
    'sourceid,code,source_enabled',
    [('alice', 200, True), ('alice', 200, False)],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
def test_vgw(
        taxi_integration,
        ordercommit_services,
        db,
        config,
        sourceid,
        code,
        source_enabled,
        pricing_data_preparer,
):
    """
    Check vwg for sourceid in request for int-api.
    Cannot check vwg for sourceids which set in user_agent (protocol).
    """

    pricing_data_preparer.set_locale('ru')

    source = [sourceid] if source_enabled else []
    vgw_config = {VGW_DRIVER_VOICE_FORWARDING_SOURCES: source}
    config.set_values(vgw_config)

    userid = COMMON_USER_ID
    order_id = 'good'
    db.users.update({'_id': userid}, {'$set': {'sourceid': sourceid}})
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.source': sourceid}},
    )

    ordercommit_services.orders_complete = 0
    phone_id = db.users.find_one({'_id': userid})['phone_id']
    db.user_phones.update({'_id': phone_id}, {'$set': {'stat.complete': 0}})

    request = {
        'userid': userid,
        'orderid': order_id,
        'sourceid': sourceid,
        'chainid': 'chainid_1',
    }

    ordercommit_services.experiments = ['forced_surge']

    response = taxi_integration.post('v1/orders/commit', request)
    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data['orderid'] == order_id
        order = db.order_proc.find_one({'_id': order_id})
        assert order['fwd_driver_phone'] == source_enabled


@pytest.mark.parametrize(
    'callback',
    [
        (
            {
                'data': 'alice_callback',
                'notify_on': ['on_assigned', 'on_waiting'],
            }
        ),
        ({'data': 'alice_callback', 'notify_on': []}),
        ({'data': 'alice_callback'}),
    ],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.order_experiments('forced_surge')
def test_callback(
        taxi_integration,
        ordercommit_services,
        db,
        config,
        callback,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    order_id = 'good'
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.callback': callback}},
    )

    order_commit_config = {
        MAX_UNFINISHED_ORDERS: 6,
        INTEGRATION_ORDER_LIMIT_PER_USER: 7,
        MAX_CONCURRENT_CARD_ORDERS: 8,
    }
    config.set_values(order_commit_config)

    userid = COMMON_USER_ID

    sourceid = 'alice'
    db.users.update({'_id': userid}, {'$set': {'sourceid': sourceid}})
    request = {
        'userid': userid,
        'orderid': order_id,
        'sourceid': sourceid,
        'chainid': 'chainid_1',
    }

    # at least some experiment must be set
    ordercommit_services.experiments = ['forced_surge']

    response = taxi_integration.post('v1/orders/commit', request)
    assert response.status_code == 200, response

    order = db.orders.find_one({'_id': order_id})
    assert order is None

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc is not None
    assert proc['order']['callback'] == callback


@pytest.mark.parametrize(
    'order_id,surge_value,expected_code',
    [
        ('surge_12', 1.2, 200),
        ('surge_12', 1.1, 200),
        ('surge_12', 1.3, 200),
        ('surge_12_future', 1.3, 406),
        ('agent_order_wo_offer', 2.1, 200),
        ('agent_delayed_order_wo_offer', 2.1, 200),
    ],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'check_forced_surge_cpp',
    'calc_info_cpp',
    'get_experiments_cpp',
    'ordercommit_cpp_full',
)
@pytest.mark.order_experiments('forced_surge')
def test_ordercommit_forced_surge(
        taxi_integration,
        ordercommit_services,
        order_id,
        surge_value,
        expected_code,
        db,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    ordercommit_services.client = {
        'name': 'iphone',
        'version': [3, 61, 4830],
        'platform_version': [10, 1, 1],
    }
    ordercommit_services.surge_value = surge_value
    ordercommit_services.experiments = ['forced_surge']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={
            'userid': COMMON_USER_ID,
            'orderid': order_id,
            'chainid': 'chainid_1',
        },
        headers=CC_HEADERS,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'order_id,expected_code',
    [('fixed_price_0', 200), ('fixed_price_1_offer_deleted', 406)],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'fixed_price_cpp',
    'calc_info_cpp',
    'get_experiments_cpp',
    'ordercommit_cpp_full',
)
@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_fixed_price(
        taxi_integration,
        ordercommit_services,
        db,
        order_id,
        expected_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={'userid': COMMON_USER_ID, 'orderid': order_id},
        headers=CC_HEADERS,
    )
    assert response.status_code == expected_code


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'integration_orders_commit': {
            'use_afs': True,
            'retries': 1,
            'timeout': 100,
        },
    },
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'fixed_price_cpp',
    'calc_info_cpp',
    'get_experiments_cpp',
    'ordercommit_cpp_full',
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_fixed_price_blocked_user(
        taxi_integration, ordercommit_services, mockserver, now,
):
    _ORDER_ID = 'fixed_price_0'

    @mockserver.json_handler(
        '/antifraud/client/user/is_spammer/integration_orders_commit',
    )
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': COMMON_USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'user_source_id': 'call_center',
            'order_id': _ORDER_ID,
        }
        blocked_until = now + datetime.timedelta(seconds=6)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={'userid': COMMON_USER_ID, 'orderid': _ORDER_ID},
        headers=CC_HEADERS,
    )
    assert response.status_code == 403
    assert response.json()['blocked'] == '2017-05-25T08:30:06+0000'


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'integration_orders_commit': {
            'use_afs': True,
            'retries': 1,
            'timeout': 100,
        },
    },
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'fixed_price_cpp',
    'calc_info_cpp',
    'get_experiments_cpp',
    'ordercommit_cpp_full',
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_fixed_price_is_spammer_disabled_in_client(
        taxi_integration, ordercommit_services, mockserver, now,
):
    _ORDER_ID = 'fixed_price_0'

    @mockserver.json_handler(
        '/antifraud/client/user/is_spammer/integration_orders_commit',
    )
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': COMMON_USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'user_source_id': 'call_center',
            'order_id': _ORDER_ID,
        }
        blocked_until = now + datetime.timedelta(seconds=6)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={'userid': COMMON_USER_ID, 'orderid': _ORDER_ID},
        headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'integration_orders_commit': {
            'use_afs': True,
            'retries': 1,
            'timeout': 100,
        },
    },
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'fixed_price_cpp',
    'calc_info_cpp',
    'get_experiments_cpp',
    'ordercommit_cpp_full',
)
@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_fixed_price_not_blocked_user(
        taxi_integration, ordercommit_services, mockserver, db,
):
    _ORDER_ID = 'fixed_price_0'

    @mockserver.json_handler(
        '/antifraud/client/user/is_spammer/integration_orders_commit',
    )
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': COMMON_USER_ID,
            'user_phone_id': '5714f45e98956f06baaae3d4',
            'user_source_id': 'call_center',
            'order_id': _ORDER_ID,
        }
        return {'is_spammer': False}

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={'userid': COMMON_USER_ID, 'orderid': _ORDER_ID},
        headers=CC_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'retries': 1, 'timeout': 100},
        'integration_orders_commit': {
            'use_afs': True,
            'retries': 1,
            'timeout': 100,
        },
    },
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'fixed_price_cpp',
    'calc_info_cpp',
    'get_experiments_cpp',
    'ordercommit_cpp_full',
)
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('response_code', [500, 400, 403])
def test_ordercommit_fixed_price_is_spammer_affected(
        taxi_integration, ordercommit_services, mockserver, db, response_code,
):
    _ORDER_ID = 'fixed_price_0'

    @mockserver.json_handler(
        '/antifraud/client/user/is_spammer/integration_orders_commit',
    )
    def mock_afs_is_spammer_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={'userid': COMMON_USER_ID, 'orderid': _ORDER_ID},
        headers=CC_HEADERS,
    )
    assert response.status_code == 200


CALLCENTER_ORDERS_LIMIT = 3
CORPCABINET_ORDERS_LIMIT = 17
BIG_LIMIT = 30
NOW_TIMESTAMP = 1539360300


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(
    MAX_CORPCABINET_ORDERS=CORPCABINET_ORDERS_LIMIT,
    MAX_CALLCENTER_ORDERS=CALLCENTER_ORDERS_LIMIT,
    # To avoid ordercommit_services.mocksurge checks.
    # Anyway we don't need to check surge here.
    SURGE_ENABLED=False,
)
@pytest.mark.parametrize(
    'source,application,limit',
    [
        ('call_center', 'callcenter', CALLCENTER_ORDERS_LIMIT),
        ('corp_cabinet', 'corpweb', CORPCABINET_ORDERS_LIMIT),
        ('persey', 'persey', BIG_LIMIT),
    ],
)
def test_ordercommit_many_orders(
        taxi_integration,
        db,
        source,
        application,
        limit,
        mock_solomon,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    proc = db.order_proc.find_one({'_id': 'good'})
    proc['order']['source'] = source
    proc['order']['statistics']['application'] = application
    for i in range(limit):
        proc['_id'] = 'order_id_' + str(i)
        db.order_proc.insert(proc)
    proc['_id'] = 'order_id_extra'
    db.order_proc.insert(proc)

    db.users.update({'_id': COMMON_USER_ID}, {'$set': {'sourceid': source}})

    def commit_order(order_id):
        request = {'userid': COMMON_USER_ID, 'orderid': order_id}
        if source == 'call_center':
            headers = CC_HEADERS
        elif source == 'persey':
            headers = {'User-Agent': 'persey'}
        else:
            headers = {}
            request['sourceid'] = source
        return taxi_integration.post(
            'v1/orders/commit', json=request, headers=headers,
        )

    mock_solomon.reset()
    mock_solomon.set_ordered(False)
    mock_solomon.add(
        [
            {
                'kind': 'IGAUGE',
                'labels': {'reason': 'too_many', 'sensor': 'order_429'},
                'timeseries': [{'ts': NOW_TIMESTAMP, 'value': 1.0}],
            },
        ],
    )

    for i in range(limit):
        response = commit_order('order_id_' + str(i))
        assert response.status_code == 200
    if limit < BIG_LIMIT:
        response = commit_order('order_id_extra')
        assert response.status_code == 429
        data = response.json()
        assert data == {'code': 'TOO_MANY_CONCURRENT_ORDERS'}

        mock_solomon.wait_for()


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(
    ORDER_RESTRICTION_USE_ORDER_CORE='enabled', SURGE_ENABLED=False,
)
@pytest.mark.parametrize('expected_status_code', [200, 429])
def test_ordercommit_by_city_limit(
        taxi_integration,
        db,
        expected_status_code,
        mockserver,
        mock_solomon,
        pricing_data_preparer,
):
    @mockserver.json_handler('/order-core/internal/stats/v1/can-commit-order')
    def mock_can_commit(request):
        return {'can_commit': expected_status_code == 200}

    pricing_data_preparer.set_locale('ru')

    proc = db.order_proc.find_one({'_id': 'good'})
    proc['order']['source'] = 'call_center'
    proc['order']['statistics']['application'] = 'callcenter'
    proc['_id'] = 'order_id_extra'
    db.order_proc.insert(proc)

    db.users.update(
        {'_id': COMMON_USER_ID}, {'$set': {'sourceid': 'call_center'}},
    )

    request = {'userid': COMMON_USER_ID, 'orderid': 'order_id_extra'}
    response = taxi_integration.post(
        'v1/orders/commit', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == expected_status_code

    assert mock_can_commit.wait_call()


COMMIT_TESTPOINTS = [
    'ordercommit::on_set_state_pending',
    'ordercommit::on_set_state_reserved',
    'ordercommit::on_set_state_done',
]


@pytest.mark.now('2018-08-08T16:00:00+0300')
@pytest.mark.parametrize('testpoint_name', COMMIT_TESTPOINTS)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(MAX_MULTIORDER_CONCURRENT_ORDERS=1)
@pytest.mark.order_experiments('forced_surge')
def test_order_race_parallel_lock(
        taxi_integration,
        db,
        ordercommit_services,
        testpoint,
        testpoint_name,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    userid = COMMON_USER_ID
    order_id = 'good'
    sourceid = 'alice'
    db.users.update({'_id': userid}, {'$set': {'sourceid': sourceid}})

    request = {
        'userid': userid,
        'orderid': order_id,
        'sourceid': sourceid,
        'chainid': 'chainid_1',
    }

    # at least some experiment must be set
    ordercommit_services.experiments = ['forced_surge']

    testpoint_calls = []

    @testpoint(testpoint_name)
    def create_parallel_order(data):
        if len(testpoint_calls) > 0:
            return  # avoid recursive calls
        testpoint_calls.append(data)
        # pdb.set_trace()
        resp_same_order = taxi_integration.post('v1/orders/commit', request)

        # should throw LockFailed and return 202
        assert resp_same_order.status_code == 202, order_id
        exp_date = 'Wed, 08 Aug 2018 13:00:05 GMT'
        assert resp_same_order.headers['Retry-After'] == exp_date

    resp = taxi_integration.post('v1/orders/commit', request)
    # limit for concurrent orders is 1
    assert resp.status_code == 200, resp


@pytest.mark.filldb(order_offers='obsolete')
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
def test_ordercommit_cant_construct_route(
        taxi_integration,
        mockserver,
        ordercommit_services,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_fixed_price(False, 'NO_ROUTE')

    ordercommit_services.experiments = ['fixed_price']
    response = taxi_integration.post(
        'v1/orders/commit',
        json={'userid': COMMON_USER_ID, 'orderid': 'order_offer_obsolete'},
        headers=CC_HEADERS,
    )
    assert response.status_code == 406
    content = response.json()
    assert content == {'error': {'code': 'PRICE_CHANGED'}}


def init_coupon(db, order_id, coupon_id):
    if not coupon_id:
        return
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.coupon': {
                    'id': coupon_id,
                    # see default values in protocol/lib/src/models/order2.cpp
                    # in func
                    # ::mongo::BSONObj ToBsonCouponObj(const Request& request)
                    'valid': True,
                    'valid_any': False,
                    'was_used': False,
                },
            },
        },
    )


def init_offer(db, order_id, coupon):
    offer = db.order_proc.find_one(order_id)['order']['offer']
    to_set = {'coupon': {'code': coupon, 'value': 100}} if coupon else {}
    db.order_offers.update({'_id': offer}, {'$set': {'extra_data': to_set}})


# TVM_SERVICES from manual/secdist.json
# communications -> 25
# integration-api -> 23
# coupons -> 40
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'communications', 'dst': 'integration-api'},
        {'src': 'integration-api', 'dst': 'coupons'},
    ],
)
def test_reserve_via_coupons_code(
        taxi_integration, mockserver, db, tvm2_client,
):

    to_coupons_ticket = 'secret'
    tvm2_client.set_ticket(json.dumps({'40': {'ticket': to_coupons_ticket}}))

    coupons_reserve_count = 0

    @mockserver.json_handler('/coupons/v1/couponreserve')
    def mock_couponreserve(request):
        assert request.headers['X-Ya-Service-Ticket'] == to_coupons_ticket
        nonlocal coupons_reserve_count
        coupons_reserve_count = coupons_reserve_count + 1
        return {
            'exists': True,
            'valid': True,
            'valid_any': True,
            'value': 100,
            'series': '_referral_',
            'some_additional_info': 'Not contained in schema info',
        }

    init_offer(db, 'fixed_price_0', 'onlyoneusage')
    init_coupon(db, 'fixed_price_0', 'onlyoneusage')

    request = {
        'userid': 'good',
        'orderid': 'fixed_price_0',
        'chainid': 'chainid_1',
    }

    # tvmknife unittest service -s 25 -d 23
    to_int_api_ticket = (
        '3:serv:CBAQ__________9_IgQIGRAX:AoNlKf1uskVjZHapuol5kki7-Ey_76c2op17'
        '2LImYQXVuqyGfItQDE7BeoCMc_sZd2UmqAt2VlS5MKpCvlHSkPfsIRZuTFY9XNCYhCz4t'
        'kmMXNA5cS_M3OjE1bOfEXlk7bIvLRXJ97yYEKexcmVoWYa9WUkcvYIlPA6souGGkMg'
    )
    response = taxi_integration.post(
        'v1/orders/commit',
        request,
        headers={
            'X-Ya-Service-Ticket': to_int_api_ticket,
            'User-Agent': 'call_center',
        },
    )
    assert 1 == coupons_reserve_count
    assert 200 == response.status_code, response.text


@pytest.mark.filldb(order_proc='agent')
@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
)
def test_orders_commit_agent(taxi_integration, pricing_data_preparer):
    pricing_data_preparer.set_locale('ru')
    commit_request = {'userid': 'agent_user', 'orderid': 'agent_order'}
    response = taxi_integration.post(
        'v1/orders/commit',
        commit_request,
        headers={'User-Agent': 'agent_007'},
    )
    assert response.status_code == 200, response.text


@pytest.mark.filldb(order_proc='agent')
@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=True,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
@pytest.mark.parametrize(
    'tvm_ticket, expected_code',
    [
        pytest.param(
            PARTNER_ORDERS_API_TVM_TICKET, 200, id='partner-orders-api',
        ),
        pytest.param(OTHER_SERVICE_TVM_TICKET, 406, id='other-service'),
    ],
)
def test_agent_order_not_acceptable(
        taxi_integration, pricing_data_preparer, tvm_ticket, expected_code,
):
    pricing_data_preparer.set_locale('ru')
    commit_request = {'userid': 'agent_user', 'orderid': 'agent_order'}
    headers = {'User-Agent': 'agent_007'}

    headers['X-Ya-Service-Ticket'] = tvm_ticket
    response = taxi_integration.post(
        'v1/orders/commit', commit_request, headers=headers,
    )
    assert response.status_code == expected_code


@pytest.mark.filldb(order_proc='agent')
@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=True,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
def test_agent_payment_ok(taxi_integration, pricing_data_preparer):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_locale('ru')
    commit_request = {'userid': 'agent_user', 'orderid': 'agent_payment_order'}
    headers = {'User-Agent': 'agent_007'}
    headers['X-Ya-Service-Ticket'] = PARTNER_ORDERS_API_TVM_TICKET
    response = taxi_integration.post(
        'v1/orders/commit', commit_request, headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.filldb(order_proc='agent')
@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=True,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
def test_agent_payment_not_acceptable(taxi_integration, pricing_data_preparer):
    pricing_data_preparer.set_locale('ru')
    commit_request = {'userid': 'agent_user', 'orderid': 'agent_payment_order'}
    headers = {'User-Agent': 'agent_007'}
    headers['X-Ya-Service-Ticket'] = OTHER_SERVICE_TVM_TICKET
    response = taxi_integration.post(
        'v1/orders/commit', commit_request, headers=headers,
    )
    assert response.status_code == 406


@pytest.mark.filldb(order_proc='agent')
@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
    INTEGRATION_API_AGENT_ORDERS_CHECK_SRC=False,
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'partner-orders-api', 'dst': 'integration-api'},
        {'src': 'other-service', 'dst': 'integration-api'},
    ],
    TVM_SERVICES={
        'integration-api': 23,
        'partner-orders-api': 123,
        'other-service': 148,
    },
)
def test_agent_payment_check_disabled(taxi_integration, pricing_data_preparer):
    pricing_data_preparer.set_locale('ru')
    pricing_data_preparer.set_fixed_price(enable=False)
    commit_request = {'userid': 'agent_user', 'orderid': 'agent_payment_order'}
    headers = {'User-Agent': 'agent_007'}
    headers['X-Ya-Service-Ticket'] = OTHER_SERVICE_TVM_TICKET
    response = taxi_integration.post(
        'v1/orders/commit', commit_request, headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.filldb(
    order_proc='agent_application', order_offers='agent_application',
)
@pytest.mark.config(
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_007'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_007'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'agent_007'}]},
)
@pytest.mark.parametrize(
    'order_id,agent_application,expected_code',
    [
        ('agent_order_callcenter', 'callcenter', 200),
        ('agent_order_callcenter', 'partner_application', 406),
        ('agent_order_callcenter', None, 406),
        ('agent_order_default', 'callcenter', 406),
        ('agent_order_default', 'partner_application', 200),
        ('agent_order_default', None, 200),
        ('agent_order_none', 'callcenter', 406),
        ('agent_order_none', 'partner_application', 200),
        ('agent_order_none', None, 200),
    ],
)
def test_orders_commit_agent_application(
        taxi_integration,
        pricing_data_preparer,
        db,
        order_id,
        agent_application,
        expected_code,
):
    pricing_data_preparer.set_locale('ru')

    commit_request = {'userid': 'agent_user', 'orderid': order_id}
    offer = db.order_proc.find_one(order_id)['order']['offer']
    agent = (
        {
            'agent_id': '007',
            'agent_user_type': 'individual',
            'agent_application': agent_application,
        }
        if agent_application
        else {'agent_id': '007', 'agent_user_type': 'individual'}
    )
    db.order_offers.update({'_id': offer}, {'$set': {'agent': agent}})

    response = taxi_integration.post(
        'v1/orders/commit',
        commit_request,
        headers={'User-Agent': 'agent_007'},
    )
    assert response.status_code == expected_code, response.text


@pytest.mark.order_experiments('forced_surge')
@pytest.mark.filldb(order_proc='vt')
@pytest.mark.config(USE_TARIFFS_TO_FILTER_SUPPLY=True)
def test_virtual_tariffs(
        taxi_integration,
        mockserver,
        db,
        ordercommit_services,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def _mock_virtual_tariffs(request):
        return {'virtual_tariffs': []}

    ordercommit_services.experiments = ['forced_surge']
    order_id = 'order_virtual_tariffs'
    commit_request = {
        'userid': 'good',
        'orderid': order_id,
        'chainid': 'chainid_1',
    }
    response = taxi_integration.post(
        'v1/orders/commit',
        commit_request,
        headers={'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text

    assert _mock_virtual_tariffs.times_called == 0

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['order']['virtual_tariffs'] == [
        {
            'class': 'econom',
            'special_requirements': [{'id': 'id1'}, {'id': 'id2'}],
        },
        {
            'class': 'express',
            'special_requirements': [{'id': 'id1'}, {'id': 'id2'}],
        },
    ]
    assert 'virtual_tariffs' not in proc['order']['request']


@pytest.mark.usefixtures('pricing_data_preparer')
@pytest.mark.filldb(order_proc='restricted_routes')
@pytest.mark.parametrize(
    ['expected_status'],
    [
        pytest.param(
            200,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': False,
                    'restricted_countries': [],
                },
            ),
            id='config_disabled',
        ),
        pytest.param(
            200,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': [],
                },
            ),
            id='config_enabled_no_countries',
        ),
        pytest.param(
            200,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': ['rus'],
                },
            ),
            id='config_enabled_A_point_country_match',
        ),
        pytest.param(
            200,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': ['kaz'],
                },
            ),
            id='config_enabled_B_point_country_match',
        ),
        pytest.param(
            406,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': ['rus', 'kaz'],
                },
            ),
            id='config_enabled_A_and_B_points_country_match',
        ),
    ],
)
def test_route_restrictions_config(
        taxi_integration,
        mockserver,
        db,
        pricing_data_preparer,
        expected_status,
):
    pricing_data_preparer.set_locale('ru')
    order_id = 'order_with_restricted_route'
    commit_request = {
        'userid': 'good',
        'orderid': order_id,
        'chainid': 'chainid_1',
    }
    response = taxi_integration.post(
        'v1/orders/commit',
        commit_request,
        headers={'User-Agent': 'call_center'},
    )
    assert response.status_code == expected_status
    if response.status_code == 406:
        assert response.json() == {
            'error': {'code': 'ROUTE_OVER_CLOSED_BORDER'},
        }


@pytest.mark.usefixtures('pricing_data_preparer')
@pytest.mark.filldb(order_proc='restricted_routes')
@pytest.mark.parametrize(
    ('cargo_matcher_response', 'expected_status'),
    [
        pytest.param(
            {'forbidden_tariffs': []},
            200,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': False,
                    'restricted_countries': [],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='only cargo-matcher no restrictions',
        ),
        pytest.param(
            {
                'forbidden_tariffs': [
                    {
                        'prohibition_reason': (
                            'estimating.international_orders_prohibition_to_kg'
                        ),
                        'tariff': 'econom',
                    },
                ],
            },
            406,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': False,
                    'restricted_countries': [],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='only cargo-matcher restricted',
        ),
    ],
)
def test_route_delivery_restrictions(
        taxi_integration,
        mockserver,
        pricing_data_preparer,
        cargo_matcher_response,
        expected_status,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/cargo_matcher/v1/routes-prohibition')
    def _mock_cargo_matcher(request):
        return mockserver.make_response(
            status=200, response=json.dumps(cargo_matcher_response),
        )

    order_id = 'order_with_restricted_route'
    commit_request = {
        'userid': 'good',
        'orderid': order_id,
        'chainid': 'chainid_1',
    }
    response = taxi_integration.post(
        'v1/orders/commit',
        commit_request,
        headers={'User-Agent': 'call_center'},
    )
    assert _mock_cargo_matcher.times_called
    assert response.status_code == expected_status
    if response.status_code == 406:
        assert response.json() == {'error': {'code': 'DELIVERY_RESTRICTED'}}


@pytest.mark.usefixtures('pricing_data_preparer')
@pytest.mark.filldb(order_proc='whitelabel')
@pytest.mark.config(
    MULTIORDER_INT_API_LIMITS_FOR_APPLICATIONS={
        '/whitelabel/superweb/whitelabel_0': 3,
    },
)
@pytest.mark.parametrize(
    ('set_cost', 'expected_status', 'expected_response'),
    [
        pytest.param(
            True,
            200,
            {
                'orderid': 'order_whitelabel',
                'status': 'search',
                'can_make_more_orders': 'allowed',
            },
            id='simple',
        ),
        pytest.param(
            False,
            406,
            {'error': {'code': 'PRICE_CHANGED'}},
            id='different cost',
        ),
    ],
)
def test_whitelabel(
        taxi_integration,
        whitelabel_fixtures,
        pricing_data_preparer,
        set_cost,
        expected_status,
        expected_response,
):
    pricing_data_preparer.set_locale('ru')
    if set_cost:
        pricing_data_preparer.set_cost(1337, 1337)

    path = 'v1/orders/commit'
    commit_request = {
        'userid': 'whitelabel_superweb_user_id',
        'orderid': 'order_whitelabel',
        'sourceid': 'turboapp',
    }

    response = taxi_integration.post(
        path,
        commit_request,
        headers={
            'User-Agent': (
                'Mozilla/5.0 Chrome/89.0 whitelabel/superweb/whitelabel_0'
            ),
        },
    )
    assert response.status_code == expected_status
    response_json = response.json()
    response_json.pop('version', None)
    assert response_json == expected_response


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['test_application'],
    MAX_MULTIORDER_CONCURRENT_ORDERS=1,
    MULTIORDER_INT_API_LIMITS_FOR_APPLICATIONS={'test_application': 5},
)
def test_ordercommit_int_api_multiorder(
        taxi_integration, db, mock_solomon, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    order_count = 5
    proc = db.order_proc.find_one({'_id': 'good'})
    proc['order']['statistics']['application'] = 'test_application'
    for i in range(order_count):
        proc['_id'] = 'order_id_' + str(i)
        db.order_proc.insert(proc)
    proc['_id'] = 'order_id_extra'
    db.order_proc.insert(proc)

    def commit_order(order_id):
        request = {'userid': COMMON_USER_ID, 'orderid': order_id}
        headers = {}
        return taxi_integration.post(
            'v1/orders/commit', json=request, headers=headers,
        )

    for i in range(order_count):
        response = commit_order('order_id_' + str(i))
        assert response.status_code == 200

    response = commit_order('order_id_extra')
    assert response.status_code == 429
    data = response.json()
    assert data == {'code': 'TOO_MANY_CONCURRENT_ORDERS'}


def test_app_config_update_failure(taxi_integration, taxi_config, mockserver):
    @mockserver.json_handler('/configs-service/configs/values')
    def mock_configs(request):
        return {
            'configs': taxi_config.get_values(),
            'updated_at': datetime.datetime.now().strftime(
                format='%Y-%m-%dT%H:%M:%SZ',
            ),
        }

    def _reload_configs():
        taxi_integration.post(
            'tests/control',
            {'invalidate_caches': True, 'cache_clean_update': True},
        )

    taxi_integration.invalidate_caches()

    taxi_config.set_values(dict(APPLICATION_DETECTION_RULES_NEW='broken'))
    mock_configs.wait_call()

    # Gather 5 fails to find out that there is a failure in configs
    for _ in range(5):
        _reload_configs()
    # every time configs are requested
    assert mock_configs.times_called == 5

    # throttle requests to configs now: skip 10 updates
    for _ in range(10):
        _reload_configs()
    # no requests
    assert mock_configs.times_called == 5

    # we can try to update now
    _reload_configs()
    assert mock_configs.times_called == 6

    # fix config
    taxi_config.set_values(
        dict(
            APPLICATION_DETECTION_RULES_NEW={
                'rules': [{'@app_name': 'agent_007'}],
            },
        ),
    )

    # skip 10 requests again
    for _ in range(10):
        _reload_configs()
    assert mock_configs.times_called == 6

    # another try to update, successful
    _reload_configs()
    assert mock_configs.times_called == 7

    # no failure now, make request every update
    for _ in range(5):
        _reload_configs()
    assert mock_configs.times_called == 12
