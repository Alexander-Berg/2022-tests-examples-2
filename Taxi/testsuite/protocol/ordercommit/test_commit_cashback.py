import pytest

from protocol.ordercommit import order_commit_common


ORDERCOMMIT_URL = '3.0/ordercommit'


def assert_cashback_order(order_id, db, discount, plus):
    proc = db.order_proc.find_one(order_id)
    extra_data = proc.get('extra_data', {})
    assert extra_data.get('cashback')
    cashback = extra_data.get('cashback')
    assert cashback.get('is_cashback') is True
    assert cashback.get('is_discount_cashback') is discount
    assert cashback.get('is_plus_cashback') is plus


def assert_not_cashback_order(order_id, db):
    proc = db.order_proc.find_one(order_id)
    cashback = proc.get('extra_data', {}).get('cashback')
    assert not cashback


pytestmark = [
    pytest.mark.now('2019-06-26T21:19:09+0300'),
    pytest.mark.order_experiments('fixed_price'),
    pytest.mark.config(COMMIT_PLUGINS_ENABLED=True),
]


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(order_offers='no_discount_no_modifier')
def test_cashback_no_discount_no_modifier(taxi_protocol, db):
    order_id = 'orderid'

    request = {'id': 'user_id', 'orderid': order_id}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    assert_not_cashback_order(order_id, db)


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(order_offers='discount')
def test_cashback_by_discount_wrong_class(taxi_protocol, db):
    order_id = 'orderid'

    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.request.class': ['vip']}},
    )
    request = {'id': 'user_id', 'orderid': order_id}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    assert_not_cashback_order(order_id, db)


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(order_offers='discount')
def test_cashback_by_discount_ok(taxi_protocol, db, mock_stq_agent):
    request = {'id': 'user_id', 'orderid': 'orderid'}

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    assert_cashback_order('orderid', db, True, False)


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(order_offers='metadata')
@pytest.mark.parametrize(
    'tariff_class, expect_cashback', [('vip', False), ('econom', True)],
)
def test_cashback_by_metadata_class(
        taxi_protocol, db, tariff_class, expect_cashback, mock_stq_agent,
):
    order_id = 'orderid'
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.request.class': [tariff_class]}},
    )
    # add meta to econom
    db.order_offers.update(
        {'_id': 'offer_id_3'},
        {'$set': {'prices.0.pricing_data.user.meta': {'cashback_rate': 0.1}}},
    )

    request = {'id': 'user_id', 'orderid': order_id}

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    if expect_cashback:
        assert_cashback_order('orderid', db, True, False)
    else:
        assert_not_cashback_order('orderid', db)


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(order_offers='metadata')
@pytest.mark.parametrize(
    'meta_to_add, expect_cashback, discount_cashback, plus_cashback',
    [
        ('some_another_meta', False, False, False),
        ('cashback_rate', True, True, False),
        ('cashback_fixed_price', True, False, True),
        ('cashback_calc_coeff', True, False, True),
        ('marketing_cashback:some_new_sponsor:rate', True, True, False),
    ],
)
def test_cashback_by_metadata_meta(
        taxi_protocol,
        db,
        meta_to_add,
        expect_cashback,
        discount_cashback,
        plus_cashback,
        mock_stq_agent,
):
    request = {'id': 'user_id', 'orderid': 'orderid'}

    db.order_offers.update(
        {'_id': 'offer_id_3'},
        {'$set': {'prices.0.pricing_data.user.meta': {meta_to_add: 0.1}}},
    )

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    if expect_cashback:
        assert_cashback_order('orderid', db, discount_cashback, plus_cashback)
    else:
        assert_not_cashback_order('orderid', db)


@pytest.mark.parametrize(
    'user, orderid, modifier_expected, cashback_modifier_expected',
    [
        ('user_id_with_plus', 'orderid_with_plus', True, False),
        (
            'user_id_with_cashback_plus',
            'orderid_with_cashback_plus',
            True,
            True,
        ),
        (
            'user_id_with_disabled_new_subscription',
            'orderid_with_disabled_new_subscription',
            False,
            False,
        ),
    ],
    ids=['old_plus', 'cashback_plus', 'disabled_new_subscription'],
)
@pytest.mark.user_experiments('ya_plus')
def test_ya_plus_disabled_by_cashback(
        taxi_protocol,
        db,
        user,
        orderid,
        modifier_expected,
        cashback_modifier_expected,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    db.order_offers.remove({})
    request = {'id': user, 'orderid': orderid}

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    order_proc = db.order_proc.find_one({'_id': orderid})

    if not modifier_expected or cashback_modifier_expected:
        assert 'price_modifiers' not in order_proc
    else:
        assert 'price_modifiers' in order_proc


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.filldb(order_offers='metadata')
def test_cashback_plus_full(taxi_protocol, db, mock_stq_agent):
    request = {'id': 'user_id', 'orderid': 'orderid'}

    db.order_offers.update(
        {'_id': 'offer_id_3'},
        {
            '$set': {
                'prices.0.pricing_data.user.meta': {
                    'user_total_price': 1000.0,
                    'cashback_fixed_price': 100.0,
                    'cashback_calc_coeff': 0.111111,
                },
            },
        },
    )

    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    assert_cashback_order('orderid', db, False, True)

    proc = db.order_proc.find_one('orderid')
    order_commit_common.check_current_prices(
        proc, 'fixed', 1000.0, cashback_price=100.0,
    )
