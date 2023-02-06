import datetime
import json

import bson
import pytest

from taxi_tests import utils

from order_offers_switch_parametrize import ORDER_OFFERS_MATCH_COMPARE_SWITCH
from order_offers_switch_parametrize import ORDER_OFFERS_MATCH_SWITCH
from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)


def check_support_commit(order_id, mock_stq_agent):
    tasks = mock_stq_agent.get_tasks('support_commit')
    ids = set(task.id for task in tasks)
    assert len(ids) == 1

    support_commit = tasks[0]
    assert support_commit.id == order_id
    a = support_commit.args
    assert a[0] == order_id
    assert 'log_extra' in a[1]
    assert a[2] == order_id
    assert a[3] is True
    assert a[4] == 5
    assert a[5] == 1
    assert a[6] == 1

    assert 'log_extra' in support_commit.kwargs
    assert support_commit.is_postponed


def check_processing(order_id, mock_stq_agent):
    tasks = mock_stq_agent.get_tasks('processing')
    ids = set(task.id for task in tasks)
    assert len(ids) == 0


def check_created_order_in_stq(order_id, mock_stq_agent):
    check_support_commit(order_id, mock_stq_agent)
    check_processing(order_id, mock_stq_agent)


@pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
@ORDER_OFFERS_MATCH_COMPARE_SWITCH
def test_ordercommit_is_idempotent(
        taxi_protocol,
        mockserver,
        load_json,
        mock_stq_agent,
        mock_order_offers,
        order_offers_match_compare_enabled,
):
    req = load_json('basic_request.json')

    # 1. create draft
    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    # 2. commit it once successfully
    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    assert resp.json()['orderid'] == order_id
    assert resp.json()['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent)

    # 3. commit second time and check that second commit is idempotent
    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    assert resp.json()['orderid'] == order_id
    assert resp.json()['status'] == 'search'
    check_created_order_in_stq(order_id, mock_stq_agent)

    assert mock_order_offers.mock_match_offer.times_called == (
        1 if order_offers_match_compare_enabled else 0
    )


@pytest.mark.config(
    BILLING_USE_MONGO_STATS_COUNTER=True,
    BILLING_AUTOMATIC_FALLBACK_MIN_EVENTS=20,
)
@pytest.mark.parametrize(
    'fallback_enabled, method, auto_min_rate, method_min_rate,'
    'method_min_events, result',
    [
        (True, 'PayBasket', 0.1, 0.9, 20, None),
        (True, 'PayBasket', 0.1, 0.1, 200, None),
        (True, 'PayBasket', 0.1, 0.1, 20, True),
        (True, 'CheckCard', 0.1, 0.1, 20, None),
        (False, 'PayBasket', 0.9, 0.1, 20, None),
        (False, 'PayBasket', 0.1, 0.1, 20, True),
        (False, 'PayBasket', 0.1, 0.9, 200, True),
    ],
)
def test_ordercommit_billing_fallback(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        fallback_enabled,
        method,
        auto_min_rate,
        method_min_rate,
        method_min_events,
        result,
        config,
):
    config.set_values(
        dict(
            BILLING_METHOD_FALLBACK_ENABLED=fallback_enabled,
            BILLING_FALLBACK_METHODS=[method],
            BILLING_AUTOMCATIC_FALLBACK_MIN_RATE=auto_min_rate,
            BILLING_FALLBACK_RATE={
                '__default__': {
                    '__default__': {
                        'fallback_rate': 0.1,
                        'fallback_events': 20,
                    },
                    'PayBasket': {
                        'fallback_rate': method_min_rate,
                        'fallback_events': method_min_events,
                    },
                },
            },
        ),
    )
    taxi_protocol.invalidate_caches()
    req = load_json('basic_request.json')

    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    proc = db.order_proc.find_one(
        {'order.user_id': req['id'], '_id': order_id},
    )
    assert proc is not None
    assert result == proc['payment_tech'].get('billing_fallback_enabled')


@pytest.mark.experiments3(filename='experiments3_origin_point_b.json')
@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
def test_ordercommit_origin_point_b(taxi_protocol, mockserver, load_json, db):
    taxi_protocol.invalidate_caches()
    setup_pp_mock(mockserver, load_json)

    @mockserver.json_handler('/alt/alt_b/v1/save')
    def _mock_alt_b_v1_save(request):
        body = json.loads(request.get_data())
        assert body['origin_point_b'] == {
            'address': 'ул. Отрадная, 7',
            'point': [37.610098, 55.857462],
            'walk_time': 30.0,
        }
        assert body['route'] == [[37.01, 55.01], [37.02, 55.02]]
        assert (
            request.headers['X-YaTaxi-UserId']
            == 'f4eb6aaa29ad4a6eb53f8a7620793561'
        )
        return {}

    req = load_json('basic_request.json')

    origin_point_b = {
        'address': 'ул. Отрадная, 7',
        'geopoint': [37.610098, 55.857462],
    }
    req.update(
        {
            'origin_point_b': origin_point_b,
            'alternative_type': 'altpin_b',
            'offer': 'altpin_b_offer',
        },
    )

    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    proc = db.order_proc.find_one(
        {'order.user_id': req['id'], '_id': order_id},
    )
    assert proc is not None
    assert proc['order']['request']['origin_point_b'] == origin_point_b
    assert proc['order']['request']['alternative_type'] == 'altpin_b'
    assert _mock_alt_b_v1_save.has_calls


COMMIT_TESTPOINTS = [
    'ordercommit::on_set_state_pending',
    'ordercommit::on_set_state_reserved',
    'ordercommit::on_set_state_done',
]


@pytest.mark.parametrize('testpoint_name', COMMIT_TESTPOINTS)
@pytest.mark.config(ORDER_COMMIT_ATTEMPTS=1)
def test_order_race_no_retry(
        taxi_protocol, testpoint, load_json, db, testpoint_name,
):
    init_testpoint(db, testpoint, testpoint_name)
    _, resp = create_order(load_json, taxi_protocol)

    # commit should fail because it made only 1 attempt
    assert resp.status_code == 406


@pytest.mark.parametrize('testpoint_name', COMMIT_TESTPOINTS)
@pytest.mark.config(ORDER_COMMIT_ATTEMPTS=2)
def test_order_race_one_retry(
        taxi_protocol, testpoint, load_json, db, testpoint_name,
):
    init_testpoint(db, testpoint, testpoint_name)
    # commit should succeed because of second attempt inside
    create_order_ok(load_json, taxi_protocol)


@pytest.mark.now('2018-08-08T16:00:00+0300')
@pytest.mark.parametrize('testpoint_name', COMMIT_TESTPOINTS)
@pytest.mark.config(MAX_MULTIORDER_CONCURRENT_ORDERS=1)
@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_order_race_parallel_lock(
        taxi_protocol,
        testpoint,
        load_json,
        db,
        mockserver,
        testpoint_name,
        read_from_replica_dbusers,
):
    setup_pp_mock(mockserver, load_json)
    order_id = create_draft(load_json, taxi_protocol)

    testpoint_calls = []
    limits_commited = testpoint_name != 'ordercommit::on_set_state_pending'

    @testpoint('orderkit::GetUserById')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    @testpoint(testpoint_name)
    def create_parallel_order(data):
        if len(testpoint_calls) > 0:
            return  # avoid recursive calls

        testpoint_calls.append(data)
        _, resp_another_order = create_order(load_json, taxi_protocol)

        exp_code = 429 if limits_commited else 200
        assert resp_another_order.status_code == exp_code

        resp_same_order = commit_order(taxi_protocol, load_json, order_id)

        # should throw LockFailed and return 202
        assert resp_same_order.status_code == 202, order_id
        exp_date = 'Wed, 08 Aug 2018 13:00:05 GMT'
        assert resp_same_order.headers['Retry-After'] == exp_date

    resp = commit_order(taxi_protocol, load_json, order_id)

    # limit for concurrent orders is 1
    exp_code = 200 if limits_commited else 429
    assert resp.status_code == exp_code, order_id
    assert replica_dbusers_test_point.times_called == 4


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_multiorder_limit(taxi_protocol, load_json):
    MAX_MULTIORDER_CONCURRENT_ORDERS = 3
    # check draft doesn't have limits
    for _ in range(MAX_MULTIORDER_CONCURRENT_ORDERS + 1):
        create_draft(load_json, taxi_protocol)

    # create MAX_MULTIORDER_CONCURRENT_ORDERS orders
    for _ in range(MAX_MULTIORDER_CONCURRENT_ORDERS):
        create_order_ok(load_json, taxi_protocol)

    # next /ordercommit must fail because of limit
    create_order_fail_limit(load_json, taxi_protocol)


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    MULTIORDER_UNLIMITED_APPLICATION=['android'],
)
def test_multiorder_unlimit(taxi_protocol, load_json):
    MAX_MULTIORDER_CONCURRENT_ORDERS = 3
    additional_orders = 5

    # create more than MAX_MULTIORDER_CONCURRENT_ORDERS orders
    for _ in range(MAX_MULTIORDER_CONCURRENT_ORDERS + additional_orders):
        create_order_ok(load_json, taxi_protocol)


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@pytest.mark.filldb(tariff_settings='limited_econom')
def test_multiorder_tariff_limit(taxi_protocol, load_json):
    CONCURRENT_ORDERS = 2
    # check draft doesn't have limits
    for _ in range(CONCURRENT_ORDERS + 1):
        create_draft(load_json, taxi_protocol)

    # create MAX_MULTIORDER_CONCURRENT_ORDERS orders
    for _ in range(CONCURRENT_ORDERS):
        create_order_ok(load_json, taxi_protocol)

    # next /ordercommit must fail because of tariff limit
    create_order_fail_limit(load_json, taxi_protocol, 406)


@pytest.mark.config(MAX_CONCURRENT_ORDERS=1)
@pytest.mark.config(MAX_MULTIORDER_CONCURRENT_ORDERS=3)
def test_multiorder_limit_disabled_limit_experiment(taxi_protocol, load_json):
    create_order_ok(load_json, taxi_protocol)

    # second creation must fail because experiment 'multiorder_limits_enabled'
    # is disabled
    create_order_fail_limit(load_json, taxi_protocol)


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=1,
    MAX_MULTIORDER_CONCURRENT_ORDERS=1,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_multiorder_no_can_make_more(taxi_protocol, load_json):
    _, resp = create_order_ok(load_json, taxi_protocol)

    # assert field == 'allowed' (fallback value) because the parameter
    # 'multiorder_calc_can_make_more_orders' is False
    assert resp.json().get('can_make_more_orders') == 'allowed'


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_multiorder_can_make_more_simple(taxi_protocol, load_json):
    MAX_MULTIORDER_CONCURRENT_ORDERS = 3
    for i in range(MAX_MULTIORDER_CONCURRENT_ORDERS):
        order_id = create_draft(load_json, taxi_protocol)
        for _ in range(2):
            # commit twice to check handling of already commited order:
            # in this case we should also return valid 'can_make_more_orders'
            resp = commit_order(taxi_protocol, load_json, order_id)
            assert resp.status_code == 200
            can_make = resp.json().get('can_make_more_orders')
            if i == MAX_MULTIORDER_CONCURRENT_ORDERS - 1:
                assert can_make == 'disallowed'
            else:
                assert can_make == 'allowed'

    # next /ordercommit must fail because of limit
    resp = create_order_fail_limit(load_json, taxi_protocol)
    assert resp.json().get('can_make_more_orders') is None


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=1,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
)
def test_ordercommit_can_make_more(taxi_protocol, load_json):
    # the same as test_multiorder_can_make_more but with disabled
    # multiorder limits
    _, resp = create_order_ok(load_json, taxi_protocol)
    assert resp.json().get('can_make_more_orders') == 'disallowed'

    # next /ordercommit must fail because of limit 1
    resp = create_order_fail_limit(load_json, taxi_protocol)
    assert resp.json().get('can_make_more_orders') is None


def create_order(
        load_json,
        taxi_protocol,
        req_file=None,
        internal_ordercommit=False,
        **http_kwargs,
):
    order_id = create_draft(load_json, taxi_protocol, req_file, **http_kwargs)
    commit_resp = commit_order(
        taxi_protocol,
        load_json,
        order_id,
        internal_ordercommit=internal_ordercommit,
        req_file=req_file,
        **http_kwargs,
    )
    return order_id, commit_resp


def create_order_ok(
        load_json,
        taxi_protocol,
        req_file=None,
        internal_ordercommit=False,
        **http_kwargs,
):
    order_id, resp = create_order(
        load_json,
        taxi_protocol,
        req_file,
        internal_ordercommit=internal_ordercommit,
        **http_kwargs,
    )
    assert resp.status_code == 200
    return order_id, resp


def create_order_ok_expect_cmm(
        taxi_protocol, load_json, exp_can_make_more, **http_kwargs,
):
    order_id, resp = create_order_ok(load_json, taxi_protocol, **http_kwargs)
    assert resp.json().get('can_make_more_orders') == exp_can_make_more
    return order_id


def create_order_fail_limit(
        load_json, taxi_protocol, status_code=429, **http_kwargs,
):
    _, resp = create_order(load_json, taxi_protocol, **http_kwargs)
    assert resp.status_code == status_code
    return resp


def create_draft(load_json, taxi_protocol, req_file=None, **http_kwargs):
    if req_file is None:
        req_file = 'basic_request.json'
    request = load_json(req_file)
    draft_resp = taxi_protocol.post('3.0/orderdraft', request, **http_kwargs)
    assert draft_resp.status_code == 200
    return draft_resp.json()['orderid']


def commit_order(
        taxi_protocol,
        load_json,
        order_id,
        internal_ordercommit=False,
        req_file=None,
        **http_kwargs,
):
    if req_file is None:
        req_file = 'basic_request.json'
    request = load_json(req_file)
    commit_request = {
        'id': request['id'],
        'orderid': order_id,
        'check_unfinished_commit': False,
    }

    if internal_ordercommit:
        url = 'internal/ordercommit'
    else:
        url = '3.0/ordercommit'
    return taxi_protocol.post(url, commit_request, **http_kwargs)


def init_testpoint(db, testpoint, testpoint_name):
    @testpoint(testpoint_name)
    def update_state_to_done(data):
        query = {'_id': data['order_id'], '_shard_id': 0}
        update = {'$set': {'commit_state': 'done'}}
        db.order_proc.find_and_modify(query, update, False)


def setup_pp_mock(mockserver, load_json):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}


EXTRA_PASS_REQ = 'basic_request_extra_pass_name.json'


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=3,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.parametrize('use_pass_name_for_order1', (False, True))
@pytest.mark.parametrize('use_pass_name_for_order2', (False, True))
def test_ordercommit_multiorder_process(
        use_pass_name_for_order1,
        use_pass_name_for_order2,
        db,
        taxi_protocol,
        load_json,
):

    # internal ordercommit should not be used for commiting new orders,
    # only for executing support commit (when commit state is not None)
    internal_ordercommit = False

    def get_req_file(use_pass_name):
        return EXTRA_PASS_REQ if use_pass_name else None

    def get_order_name(use_pass_name, order_number):
        if use_pass_name:
            return 'Для Денис'
        return 'Заказ №{}'.format(order_number + 1)

    use_pass_names = [
        use_pass_name_for_order1,
        use_pass_name_for_order2,
        False,
    ]
    reqs = list(map(get_req_file, use_pass_names))
    order_names = [get_order_name(u, i) for i, u in enumerate(use_pass_names)]

    order_ids = []
    for i in range(3):
        order_id, _ = create_order_ok(
            load_json,
            taxi_protocol,
            req_file=reqs[i],
            internal_ordercommit=internal_ordercommit,
        )
        order_ids.append(order_id)

        db_order = db.order_proc.find_one({'_id': order_id})
        assert db_order is not None, order_id
        assert db_order['order'] is not None

        order_name = db_order['order'].get('multiorder_order_name')
        if i == 0:
            # must be lazy filled after creation of the 2-nd order
            assert order_name is None
        else:
            assert order_name == order_names[i]

        for j in range(i):  # check all previously created orders
            db_order = db.order_proc.find_one({'_id': order_ids[j]})
            assert db_order['order']['multiorder_order_name'] == order_names[j]
            assert db_order['order'].get('multiorder_order_number') == j


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=4,
    MAX_MULTIORDER_CONCURRENT_ORDERS=4,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
def test_ordercommit_multiorder_process_numeration_with_gap(
        db, taxi_protocol, load_json,
):
    # create 3 orders
    order_ids = [
        create_order_ok(load_json, taxi_protocol)[0],
        create_order_ok(load_json, taxi_protocol)[0],
        create_order_ok(load_json, taxi_protocol)[0],
    ]

    # finish the 2-nd order
    db.order_proc.find_and_modify(
        {'_id': order_ids[1], '_shard_id': 0},
        {'$set': {'order.status': 'finished'}},
    )

    # create the 4-th order
    order_ids.append(create_order_ok(load_json, taxi_protocol)[0])

    # check that 4-th order was numbered as 4-th (not 2-nd because of gap)
    for i, order_id in enumerate(order_ids):
        db_order = db.order_proc.find_one({'_id': order_id})

        order_name = db_order['order'].get('multiorder_order_name')
        exp_order_name = 'Заказ №{}'.format(i + 1)
        assert order_name == exp_order_name

        order_number = db_order['order'].get('multiorder_order_number')
        assert order_number == i


def check_name_number(db, order_id, name, number):
    db_order = db.order_proc.find_one({'_id': order_id})

    assert db_order['order'].get('multiorder_order_name') == name
    assert db_order['order'].get('multiorder_order_number') == number


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=3,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
def test_ordercommit_multiorder_process_no_repeated_processing(
        db, taxi_protocol, load_json,
):
    order_ids = [
        create_order_ok(load_json, taxi_protocol)[0],
        create_order_ok(load_json, taxi_protocol)[0],
    ]

    # remove multiorder fields from the db to check they won't be created again
    update_all = {
        '$unset': {
            'order.multiorder_order_name': True,
            'order.multiorder_order_number': True,
        },
    }
    update_name = {'$unset': {'order.multiorder_order_name': True}}
    db.order_proc.find_and_modify(
        {'_id': order_ids[0], '_shard_id': 0}, update_all,
    )
    db.order_proc.find_and_modify(
        {'_id': order_ids[1], '_shard_id': 0}, update_name,
    )

    last_order_id, _ = create_order_ok(load_json, taxi_protocol)

    check_name_number(db, order_ids[0], None, None)
    check_name_number(db, order_ids[1], None, 1)
    check_name_number(db, last_order_id, 'Заказ №3', 2)


@pytest.mark.config(
    MAX_CONCURRENT_ORDERS=3,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
def test_ordercommit_multiorder_process_on_timeout(
        db, taxi_protocol, load_json,
):
    order_id, _ = create_order_ok(load_json, taxi_protocol)

    # Simulate mongo timeout during order_proc creation:
    # order_proc was created,
    # commit_state='reserved' and order commit was restarted.
    # Buggy code can make multiorder from orders [order_id, order_id].
    update = {'$set': {'commit_state': 'reserved'}}
    db.orders.find_and_modify({'_id': order_id, '_shard_id': 0}, update)

    commit_resp = commit_order(taxi_protocol, load_json, order_id)
    assert commit_resp.status_code == 200

    check_name_number(db, order_id, None, None)

    # create the 2-nd order and check it
    order_id2, _ = create_order_ok(load_json, taxi_protocol)
    check_name_number(db, order_id, 'Заказ №1', 0)
    check_name_number(db, order_id2, 'Заказ №2', 1)


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=1,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.translations(
    client_messages={'multiorder.order_name.n1': {'ru': 'order_name_1'}},
)
def test_ordercommit_multiorder_process_numerical(
        db, taxi_protocol, load_json,
):
    """
    Checks that orders below MULTIORDER_NUMERAL_THRESHOLD_COUNT have numeral
    name from translations, otherwise default name like "Order #1"
    """

    def get_order_name(i):
        if i == 1:
            return 'order_name_{}'.format(i)
        else:
            return 'Заказ №{}'.format(i)

    order_ids = []
    for _ in range(2):
        order_id, _ = create_order_ok(load_json, taxi_protocol, req_file=None)
        order_ids.append(order_id)

    for i, order_id in enumerate(order_ids, start=1):
        db_order = db.order_proc.find_one({'_id': order_id})

        order_name = db_order['order'].get('multiorder_order_name')
        assert order_name == get_order_name(i)


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
def test_ordercommit_multiorder_process_zero_threshold(
        db, taxi_protocol, load_json,
):
    """
    Checks if MULTIORDER_NUMERAL_THRESHOLD_COUNT=0 then first order has a
    default name like "Order #1"
    """
    order_ids = []
    for _ in range(2):
        order_id, _ = create_order_ok(load_json, taxi_protocol, req_file=None)
        order_ids.append(order_id)

    db_order = db.order_proc.find_one({'_id': order_ids[0]})
    order_name = db_order['order'].get('multiorder_order_name')
    assert order_name == 'Заказ №1'


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_NUMERAL_THRESHOLD_COUNT=0,
    # mark user creating orders in this test as SVO user
    SVO_USER_ID='f4eb6aaa29ad4a6eb53f8a7620793561',
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_PROCESS_FOR_MULTIORDER_ON_ORDER_COMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_ordercommit_multiorder_no_processing_for_special_users(
        db, taxi_protocol, load_json,
):
    order_ids = []
    for _ in range(2):
        order_id, _ = create_order_ok(load_json, taxi_protocol)
        order_ids.append(order_id)

    for order_id in order_ids:
        db_order = db.order_proc.find_one({'_id': order_id})
        assert 'multiorder_order_name' not in db_order['order']


USER_PHONE_ID = bson.ObjectId('59246c5b6195542e9b084206')


@pytest.mark.config(
    MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N=2,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS_CHECK_COMPLETE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.parametrize(
    'complete,can_make_more',
    [(1, 'disallowed'), (2, 'allowed'), (3, 'allowed')],
)
def test_multiorder_can_make_more_antifraud(
        taxi_protocol, db, load_json, complete, can_make_more,
):
    db.user_phones.find_and_modify(
        {'_id': USER_PHONE_ID}, {'$set': {'stat.complete': complete}},
    )
    _, resp = create_order_ok(load_json, taxi_protocol)
    assert resp.json().get('can_make_more_orders') == can_make_more


@pytest.mark.config(
    MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N=2,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS_CHECK_COMPLETE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
def test_multiorder_antifraud_partial_order(taxi_protocol, db, load_json):
    db.user_phones.find_and_modify(
        {'_id': USER_PHONE_ID}, {'$set': {'stat.complete': 1}},
    )
    order_id = create_order_ok_expect_cmm(
        taxi_protocol, load_json, 'disallowed',
    )

    # emulate case of timeout to mongo during update of orders.commit_state
    # from reserved to done.
    db.orders.find_and_modify(
        {'_id': order_id, '_shard_id': 0},
        {'$set': {'commit_state': 'reserved'}},
    )

    # commit partially created order: check that we won't get error
    # NO_MULTIORDER (multiorder isn't allowed because too few complete orders)
    commit_resp = commit_order(taxi_protocol, load_json, order_id)
    assert commit_resp.status_code == 200
    assert commit_resp.json().get('can_make_more_orders') == 'disallowed'


@pytest.mark.config(
    MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N=2,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
def test_multiorder_can_make_more_antifraud_exp_disabled(
        taxi_protocol, db, load_json,
):
    db.user_phones.find_and_modify(
        {'_id': USER_PHONE_ID}, {'$set': {'stat.complete': 1}},
    )
    _, resp = create_order_ok(load_json, taxi_protocol)
    assert resp.json().get('can_make_more_orders') == 'allowed'


MIN_COMPLETE_ORDERS_CUSTOMIZATION_EXP = (
    pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N_CUSTOMIZATION',
        consumers=['ordercommit', 'protocol/ordercommit'],
        clauses=[
            {
                'title': '',
                'value': {'enabled': True, 'num_orders': 3},
                'predicate': {'type': 'true'},
            },
        ],
    ),
)


@pytest.mark.config(
    MULTIORDER_ENABLING_MIN_COMPLETE_ORDERS_N=2,
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS_CHECK_COMPLETE_ORDERS=True,
    MULTIORDER_ANTIFRAUD_AND_SPAM_ON_ORDERCOMMIT=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.translations(
    client_messages={
        'common_errors.MULTIORDER_DISALLOWED': {'ru': 'Мультизаказ отключен'},
    },
)
@pytest.mark.parametrize(
    'complete,status_code',
    [
        pytest.param(1, 406),
        pytest.param(2, 200),
        pytest.param(3, 200),
        pytest.param(2, 406, marks=MIN_COMPLETE_ORDERS_CUSTOMIZATION_EXP),
        pytest.param(4, 200, marks=MIN_COMPLETE_ORDERS_CUSTOMIZATION_EXP),
    ],
)
def test_multiorder_can_make_more_antifraud_commit(
        taxi_protocol, db, load_json, complete, status_code,
):
    db.user_phones.find_and_modify(
        {'_id': USER_PHONE_ID}, {'$set': {'stat.complete': complete}},
    )
    create_order_ok(load_json, taxi_protocol)  # only one order, no check

    _, resp = create_order(load_json, taxi_protocol)
    assert resp.status_code == status_code  # check only from the second order
    if status_code == 406:
        assert resp.json() == {
            'error': {
                'code': 'MULTIORDER_DISALLOWED',
                'text': 'Мультизаказ отключен',
            },
        }


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@pytest.mark.now('2018-08-08T16:00:00+0000')
def test_ordercommit_multiorder_corrected_limits(db, taxi_protocol, load_json):

    # create 2/3 orders
    order_ids = [
        create_order_ok(load_json, taxi_protocol)[0],
        create_order_ok(load_json, taxi_protocol)[0],
    ]

    def create_order_ok_expected(expected):
        return create_order_ok_expect_cmm(taxi_protocol, load_json, expected)

    def finish_order(order_id, updated_at=None):
        if updated_at is None:
            updated_at = datetime.datetime(2018, 8, 8, 16, 0, 0)
        db.order_proc.find_and_modify(
            {'_id': order_id, '_shard_id': 0},
            {
                '$set': {
                    'status': 'finished',
                    'order.status_updated': updated_at,
                },
            },
        )

    # check got disallowed on the last order creation
    last_order_id = create_order_ok_expected('disallowed')

    # check can't create more
    create_order_fail_limit(load_json, taxi_protocol)

    # finish order too past in time, shouldn't affect limits
    finish_order(last_order_id, datetime.datetime(2018, 8, 8, 15, 0, 0))
    create_order_fail_limit(load_json, taxi_protocol)

    # finish order now, should increase limit by one
    finish_order(last_order_id)
    create_order_ok_expected('disallowed')

    # finish 2 orders and check that we can create 2 another orders after that
    finish_order(order_ids[0])
    finish_order(order_ids[1])

    create_order_ok_expected('allowed')
    create_order_ok_expected('disallowed')
    create_order_fail_limit(load_json, taxi_protocol)


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=2,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
)
@pytest.mark.now('2018-08-08T16:00:00+0000')
def test_ordercommit_multiorder_corrected_limits_no_experiment(
        db, taxi_protocol, load_json,
):
    def create_order_ok_expected(expected):
        return create_order_ok_expect_cmm(taxi_protocol, load_json, expected)

    def finish_order(order_id, updated_at=None):
        if updated_at is None:
            updated_at = datetime.datetime(2018, 8, 8, 16, 0, 0)
        db.order_proc.find_and_modify(
            {'_id': order_id, '_shard_id': 0},
            {
                '$set': {
                    'status': 'finished',
                    'order.status_updated': updated_at,
                },
            },
        )

    first_order_id = create_order_ok_expected('allowed')
    finish_order(first_order_id)

    # check got disallowed on the last order creation
    last_order_id = create_order_ok_expected('disallowed')
    finish_order(last_order_id)

    # check can't create more
    create_order_fail_limit(load_json, taxi_protocol)


FRANCE_IP = '89.185.38.136'


@pytest.mark.config(
    MAX_MULTIORDER_CONCURRENT_ORDERS=3,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_CALC_CAN_MAKE_MORE_ORDERS=True,
    MULTIORDER_CORRECT_MULTIORDER_LIMITS=True,
)
@pytest.mark.parametrize(
    'remote_ip,allowed_countries,expected_res',
    [
        (FRANCE_IP, None, 'allowed'),
        (FRANCE_IP, ['ru', 'us'], 'disallowed'),
        (FRANCE_IP, ['fr'], 'allowed'),
    ],
)
def test_multiorder_by_country(
        remote_ip,
        allowed_countries,
        expected_res,
        taxi_protocol,
        load_json,
        config,
):

    use_by_country_check = allowed_countries is not None
    config.set_values(dict(MULTIORDER_ENABLE_BY_COUNTRY=use_by_country_check))
    config.set_values(dict(MULTIORDER_ENABLED_COUNTRIES=allowed_countries))

    create_order_ok_expect_cmm(
        taxi_protocol, load_json, expected_res, x_real_ip=remote_ip,
    )
    if expected_res == 'allowed':
        create_order_ok(load_json, taxi_protocol, x_real_ip=remote_ip)
    else:
        create_order_fail_limit(load_json, taxi_protocol, x_real_ip=remote_ip)


def make_afs_is_spammer_true_response_builder(add_sec_to_block_time=0):
    def response_builder(now):
        blocked_until = now + datetime.timedelta(seconds=add_sec_to_block_time)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    return response_builder


def afs_is_spammer_true_response_no_time_builder(_):
    return {'is_spammer': True}


def afs_is_spammer_false_response_builder(_):
    return {'is_spammer': False}


MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE = (
    'Мультизаказ недоступен из-за частых отмен'
)


def make_multiorder_disallowed_in_duration_err(duration):
    prefix = MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE + ', попробуйте через '
    return prefix + duration


@pytest.mark.translations(
    client_messages={
        'common_errors.MULTIORDER_DISALLOWED_FOR_SPAMMER': {
            'ru': MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        },
        'common_errors.MULTIORDER_DISALLOWED_FOR_SPAMMER_WITH_DURATION': {
            'ru': (
                MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE
                + ', попробуйте через %(unblock_after_duration)s'
            ),
        },
    },
    tariff={
        'round.minute': {'ru': '%(value).0f мин'},
        'round.hours': {'ru': '%(value).0f ч'},
    },
)
@pytest.mark.config(
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    MULTIORDER_LIMITS_ENABLED=True,
    MULTIORDER_ANTIFRAUD_CHECK_IS_NOT_SPAMMER=True,
    MULTIORDER_ANTIFRAUD_AND_SPAM_ON_ORDERCOMMIT=True,
    APPLICATION_MAP_BRAND={'__default__': 'yataxi', 'android': 'yataxi'},
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'afs_resp_builder,exp_error_text',
    [
        (
            make_afs_is_spammer_true_response_builder(0),
            make_multiorder_disallowed_in_duration_err('1 мин'),
        ),
        (
            make_afs_is_spammer_true_response_builder(-1),
            make_multiorder_disallowed_in_duration_err('1 мин'),
        ),
        (
            make_afs_is_spammer_true_response_builder(60 * 60 * 4),
            make_multiorder_disallowed_in_duration_err('4 ч'),
        ),
        (
            afs_is_spammer_true_response_no_time_builder,
            MUTLTIORDER_DISALLOWED_SPAMMER_ERR_BASE,
        ),
        (afs_is_spammer_false_response_builder, None),
    ],
)
def test_multiorder_is_spammer_check(
        taxi_protocol,
        load_json,
        mockserver,
        now,
        afs_resp_builder,
        exp_error_text,
):
    create_order_ok(load_json, taxi_protocol)

    order_id = create_draft(load_json, taxi_protocol)

    @mockserver.json_handler('/antifraud/client/user/is_spammer')
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'order_id': order_id,
            'is_multiorder': True,
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            'user_phone_id': '59246c5b6195542e9b084206',
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
        }
        return afs_resp_builder(now)

    resp = commit_order(taxi_protocol, load_json, order_id)
    if exp_error_text is None:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 406
        assert resp.json() == {
            'error': {
                'code': 'MULTIORDER_DISALLOWED_FOR_SPAMMER',
                'text': exp_error_text,
            },
        }


@pytest.mark.config(BILLING_PERSONAL_WALLET_ENABLED=True)
def test_personal_wallet(taxi_protocol, load_json, mockserver, db):
    order_id, resp = create_order(
        load_json, taxi_protocol, 'personal_wallet_request.json',
    )
    assert resp.status_code == 406


@pytest.mark.parametrize(
    'config_override',
    [None, ({'IGNORED_MODIFIER_BY_REQUIREMENTS': ['hourly_rental']})],
)
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('ya_plus')
def test_ignore_ya_plus_by_requirements(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        config,
        config_override,
        pricing_data_preparer,
):
    if config_override is not None:
        config.set_values(config_override)

    db.order_offers.remove({})
    order_id, resp = create_order_ok(
        load_json,
        taxi_protocol,
        'ignore_ya_plus_by_requirements_request.json',
    )

    order_proc = db.order_proc.find_one({'_id': order_id})

    if config_override:
        assert 'price_modifiers' not in order_proc
    else:
        assert 'price_modifiers' in order_proc


@pytest.mark.filldb(order_proc='rollback')
def test_rollback(taxi_protocol, db, mock_stq_agent):
    request = {'id': 'user_id', 'orderid': 'order_id'}
    resp = taxi_protocol.post('/3.0/ordercommit', request)
    assert resp.status_code == 406
    assert resp.json() == {'error': {'code': 'ORDER_NOT_FOUND'}}

    support_commit_tasks = mock_stq_agent.get_tasks('support_commit')
    assert len(support_commit_tasks) == 1

    processing_tasks = mock_stq_agent.get_tasks('processing', 'order_id')
    assert len(processing_tasks) == 0

    request['check_unfinished_commit'] = True
    resp = taxi_protocol.post('/internal/ordercommit', request)
    assert resp.status_code == 200
    proc = db.order_proc.find_one({'_id': 'order_id'})
    assert proc['commit_state'] == 'init'
    assert proc['status'] == 'draft'


@pytest.mark.parametrize('enable_freecancel', [False, True])
def test_last_freecancel_usage(
        taxi_protocol, load_json, db, config, enable_freecancel,
):
    if enable_freecancel:
        config.set_values(dict(FREE_CANCEL_FOR_REASON_MIN_INTERVAL=1))
        taxi_protocol.invalidate_caches()

    order_id, resp = create_order_ok(
        load_json, taxi_protocol, 'last_freecancel_request.json',
    )
    assert resp.status_code == 200

    order_proc = db.order_proc.find_one({'_id': order_id})
    assert order_proc['free_cancel_for_reason'] == enable_freecancel


@pytest.mark.translations(
    client_messages={
        'common_errors.CASH_RESTRICTED_BY_TAGS': {
            'en': 'Cash option is not available: driver rides from afar',
        },
    },
)
@pytest.mark.parametrize('ordercommit_fetch_user_tags', [False, True])
@pytest.mark.parametrize('user_has_restricting_tags', [False, True])
def test_cash_restricting_user_tags(
        config,
        taxi_protocol,
        load_json,
        mockserver,
        ordercommit_fetch_user_tags,
        user_has_restricting_tags,
        mock_stq_agent,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def mock_tags(tags_request):
        assert ordercommit_fetch_user_tags

        req_body = json.loads(tags_request.get_data())
        if ordercommit_fetch_user_tags:
            assert req_body['match'] == [
                {
                    'type': 'user_id',
                    'value': 'f4eb6aaa29ad4a6eb53f8a7620793561',
                },
                {'type': 'user_phone_id', 'value': '59246c5b6195542e9b084206'},
                {'type': 'yandex_uid', 'value': '4003514353'},
            ]
        user_tags = []
        if user_has_restricting_tags:
            user_tags = ['cash_restriction_tag']
        return {'tags': user_tags}

    config.set_values(
        dict(
            ORDER_COMMIT_FETCH_USER_TAGS=ordercommit_fetch_user_tags,
            CASH_RESTRICTING_USER_TAGS={
                '__default__': {'__default__': ['cash_restriction_tag']},
            },
        ),
    )

    commit_restricted = (
        ordercommit_fetch_user_tags and user_has_restricting_tags
    )

    _, commit_resp = create_order(load_json, taxi_protocol)

    if commit_restricted:
        assert commit_resp.status_code == 406
        assert commit_resp.json() == {
            'error': {
                'code': 'CASH_RESTRICTED_BY_TAGS',
                'text': 'Cash option is not available: driver rides from afar',
            },
        }
        return

    assert commit_resp.status_code == 200


@pytest.mark.parametrize('cargo_order', [False, True])
@pytest.mark.usefixtures('pricing_data_preparer')
def test_virtual_tariffs_match(
        taxi_protocol, load_json, mockserver, db, virtual_tariffs, cargo_order,
):
    draft_request = load_json('basic_request.json')
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    cargo_ref_id = 'f7793a14a2e94cd78dbdb2831476aafc'
    if cargo_order:
        db.order_proc.update(
            {'_id': order_id},
            {'$set': {'order.request.cargo_ref_id': cargo_ref_id}},
        )

    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def _mock_virtual_tariffs(request):
        assert request.json['cargo_ref_id'] == cargo_ref_id
        assert 'corp_client_id' not in request.json
        return {'virtual_tariffs': []}

    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert response.status_code == 200

    if cargo_order:
        _mock_virtual_tariffs.times_called == 1
    else:
        _mock_virtual_tariffs.times_called == 0


@pytest.mark.translations(
    client_messages={
        'common_errors.NO_USER_EMAIL': {'en': 'User should set email'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='check_user_email_for_countries',
    consumers=['protocol/ordercommit'],
    clauses=[
        {
            'title': '',
            'value': {'enabled': True, 'countries': ['rus']},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize('no_email', [True, False])
def test_no_user_email_in_selected_country(
        config, taxi_protocol, load_json, mockserver, no_email,
):
    @mockserver.json_handler('/user-api/user_emails/get')
    def mock_user_api_user_emails_get(request):
        if no_email:
            return {'items': []}
        else:
            return {
                'items': [
                    {
                        'personal_email_id': 'test_personal_email_id',
                        'confirmed': True,
                        'confirmation_code': 'test_confirmation_code',
                    },
                ],
            }

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    _, commit_resp = create_order(load_json, taxi_protocol)

    if no_email:
        assert commit_resp.status_code == 406
        assert commit_resp.json() == {
            'error': {
                'code': 'NO_USER_EMAIL',
                'text': 'User should set email',
            },
        }
    else:
        assert commit_resp.status_code == 200


@pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
def test_ordercommit_use_order_core(
        taxi_protocol,
        mockserver,
        load_json,
        mock_stq_agent,
        mock_order_core,
        db,
):
    req = load_json('basic_request.json')

    # 1. create draft
    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    # 2. commit it once successfully
    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    assert resp.json()['orderid'] == order_id
    assert resp.json()['status'] == 'search'
    check_support_commit(order_id, mock_stq_agent)
    assert mock_order_core.post_event_times_called == 1
    assert not mock_stq_agent.get_tasks('processing')
    proc = db.order_proc.find_one({'_id': order_id})
    assert proc is not None
    events = proc['order_info']['statistics']['status_updates']
    assert len(events) == 1
    created_event = events[0]
    assert created_event['q'] == 'create'


@pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
@ORDER_OFFERS_MATCH_COMPARE_SWITCH
@ORDER_OFFERS_MATCH_SWITCH
@pytest.mark.now('2022-06-06T16:00:00+0300')
def test_ordercommit_use_order_offers(
        taxi_protocol,
        load_json,
        db,
        mock_order_offers,
        order_offers_match_compare_enabled,
        order_offers_match_enabled,
):
    req = load_json('basic_request.json')

    # Matching logic is incapsulated inside order-offers service for the new
    # flow, so we need to explicitly specify offer id to be matched.
    mock_order_offers.set_offer_to_match('nonfixed_price_upgrade')

    # 1. create draft
    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    # 2. commit it once successfully
    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    assert resp.json()['orderid'] == order_id
    assert resp.json()['status'] == 'search'

    order_offers_should_be_called = (
        order_offers_match_compare_enabled or order_offers_match_enabled
    )
    mock_order_offers.mock_match_offer.times_called == (
        1 if order_offers_should_be_called else 0
    )
    if order_offers_should_be_called:
        match_request = mock_order_offers.last_match_request
        assert match_request == {
            'filters': {
                'order': {
                    'classes': ['econom'],
                    # +10 minutes from mocked now moment
                    'due': datetime.datetime(2022, 6, 6, 13, 10, 0),
                    'requirements': {},
                    'route': [[37.61672446877377, 55.75774301935856]],
                },
                'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
            },
        }


@pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
@pytest.mark.parametrize(
    'store_user_experiments_enabled',
    [
        pytest.param(True),
        pytest.param(
            True,
            marks=[
                pytest.mark.experiments3(
                    filename=(
                        'disable_store_user_experiments_to_order_error.json'
                    ),
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.experiments3(
                    filename=(
                        'disable_store_user_experiments_to_order_enabled.json'
                    ),
                ),
            ],
        ),
    ],
)
def test_ordercommit_no_user_experiments(
        taxi_protocol,
        mockserver,
        load_json,
        mock_stq_agent,
        db,
        store_user_experiments_enabled,
):
    req = load_json('basic_request.json')

    # 1. create draft
    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    # 2. commit it once successfully
    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200
    assert resp.json()['orderid'] == order_id
    assert resp.json()['status'] == 'search'

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc is not None
    if store_user_experiments_enabled:
        assert proc['order']['user_experiments'] == [
            'divining_point_b',
            'userplaces_in_b',
        ]
    else:
        assert 'user_experiments' not in proc['order']


@pytest.mark.translations(
    client_messages={
        'common_errors.DELIVERY_RESTRICTED': {
            'ru': 'Международные поездки запрещены',
        },
    },
)
@pytest.mark.usefixtures('pricing_data_preparer')
@pytest.mark.parametrize(
    ('cargo_matcher_response', 'expected_status'),
    [
        pytest.param(
            {'status': 200, 'json': {'forbidden_tariffs': []}},
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
            None,
            200,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': False,
                    'fallback_enabled': True,
                    'restricted_countries': [],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='only fallback no restrictions',
        ),
        pytest.param(
            {
                'status': 200,
                'json': {
                    'forbidden_tariffs': [
                        {
                            'prohibition_reason': (
                                'estimating.'
                                'international_orders_prohibition_to_kg'
                            ),
                            'tariff': 'econom',
                        },
                    ],
                },
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
        pytest.param(
            None,
            406,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': False,
                    'fallback_enabled': True,
                    'restricted_countries': ['kaz'],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
        ),
        # only cargo-matcher priority
        pytest.param(
            {'status': 200, 'json': {'forbidden_tariffs': []}},
            200,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': ['kaz'],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='only cargo-matcher priority',
        ),
        pytest.param(
            {
                'status': 200,
                'json': {
                    'forbidden_tariffs': [
                        {
                            'prohibition_reason': (
                                'estimating.'
                                'international_orders_prohibition_to_kg'
                            ),
                            'tariff': 'econom',
                        },
                    ],
                },
            },
            406,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': [],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='cargo-matcher restricted fallback ignore',
        ),
        pytest.param(
            {'status': 200, 'json': {}},
            406,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': ['kaz'],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='fallback after matcher 1',
        ),
        pytest.param(
            {'status': 200, 'json': {}},
            406,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': ['rus'],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='fallback after matcher 2',
        ),
        pytest.param(
            {'status': 500, 'json': {}},
            200,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': [],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='cargo-matcher error fallback allowed 1',
        ),
        pytest.param(
            {'status': 401, 'json': {}},
            200,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': [],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='cargo-matcher error fallback allowed 2',
        ),
        pytest.param(
            {'status': 500, 'json': {}},
            406,
            marks=pytest.mark.config(
                CARGO_PROTOCOL_RESTRICTIONS_CHECK_SETTINGS={
                    'cargo_matcher_enabled': True,
                    'fallback_enabled': True,
                    'restricted_countries': ['kaz'],
                    'tariff_classes_for_check': ['econom'],
                },
            ),
            id='cargo-matcher error fallback not allowed',
        ),
    ],
)
def test_delivery_restrictions(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        cargo_matcher_response,
        expected_status,
):
    draft_request = load_json('basic_request.json')
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.destinations': [
                    {
                        'description': 'площадь Республики',
                        'fullname': 'Казахстан, Алматы, площадь Республики',
                        'geopoint': [76.945627, 43.237163],
                        'method': 'fs_finalize_uri',
                        'metrica_action': 'addressCorrection',
                        'metrica_method': 'suggest',
                        'passed': False,
                        'short_text': 'площадь Республики',
                        'type': 'address',
                    },
                ],
            },
        },
    )
    if cargo_matcher_response:

        @mockserver.json_handler('/cargo_matcher/v1/routes-prohibition')
        def _mock_cargo_matcher(request):
            assert request.json == {
                'route_points': [
                    {'coordinates': [37.61672446877377, 55.75774301935856]},
                    {'coordinates': [76.945627, 43.237163]},
                ],
                'tariffs': ['econom'],
            }
            return mockserver.make_response(
                status=cargo_matcher_response['status'],
                response=json.dumps(cargo_matcher_response['json']),
            )

    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', commit_request)

    if cargo_matcher_response:
        assert _mock_cargo_matcher.times_called
    assert response.status_code == expected_status
    if expected_status == 406:
        assert response.json() == {
            'error': {
                'code': 'DELIVERY_RESTRICTED',
                'text': 'Международные поездки запрещены',
            },
        }


@pytest.mark.config(CARGO_ORDERS_RETRIEVE_PRICING_DATA_ON_COMMIT=True)
@pytest.mark.usefixtures('pricing_data_preparer')
def test_cargo_fixed_price(taxi_protocol, load_json, mockserver, db):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    @mockserver.json_handler('/cargo_orders/v1/retrieve-pricing-data')
    def mock_cargo_orders(request):
        return {
            'order_info': {
                'destination': {'point': [37.2, 55.2]},
                'source': {'point': [37.1, 55.1]},
            },
            'taxi_pricing_response': {
                'taximeter_metadata': {
                    'max_distance_from_point_b': 1000.1,
                    'show_price_in_taximeter': True,
                },
                'driver': {
                    'additional_prices': {
                        'paid_supply': {
                            'price': {'total': 1000.12},
                            'meta': {'paid_supply_price': 1000.12},
                        },
                    },
                },
            },
            'receipt': {'total': 999.1, 'total_distance': 1000},
            'offer_expectations': {
                'seconds_to_arrive': 100,
                'meters_to_arrive': 101,
            },
        }

    draft_request = load_json('basic_request.json')
    draft_request['cargo_ref_id'] = 'some_cargo_ref_id'
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    commit_response = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert commit_response.status_code == 200

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['order']['fixed_price'] == {
        'destination': [37.2, 55.2],
        'driver_price': 999.1,
        'max_distance_from_b': 1000,
        'paid_supply_price': 1000.12,
        'price': 999.1,
        'price_original': 999.1,
        'show_price_in_taximeter': True,
        'paid_supply_info': {'distance': 101, 'time': 100},
    }


@pytest.mark.config(CARGO_ORDERS_RETRIEVE_PRICING_DATA_ON_COMMIT=True)
@pytest.mark.usefixtures('pricing_data_preparer')
def test_cargo_card_flow(taxi_protocol, load_json, mockserver, db):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    @mockserver.json_handler('/cargo_orders/v1/retrieve-pricing-data')
    def mock_cargo_orders(request):
        return {
            'order_info': {
                'destination': {'point': [37.2, 55.2]},
                'source': {'point': [37.1, 55.1]},
            },
            'taxi_pricing_response': {
                'taximeter_metadata': {
                    'max_distance_from_point_b': 1000.1,
                    'show_price_in_taximeter': True,
                },
                'driver': {
                    'additional_prices': {
                        'paid_supply': {
                            'price': {'total': 1000.12},
                            'meta': {'paid_supply_price': 1000.12},
                        },
                    },
                },
            },
            'receipt': {'total': 999.1, 'total_distance': 1000},
            'offer_expectations': {
                'seconds_to_arrive': 100,
                'meters_to_arrive': 101,
            },
        }

    @mockserver.json_handler('/cardstorage/v1/card')
    def mock_cardstorage(request):
        return mockserver.make_response('error', 500)

    @mockserver.json_handler('/statistics_agent/v1/fallbacks/state')
    def mock_statistics_agent(request):
        return {
            'service_name': 'protocol',
            'fallbacks': [
                {'name': 'protocol.reserve_card.fallback', 'value': True},
            ],
        }

    draft_request = load_json('basic_request.json')
    draft_request['cargo_ref_id'] = 'some_cargo_ref_id'
    draft_request['payment'] = {
        'type': 'card',
        'payment_method_id': 'card-x5618',
    }
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    commit_response = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert commit_response.status_code == 200

    assert mock_cardstorage.times_called == 0

    proc = db.order_proc.find_one({'_id': order_id})
    assert proc['payment_tech']['main_card_billing_id'] == 'x5618'


@pytest.mark.translations(
    client_messages={
        'common_errors.ROUTE_OVER_CLOSED_BORDER': {
            'ru': 'Международные поездки запрещены',
        },
    },
)
@pytest.mark.usefixtures('pricing_data_preparer')
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
def test_route_restrictions(
        taxi_protocol, load_json, mockserver, db, expected_status,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    draft_request = load_json('basic_request.json')
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.destinations': [
                    {
                        'description': 'площадь Республики',
                        'fullname': 'Казахстан, Алматы, площадь Республики',
                        'geopoint': [76.945627, 43.237163],
                        'method': 'fs_finalize_uri',
                        'metrica_action': 'addressCorrection',
                        'metrica_method': 'suggest',
                        'passed': False,
                        'short_text': 'площадь Республики',
                        'type': 'address',
                    },
                ],
            },
        },
    )
    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert response.status_code == expected_status
    if expected_status == 406:
        assert response.json() == {
            'error': {
                'code': 'ROUTE_OVER_CLOSED_BORDER',
                'text': 'Международные поездки запрещены',
            },
        }


@pytest.mark.translations(
    client_messages={
        'common_errors.ROUTE_OVER_CLOSED_BORDER': {
            'ru': 'Международные поездки запрещены',
        },
    },
)
@pytest.mark.usefixtures('pricing_data_preparer')
@pytest.mark.config(
    ROUTE_COUNTRY_BORDER_RESTRICTIONS={
        'enabled': True,
        'restricted_countries': [],
        'block_on_exception': True,
    },
)
def test_route_restrictions_missing_tariff_settings(
        taxi_protocol, load_json, mockserver, db,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    draft_request = load_json('basic_request.json')
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.destinations': [
                    {
                        'description': 'Malmi, Helsinki, Uusimaa, Suomi',
                        'fullname': (
                            'Suomi, Uusimaa, Helsinki, Malmi, Maasalvantie, 8'
                        ),
                        # В тесте координаты по котором нет данных
                        # в geoindex, поэтому мы не находим страну через
                        # tariff_settings и ищем через geobase
                        'geopoint': [25.008918, 60.237073],
                        'method': 'fs_finalize_uri',
                        'metrica_action': 'addressCorrection',
                        'metrica_method': 'suggest',
                        'passed': False,
                        'short_text': 'Maasalvantie, 8',
                        'type': 'address',
                    },
                ],
            },
        },
    )
    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    response = taxi_protocol.post('3.0/ordercommit', commit_request)
    # no errors despite block_on_exception=True
    # because we resolve point in geobase as fallback
    assert response.status_code == 200


def test_combo_express_order(taxi_protocol, load_json, mockserver, db):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    draft_request = load_json('basic_request.json')
    draft_request['alternative_type'] = 'combo_order'
    draft_resp = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_resp.status_code == 200

    order_id = draft_resp.json()['orderid']
    commit_request = {'id': draft_request['id'], 'orderid': order_id}
    commit_response = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert commit_response.status_code == 200

    proc = db.order_proc.find_one({'_id': order_id})

    assert proc['order']['request']['alternative_type'] == 'combo_order'
    assert proc['order']['request']['class_options'] == {'strong_mode': True}


# @pytest.mark.config(SURGE_CREATE_PIN_WITH_ORDER=True)
def test_intercity(taxi_protocol, db, mockserver, load_json):
    req = load_json('basic_request.json')
    req['offer'] = 'intercity_offer_id'

    # 1. create draft
    draft_resp = taxi_protocol.post('3.0/orderdraft', req)
    assert draft_resp.status_code == 200
    order_id = draft_resp.json()['orderid']

    commit_request = {'id': req['id'], 'orderid': order_id}

    # 2. commit it once successfully
    resp = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert resp.status_code == 200

    order_proc = db.order_proc.find_one({'_id': order_id})
    assert order_proc is not None

    order = order_proc['order']
    intercity = order['intercity']
    assert intercity['enabled'] is True
