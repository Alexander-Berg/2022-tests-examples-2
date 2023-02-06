import bson
import pytest


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
def test_ordercommit_internal(
        taxi_protocol, mockserver, db, pricing_data_preparer,
):
    """Check handler call with normal data. That return 200, not 500"""

    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848c',
    }

    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 200
    proc = db.order_proc.find_one({'_id': '272fbd2b67b0bb9c5135d71d1d1a848c'})
    assert proc is not None
    assert proc['order']['status'] == 'pending'
    assert proc['order']['referral_id'] == 'referral_id'
    assert proc['order']['referral_timestamp'] is not None
    assert proc['order_info']['need_sync'] is True


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
@pytest.mark.config(MAX_CONCURRENT_CARD_ORDERS=1)
@pytest.mark.config(MAX_CONCURRENT_CARD_ORDERS=1)
@pytest.mark.config(MAX_ORDERS_PER_CARD=1)
def test_ordercommit_limits(taxi_protocol, mockserver, pricing_data_preparer):
    pricing_data_preparer.set_locale('ru')
    """
    Check that limits sent in json have more priority than existing
    """

    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
        'max_orders_per_phone': 2,
        'max_orders_per_device': 2,
        'max_unpaid_orders': 2,
        'max_orders_per_card': 2,
    }
    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 200


@pytest.mark.config(BILLING_AUTOMATIC_FALLBACK_ENABLED=False)
@pytest.mark.parametrize(
    'billing_status,expected_commit_state,expected_status,order_fallback',
    [
        ('billing-ok', 'init', 'draft', True),
        ('billing-fail', 'done', 'pending', True),
        ('billing-ok', 'init', 'draft', False),
        ('billing-fail', 'init', 'draft', False),
    ],
)
@pytest.mark.filldb()
def test_billing_autofallback(
        billing_status,
        expected_commit_state,
        expected_status,
        order_fallback,
        mockserver,
        taxi_protocol,
        config,
        db,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    if billing_status == 'billing-ok':
        enable_billing = True
    else:
        enable_billing = False

    # if BILLING_AUTOMATIC_FALLBACK_ENABLED is False, stat counter will return
    # static value. That is normally True, but can be changed via
    # BILLING_STATIC_COUNTER_STATUS
    config.set_values(
        dict(
            BILLING_STATIC_COUNTER_STATUS=enable_billing,
            BILLING_ORDER_AUTOFALLBACK_ENABLED=order_fallback,
        ),
    )

    _mock_surge(mockserver)

    request = {
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
        'max_orders_per_phone': 2,
        'max_orders_per_device': 2,
        'max_orders_per_card': 2,
        'max_unpaid_orders': 1,
    }
    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 200

    proc = db.order_proc.find_one({'_id': '272fbd2b67b0bb9c5135d71d1d1a848b'})
    assert proc['status'] == expected_status
    assert proc['commit_state'] == expected_commit_state

    if not enable_billing and order_fallback:
        assert proc['payment_tech'].get('billing_fallback_enabled') is True


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
def test_ordercommit_internal_nosurge(taxi_protocol, mockserver, db):
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

    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 500


def test_unfinished_order(taxi_protocol, db, mockserver):
    """
    Should return 200 if commit_state == 'init':
        no any work, no rescheduling in stq.
    PS: scheduling is needed when dist_lock is active
    (execution should be only on 1 machine): so return 500 and rescheduling

    """

    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1aaaac',
    }

    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 200
    proc = db.order_proc.find_one({'_id': request['orderid']})
    assert proc is not None
    assert proc['commit_state'] == 'init'


def test_no_order(taxi_protocol, db, mockserver):
    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1bbbbb',
    }

    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 200


def test_rolback_partner_order(taxi_protocol, load, db, mockserver):
    db.order_proc.update(
        {'_id': '272fbd2b67b0bb9c5135d71d1d1a848b'},
        {
            '$set': {
                'commit_state': 'rollback',
                'order.statistics.application': 'partner',
                'order.operator_login': 'vasya',
            },
        },
    )
    db.users_order_count.insert(
        {
            '_id': 'vasya',
            'count': 2,
            'orders': [
                '272fbd2b67b0bb9c5135d71d1d1a848b',
                '272fbd2b67b0bb9c5135d71d1d1a848c',
            ],
        },
    )

    request = {
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
        'max_orders_per_phone': 2,
        'max_orders_per_device': 2,
        'max_orders_per_card': 2,
        'max_unpaid_orders': 1,
    }
    response = taxi_protocol.post('internal/ordercommit', request)
    assert response.status_code == 200

    proc = db.order_proc.find_one({'_id': '272fbd2b67b0bb9c5135d71d1d1a848b'})
    assert proc['commit_state'] == 'init'

    orders_count = db.users_order_count.find_one({'_id': 'vasya'})
    assert orders_count == {
        '_id': 'vasya',
        'count': 1,
        'orders': ['272fbd2b67b0bb9c5135d71d1d1a848c'],
    }


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

    response = taxi_protocol.post('internal/ordercommit', request)
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
