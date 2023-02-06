import datetime

import pytest

from taxi.core import db
from taxi.internal import order_manager
from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
def test_is_mqc_order_no_info():
    assert False == order_manager.is_mqc_order({'_id': 'Order123'})


@pytest.mark.filldb(_fill=False)
def test_is_mqc_order_on_missing_mqc():
    assert False == order_manager.is_mqc_order({
        '_id': 'Order123',
        'feedback': {'rating': 3.2}
    })


@pytest.mark.filldb(_fill=False)
def test_is_mqc_order_not_mqc():
    assert False == order_manager.is_mqc_order({
        '_id': 'Order123',
        'feedback': {'rating': 3.3, 'mqc': False}
    })


@pytest.mark.filldb(_fill=False)
def test_is_mqc_order_true_mqc():
    assert True == order_manager.is_mqc_order({
        '_id': 'Order123',
        'feedback': {'rating': 3.3, 'mqc': True}
    })


@pytest.mark.parametrize('expectations', [
    pytest.mark.now(stamp)(expectations) for (stamp, expectations) in [
        # orders with coupons can be taken until 2nd day of month
        # if additional compensation is enough to fill the gap
        ('2015-01-02 23:59:00 +03', {
            0: True,  # not moscow park
            # parks on prepay
            1: (True, False),  # available: more than coupon (by card only)
            2: (False, True),  # available: equal to coupon (by cash only)
            3: False,  # available: less than coupon
            4: True,  # available + add: more than coupon
            5: True,  # available + add: equal to coupon
            6: False,  # available + add: less than coupon
            # parks with postpaid contracts
            7: True,  # available: more than coupon
            8: True,  # available: equal to coupon
            9: False,  # available: less than coupon
            # different additional for card and cash
            10: (True, False),  # available + add: more/less than coupon
            11: (True, True),  # available + add: equal/equal to coupon
            12: (False, True),  # available + add: less/more than coupon
        }),
        # additional compensation does not count since 3rd of month
        ('2015-01-03 00:00:00 +03', {
            0: True,  # not moscow park
            # parks on prepay
            1: (True, False),  # available: more than coupon (by card only)
            2: (False, True),  # available: equal to coupon (by cash only)
            3: False,  # available: less than coupon
            4: False,  # available + add: more than coupon
            5: False,  # available + add: equal to coupon
            6: False,  # available + add: less than coupon
            # parks with postpaid contracts
            7: True,  # available: more than coupon
            8: True,  # available: equal to coupon
            9: False,  # available: less than coupon
            10: False,  # available + add: more than coupon
            11: False,  # available + add: equal to coupon
            12: False,  # available + add: less than coupon
        }),
    ]
])
@pytest.mark.filldb(parks='coupon')
@pytest.inline_callbacks
def test_can_take_coupon(expectations):
    """Test can_take_coupon function.

    Checks different behaviour until and after 3rd day of month.
    Each test tries to check 6 different parks against coupon order.
    Parks have parameters for all possible situations.

    :param expectations: Dict like {park_id: expected result}
    """
    due = datetime.datetime.utcnow()

    coupon_proc_by_card = dbh.order_proc.Doc(
        {
            '_id': 1,
            'order': {
                'coupon': {'value': 300, 'valid': True},
                'request': {
                    'due': due,
                    'payment': {
                        'type': 'card'
                    },
                },
            },
        }
    )

    coupon_proc_by_cash = dbh.order_proc.Doc(
        {
            '_id': 1,
            'order': {
                'coupon': {'value': 300, 'valid': True},
                'request': {
                    'due': due,
                },
            }
        }
    )

    simple_proc = dbh.order_proc.Doc({'_id': 2, 'order': {}})

    for park in (yield db.parks.find().run()):
        expected = expectations[park['_id']]
        if type(expected) is tuple:
            expected_by_card, expected_by_cash = expected
        else:
            expected_by_card = expected_by_cash = expected
        coupon_result = yield order_manager.can_take_coupon(
            park, coupon_proc_by_card, dbh.orders.PAYMENT_TYPE_CARD
        )
        msg = 'park %s, coupon_result %s, expected %s' % (
            park['_id'], coupon_result, expected_by_card
        )
        assert coupon_result == expected_by_card, msg

        coupon_result = yield order_manager.can_take_coupon(
            park, coupon_proc_by_cash, dbh.orders.PAYMENT_TYPE_CASH
        )
        msg = 'park %s, coupon_result %s, expected %s' % (
            park['_id'], coupon_result, expected_by_cash
        )
        assert coupon_result == expected_by_cash, msg

        simple_result = yield order_manager.can_take_coupon(
            park, simple_proc, dbh.orders.PAYMENT_TYPE_CASH
        )
        msg = 'park %s, simple_result %s, expected True' % (
            park['_id'], simple_result
        )
        assert simple_result, msg  # must be always True


@pytest.mark.parametrize(
    'order_proc, price, exception',
    [
        (
            dbh.order_proc.Doc({
                '_id': 1,
                'order': {
                    'calc': {
                        'allowed_tariffs': {
                            'park': {'econom': 100}
                        }
                    }
                },
                'candidates': [
                    {
                        'tariff_class': 'econom'
                    }
                ],
                'performer': {'candidate_index': 0}
            }),
            100,
            None
        ),
        (
            dbh.order_proc.Doc({
                '_id': 2,
                'order': {
                    'calc': {
                        'allowed_tariffs': {
                            'park': {'econom': 100}
                        }
                    }
                },
                'candidates': [
                    {
                        'tariff_class': 'not econom'
                    }
                ],
                'performer': {'candidate_index': 0}
            }),
            100,
            ValueError
        )
    ]
)
def test_calc_price(order_proc, price, exception):
    if exception is not None:
        with pytest.raises(exception):
            order_manager.calc_price(order_proc)
    else:
        assert order_manager.calc_price(order_proc) == price
