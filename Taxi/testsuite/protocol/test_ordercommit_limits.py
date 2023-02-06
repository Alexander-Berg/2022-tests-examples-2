import bson
import pytest


ORDERDRAFT_URL = '3.0/orderdraft'
ORDERCOMMIT_URL = '3.0/ordercommit'
ORDERFROMPROC_URL = 'internal/orderfromproc'
NOW_TIMESTAMP = 1483228800  # '2017-01-01T00:00:00.000Z'


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
def test_ordercommit_ok(taxi_protocol, mockserver, db, pricing_data_preparer):
    """Check handler call with normal data. That return 200, not 500"""
    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848c',
    }

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200
    proc = db.order_proc.find_one({'_id': '272fbd2b67b0bb9c5135d71d1d1a848c'})
    assert proc is not None
    assert proc['order']['status'] == 'pending'
    assert proc['order']['referral_id'] == 'referral_id'
    assert proc['order']['referral_timestamp'] is not None
    assert proc['order_info']['need_sync'] is True


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
def test_ordercommit_phone_limit_failed(
        taxi_protocol, mockserver, mock_solomon,
):
    _mock_surge(mockserver)

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

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 429

    mock_solomon.wait_for()


def get_order_restriction_settings_mark(
        max_pending=2, enabled=True, use_order_core='disabled',
):
    return pytest.mark.config(
        ORDER_RESTRICTION_SETTINGS={
            'enabled': enabled,
            'max_pending_orders': max_pending,
        },
        ORDER_RESTRICTION_USE_ORDER_CORE=use_order_core,
    )


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.config(MAX_CONCURRENT_ORDERS=5)
@pytest.mark.config(MAX_CONCURRENT_CARD_ORDERS=5)
@pytest.mark.parametrize(
    'expected_status_code',
    [
        pytest.param(
            200,
            id='Under limit, native',
            marks=get_order_restriction_settings_mark(),
        ),
        pytest.param(
            429,
            id='Limit exceeded, native',
            marks=get_order_restriction_settings_mark(max_pending=1),
        ),
        pytest.param(
            200,
            id='Under limit, order-core',
            marks=get_order_restriction_settings_mark(
                use_order_core='enabled',
            ),
        ),
        pytest.param(
            429,
            id='Limit exceeded, order-core',
            marks=get_order_restriction_settings_mark(
                use_order_core='enabled',
            ),
        ),
        pytest.param(
            200,
            id='Under limit, fallback',
            marks=get_order_restriction_settings_mark(
                use_order_core='check_mode',
            ),
        ),
        pytest.param(
            429,
            id='Limit exceeded, fallback',
            marks=get_order_restriction_settings_mark(
                max_pending=1, use_order_core='check_mode',
            ),
        ),
    ],
)
def test_ordercommit_city_limit_failed(
        taxi_protocol,
        load,
        mockserver,
        taxi_config,
        mock_solomon,
        pricing_data_preparer,
        expected_status_code,
):
    max_count = taxi_config.get('ORDER_RESTRICTION_SETTINGS')[
        'max_pending_orders'
    ]
    current_count = 0

    @mockserver.json_handler('/order-core/internal/stats/v1/can-commit-order')
    def mock_can_commit(request):
        nonlocal current_count
        current_count += 1
        if expected_status_code == 429 and current_count >= max_count:
            can_commit = False
        else:
            can_commit = True
        return {'can_commit': can_commit}

    pricing_data_preparer.set_locale('ru')

    ORDER_ID_1 = '272fbd2b67b0bb9c5135d71d1d1a848b'
    ORDER_ID_2 = '272fbd2b67b0bb9c5135d71d1d1a848c'
    request = {'id': '0c1dd6723153692ec43a5827e3603ac9', 'orderid': ORDER_ID_1}

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    response = taxi_protocol.post(ORDERFROMPROC_URL, request)
    assert response.status_code == 200

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

    request = {'id': '0c1dd6723153692ec43a5827e3603ac9', 'orderid': ORDER_ID_2}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)

    assert response.status_code == expected_status_code
    if expected_status_code == 429:
        mock_solomon.wait_for()

    if taxi_config.get('ORDER_RESTRICTION_USE_ORDER_CORE') != 'disabled':
        assert mock_can_commit.wait_call()


@pytest.mark.now(NOW_TIMESTAMP)
@pytest.mark.parametrize(
    'expected_status_code',
    [
        pytest.param(
            200,
            id='Under limit, native',
            marks=get_order_restriction_settings_mark(),
        ),
        pytest.param(
            429,
            id='Limit exceeded, native',
            marks=get_order_restriction_settings_mark(max_pending=1),
        ),
        pytest.param(
            200,
            id='Under limit, order-core',
            marks=get_order_restriction_settings_mark(
                use_order_core='enabled',
            ),
        ),
        pytest.param(
            429,
            id='Limit exceeded, order-core',
            marks=get_order_restriction_settings_mark(
                use_order_core='enabled',
            ),
        ),
        pytest.param(
            200,
            id='Under limit, fallback',
            marks=get_order_restriction_settings_mark(
                use_order_core='check_mode',
            ),
        ),
        pytest.param(
            429,
            id='Limit exceeded, fallback',
            marks=get_order_restriction_settings_mark(
                max_pending=1, use_order_core='check_mode',
            ),
        ),
    ],
)
def test_orderdraft_city_limit_failed(
        taxi_protocol,
        load,
        load_json,
        mockserver,
        taxi_config,
        mock_solomon,
        pricing_data_preparer,
        expected_status_code,
):
    max_count = taxi_config.get('ORDER_RESTRICTION_SETTINGS')[
        'max_pending_orders'
    ]
    current_count = 0

    @mockserver.json_handler('/order-core/internal/stats/v1/can-commit-order')
    def mock_can_commit(request):
        nonlocal current_count
        current_count += 1
        if expected_status_code == 429 and current_count >= max_count:
            can_commit = False
        else:
            can_commit = True
        return {'can_commit': can_commit}

    pricing_data_preparer.set_locale('ru')

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    response = taxi_protocol.post(ORDERFROMPROC_URL, request)
    assert response.status_code == 200

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

    request = load_json('basic_request.json')
    response = taxi_protocol.post(ORDERDRAFT_URL, request)
    assert response.status_code == expected_status_code

    if expected_status_code == 429:
        mock_solomon.wait_for()

    if taxi_config.get('ORDER_RESTRICTION_USE_ORDER_CORE') != 'disabled':
        assert mock_can_commit.wait_call()


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
def test_ordercommit_nosurge(taxi_protocol, mockserver, db):
    """
    Check handler call with normal data.
    That return 500, when surger not available
    """

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return mockserver.make_response(status=404)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848c',
    }

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 500


def test_partially_committed_order(
        taxi_protocol, db, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1aaaac',
    }

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200
    order = db.orders.find_one({'_id': request['orderid']})
    assert order is None
    proc = db.order_proc.find_one({'_id': request['orderid']})
    assert proc['commit_state'] == 'done'


def test_orderlocks_for_old_client(
        taxi_protocol, db, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    # a case with invalid payment information within an order request:
    # non-null payment_method_id for 'cash' type of payment
    request = {
        'id': '13c01c8543eaaa3af024517053a4051d',
        'orderid': '82862422308c4055302adca1b248ea6a',
    }

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    # ensure that order not marked as 'unpaid' in the phonelock
    plock = db.phonelocks.find_one(
        {'i': bson.ObjectId('b63047b9fa7c992edb826183')},
    )
    assert plock is not None
    assert plock.get('x') is None
    assert plock.get('o') == ['82862422308c4055302adca1b248ea6a']

    # ensure that order not marked as 'unpaid' in the devicelock
    dlock = db.devicelocks.find_one({'i': '13c01c8543eaaa3af024517053a4051d'})
    assert dlock is not None
    assert dlock.get('x') is None
    assert dlock.get('o') == ['82862422308c4055302adca1b248ea6a']

    # ensure that cardlock is not set for the order
    clock = db.cardlocks.find(
        {
            '$or': [
                {'x': '82862422308c4055302adca1b248ea6a'},
                {'o': '82862422308c4055302adca1b248ea6a'},
            ],
        },
    )
    assert list(clock) == []


@pytest.mark.config(MULTIORDER_LIMITS_ENABLED=False)
def test_partner_limits(
        taxi_protocol, db, mockserver, pricing_data_preparer, testpoint,
):
    @testpoint('LoadOrderLimits')
    def handle_test_point(data):
        assert data == {
            'max_orders_per_phone': 5,
            'max_orders_per_device': 100500,
            'max_orders_per_card': 1000,
            'max_unpaid_orders': 1,
        }

    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    db.order_proc.update(
        {'_id': '82862422308c4055302adca1b248ea6a'},
        {
            '$set': {
                'order.statistics.application': 'partner',
                'order.operator_login': 'vasya',
            },
        },
    )
    db.users_order_count.insert(
        {
            '_id': 'vasya',
            'count': 1,
            'orders': ['82862422308c4055302adca1b248ea6a'],
        },
    )

    request = {
        'id': '13c01c8543eaaa3af024517053a4051d',
        'orderid': '82862422308c4055302adca1b248ea6a',
    }

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200
    assert handle_test_point.times_called == 1


def _mock_surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }
