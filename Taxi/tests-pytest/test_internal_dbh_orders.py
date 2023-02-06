import collections
import copy
import datetime

import pytest

from taxi.internal import dbh
from taxi.util import decimal


OrderChecker = collections.namedtuple('OrderChecker', ['func', 'msg'])


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('coupon_block,expected', [
    (None, False),
    ({}, False),
    ({'valid': False}, False),
    ({'valid': True}, True),
])
def test_has_coupon(coupon_block, expected):
    cls = dbh.orders.Doc
    assert cls({cls.coupon: coupon_block}).has_coupon() == expected


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
def test_requested_route():
    point1 = [37.5, 55.7]
    point2 = [37.6, 55.6]
    Order = dbh.orders.Doc
    order = Order({
        Order.request: {
            Order.request.source.key: {
                Order.request.source.point.key: point1,
            },
            Order.request.destinations.key: [{
                Order.request.source.point.key: point2,
            }],
        },
    })

    points = [obj.point for obj in order.requested_route]
    assert points == [point1, point2]


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.mark.parametrize('feedback,by_mqc', [
    (None, False),
    ({dbh.orders.Doc.feedback.mqc.key: False}, False),
    ({dbh.orders.Doc.feedback.mqc.key: True}, True),
])
def test_called_by_mqc(feedback, by_mqc):
    doc = dbh.orders.Doc({dbh.orders.Doc.feedback: feedback})
    assert doc.called_by_mqc is by_mqc


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('status,taxi_status,finished', [
    (dbh.orders.STATUS_DRAFT, None, False),
    (dbh.orders.STATUS_PENDING, None, False),
    (dbh.orders.STATUS_ASSIGNED, None, False),
    (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_PREEXPIRED, False),
    (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_EXPIRED, True),
    (dbh.orders.STATUS_FINISHED, dbh.orders.TAXI_STATUS_FAILED, True),
    (dbh.orders.STATUS_CANCELLED, None, True),
    (dbh.orders.STATUS_REORDERED, None, True),
])
def test_finished(status, taxi_status, finished):
    cls = dbh.orders.Doc
    doc = cls({cls.status: status, cls.taxi_status: taxi_status})
    assert doc.finished == finished


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
@pytest.mark.parametrize('card_number,card_system', [
    (None, None),
    ('5555***4444', 'Visa'),
])
def _update_update_with_coupon_with_card(stub, card_number, card_system):
    # Test update update with coupon information

    update = {'$set': {}}
    if card_number:
        card = stub(number=card_number, system=card_system)
        expected = {
            dbh.orders.Doc.creditcard.credentials.card_number: card_number,
            dbh.orders.Doc.creditcard.credentials.card_system: card_system,
        }
    else:
        card = None
        expected = {}
    dbh.orders.Doc()._update_update_with_coupon_with_card(update, card)
    assert update['$set'] == expected


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(orders='test_sync_with_proc_fails')
@pytest.mark.parametrize('order_id', ['version_6'])
@pytest.inline_callbacks
def test_sync_with_proc_fails(order_id):
    # Test cases when order cannot be synced with order_proc document

    status_updates = dbh.order_proc.Doc.order_info.statistics.status_updates
    proc = dbh.order_proc.Doc({
        dbh.order_proc.Doc._id: order_id,
        dbh.order_proc.Doc.order: {
            dbh.order_proc.Doc.order.version.key: 5,
        },
        dbh.order_proc.Doc.order_info: {
            dbh.order_proc.Doc.order_info.statistics.key: {
                status_updates.key: [{
                    status_updates.created: datetime.datetime.utcnow(),
                    status_updates.status: dbh.orders.STATUS_CANCELLED,
                }]
            },
        },
    })

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order.version >= proc.order.version
    with pytest.raises(dbh.orders.RaceCondition):
        yield dbh.orders.Doc.sync_with_proc(proc)


_NOW = datetime.datetime(2016, 12, 16, 12, 46)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(
    orders='test_set_subvention_bonus',
    subvention_reasons='test_set_subvention_bonus'
)
@pytest.mark.parametrize('order_id,bonus_reason,bonus_value,expected_bonus', [
    (
        'first_time_bonus_order_id',
        'test_reason_1',
        decimal.Decimal('3000.0'),
        [
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key: '3000.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    'test_reason_1': '3000.0'
                }
            },
        ]
    ),
    (
        'have_bonus_order_id',
        'test_reason_2',
        decimal.Decimal('2500.0'),
        [
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key:
                    datetime.datetime(2016, 12, 15, 12, 18),
                dbh.subvention_reasons.Doc.subvention_bonus.value.key:
                    '2000.0',
            },
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key:
                    '4500.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    'bulk_bonus_pay': '2000.0',
                    'test_reason_2': '2500.0'
                }
            },
        ]
    ),
    (
        'have_bonus_with_details_order_id',
        'test_reason_2',
        decimal.Decimal('2500.0'),
        [
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key:
                    datetime.datetime(2016, 12, 15, 12, 18),
                dbh.subvention_reasons.Doc.subvention_bonus.value.key: '2000.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    'test_reason_1': '2000.0',
                }
            },
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key:
                    '4500.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    'test_reason_1': '2000.0',
                    'test_reason_2': '2500.0'
                }
            },
        ]
    ),
    (
        'have_bonus_with_details_order_id',
        'test_reason_1',
        decimal.Decimal('2500.0'),
        [
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key:
                    datetime.datetime(2016, 12, 15, 12, 18),
                dbh.subvention_reasons.Doc.subvention_bonus.value.key: '2000.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    'test_reason_1': '2000.0',
                }
            },
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key:
                    '2500.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    'test_reason_1': '2500.0',
                }
            },
        ]
    ),
])
@pytest.inline_callbacks
def test_set_subvention_bonus(order_id, bonus_reason,
                              bonus_value, expected_bonus):
    yield dbh.orders.Doc.set_subvention_bonus(
        order_id, bonus_reason, bonus_value
    )
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    subvention_reasons = yield order.get_subvention_reasons()
    assert subvention_reasons.subvention_bonus == expected_bonus


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('subvention_bonus,expected_bonus,expected_details', [
    (
        [
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key:
                    '3000.0',
            }
        ],
        decimal.Decimal(3000),
        {dbh.subvention_reasons.BULK_BONUS_PAY_REASON: '3000.0'}
    ),
    (
        [
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key: '3000.0',
            },
            {
                dbh.subvention_reasons.Doc.subvention_bonus.created.key: _NOW,
                dbh.subvention_reasons.Doc.subvention_bonus.value.key: '3001.0',
                dbh.subvention_reasons.Doc.subvention_bonus.details.key: {
                    dbh.subvention_reasons.BULK_BONUS_PAY_REASON: '3000.0',
                    'test_subvention_reason': '1.0'
                }
            }
        ],
        decimal.Decimal(3001),
        {
            dbh.subvention_reasons.BULK_BONUS_PAY_REASON: '3000.0',
            'test_subvention_reason': '1.0'
        }
    ),
    (
        None,
        decimal.Decimal(0),
        {}
    ),
    (
        [],
        decimal.Decimal(0),
        {}
    ),
])
def test_get_subvention_bonus(subvention_bonus, expected_bonus,
                              expected_details):
    if subvention_bonus is not None:
        subvention_reason = dbh.subvention_reasons.Doc({
            dbh.subvention_reasons.Doc.subvention_bonus: subvention_bonus
        })
    else:
        subvention_reason = dbh.subvention_reasons.Doc({})
    bonus, details = subvention_reason.subvention_bonus_value_details
    assert bonus == expected_bonus
    assert details == expected_details


@pytest.inline_callbacks
def test_link_embedded_to_umbrella():
    emb_order = dbh.orders.Doc()
    emb_order._id = 'emb'
    emb_order.performer.park_id = '888111'
    emb_order.performer.driver_uuid = 'abcdefg'
    emb_order.performer.taxi_alias.id = 't_al'
    yield dbh.orders.Doc._save(emb_order)
    umb_order = dbh.orders.Doc()
    umb_order._id = 'umb'
    yield dbh.orders.Doc._save(umb_order)

    emb_proc = dbh.order_proc.Doc()
    emb_proc.order_info.umbrella_order_id = umb_order._id
    yield emb_order.link_embedded_to_umbrella(emb_proc, 'zzz')

    assert not emb_order.umbrella_order_id
    assert not umb_order.embedded_orders

    new_emb_order = yield dbh.orders.Doc.find_one_by_id(emb_order._id)
    new_umb_order = yield dbh.orders.Doc.find_one_by_id(umb_order._id)

    assert new_emb_order.umbrella_order_id == umb_order._id
    assert len(new_umb_order.embedded_orders) == 1
    assert new_umb_order.embedded_orders[0].id == emb_order._id


@pytest.inline_callbacks
def test_link_embedded_to_umbrella_sets_performer():
    emb_order = dbh.orders.Doc()
    emb_order._id = 'emb'
    emb_order.performer.park_id = '888111'
    emb_order.performer.driver_uuid = 'abcdefg'
    emb_order.performer.taxi_alias.id = 't_al'
    yield dbh.orders.Doc._save(emb_order)
    umb_order = dbh.orders.Doc()
    umb_order._id = 'umb'
    yield dbh.orders.Doc._save(umb_order)

    emb_proc = dbh.order_proc.Doc()
    emb_proc.order_info.umbrella_order_id = umb_order._id

    assert not umb_order.performer
    yield emb_order.link_embedded_to_umbrella(emb_proc, 'zzz')
    new_umb_order = yield dbh.orders.Doc.find_one_by_id(umb_order._id)
    assert new_umb_order.performer.park_id == '888111'
    assert new_umb_order.performer.driver_uuid == 'abcdefg'
    assert new_umb_order.performer.taxi_alias.id == 'zzz'


@pytest.inline_callbacks
def test_link_embedded_to_umbrella_checks_performer_ok():
    emb_order = dbh.orders.Doc()
    emb_order._id = 'emb'
    emb_order.performer.park_id = '888111'
    emb_order.performer.driver_uuid = 'abcdefg'
    emb_order.performer.taxi_alias.id = 't_al'
    emb_order.performer.car_age = 11
    yield dbh.orders.Doc._save(emb_order)
    umb_order = dbh.orders.Doc()
    umb_order._id = 'umb'
    umb_order.performer.park_id = '888111'
    umb_order.performer.driver_uuid = 'abcdefg'
    umb_order.performer.taxi_alias.id = 'zzz'
    umb_order.performer.car_age = 10
    yield dbh.orders.Doc._save(umb_order)

    emb_proc = dbh.order_proc.Doc()
    emb_proc.order_info.umbrella_order_id = umb_order._id

    yield emb_order.link_embedded_to_umbrella(emb_proc, 'zzz')
    new_umb_order = yield dbh.orders.Doc.find_one_by_id(umb_order._id)
    assert new_umb_order.performer.park_id == '888111'
    assert new_umb_order.performer.driver_uuid == 'abcdefg'
    assert new_umb_order.performer.car_age == 11
    assert new_umb_order.performer.taxi_alias.id == 'zzz'


@pytest.inline_callbacks
def test_link_embedded_to_umbrella_checks_performer_fail():
    emb_order = dbh.orders.Doc()
    emb_order._id = 'emb'
    emb_order.performer.park_id = '888222'
    emb_order.performer.driver_uuid = 'zyxywr'
    emb_order.performer.taxi_alias.id = 't_al'
    emb_order.performer.car_age = 11
    yield dbh.orders.Doc._save(emb_order)
    umb_order = dbh.orders.Doc()
    umb_order._id = 'umb'
    umb_order.performer.park_id = '888111'
    umb_order.performer.driver_uuid = 'abcdefg'
    umb_order.performer.taxi_alias.id = 'pp'
    umb_order.performer.car_age = 10
    yield dbh.orders.Doc._save(umb_order)

    emb_proc = dbh.order_proc.Doc()
    emb_proc.order_info.umbrella_order_id = umb_order._id

    with pytest.raises(dbh.orders.RaceCondition):
        yield emb_order.link_embedded_to_umbrella(emb_proc, 'zzz')


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('update,ev_type,data,expected_push', [
    # empty update
    (
        {}, 'some_type', {'x': 1},
        {
            dbh.orders.Doc.payment_events: {
                'c': _NOW,
                'type': 'some_type',
                'data': {'x': 1},
                'status': 'success',
            }
        },
    ),
    # $push exists
    (
        {
            '$push': {'b': 1}
        }, 'some_type', {'x': 1},
        {
            dbh.orders.Doc.payment_events: {
                'c': _NOW,
                'type': 'some_type',
                'data': {'x': 1},
                'status': 'success',
            },
            'b': 1,
        }
    )
])
def test_update_update_payment_events(update, ev_type, data, expected_push):
    update_copy = copy.deepcopy(update)
    dbh.orders.Doc.update_update_payment_events(update_copy, ev_type, data)
    assert update_copy['$push'] == expected_push


@pytest.mark.parametrize('order_id,discount_class,expected', [
    (
        'no-discount',
        dbh.orders.Doc.discount,
        {},
    ),
    (
        'no-discount',
        dbh.order_proc.Doc.order.discount,
        {},
    ),
    (
        'order-with-discount',
        dbh.orders.Doc.discount,
        {
            'discount.driver_less_coeff': 0.5,
            'discount.id': '5694bf44482342e6b8b40099fb537c48',
            'discount.method': 'subvention-fix',
            'discount.original_value': 0.01,
            'discount.price': 999.0,
            'discount.reason': 'analytics',
            'discount.value': 0.01
        }
    ),
    (
        'order-with-discount',
        dbh.order_proc.Doc.order.discount,
        {
            'order.discount.driver_less_coeff': 0.5,
            'order.discount.id': '5694bf44482342e6b8b40099fb537c48',
            'order.discount.method': 'subvention-fix',
            'order.discount.original_value': 0.01,
            'order.discount.price': 999.0,
            'order.discount.reason': 'analytics',
            'order.discount.value': 0.01
        }
    ),
])
@pytest.inline_callbacks
def test_build_discount_update(order_id, discount_class, expected):
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    if proc.candidates:
        proc.preupdated_order_data.discount = proc.candidates[0].discount
    update_set = yield dbh.orders.build_discount_update(
         proc, discount_class
    )
    assert update_set == expected


@pytest.mark.parametrize(
    'order_id, complements',
    [
        #  drop complements
        ('order-with-comp', []),
        #  add complements
        (
            'order-without-comp',
            [{
                'type': 'personal_wallet',
                'payment_method_id': 'wallet_id/1234567'
            }]
        ),
        #  change complements
        (
            'order-with-comp',
            [{
                'type': 'personal_wallet',
                'payment_method_id': 'wallet_id/9876543'
            }]
        ),
        #  complements is None
        ('order-without-comp', None),
    ]
)
@pytest.mark.filldb(orders='test_sync_payment_tech')
@pytest.inline_callbacks
def test_sync_payment_tech(order_id, complements):
    new_version = 6
    order = yield dbh.orders.Doc.find_one_by_id(order_id)

    proc = dbh.order_proc.Doc({
        dbh.order_proc.Doc._id: order_id,
        dbh.order_proc.Doc.order: {
            dbh.order_proc.Doc.order.version.key: new_version,
        }
    })
    proc.preupdated_order_data.payment_method_info = [{
        'data': dbh.orders.PaymentMethodInfo(
            '', '', '', '', None, 'card', '', '', '', complements
        ),
        'tag': 'payment_method_info'
    }]

    yield order.sync_with_proc(proc)
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order.version == new_version

    if complements is not None:
        assert order.payment_tech.complements == complements
        if complements:
            assert order.payment_tech.complements[0].type == complements[0]['type']
            assert order.payment_tech.complements[0].payment_method_id == complements[0]['payment_method_id']
    else:
        assert 'complements' not in order.payment_tech


@pytest.inline_callbacks
@pytest.mark.filldb(orders='test_sync_payment_tech')
@pytest.mark.parametrize('with_cashback', [
    True, False
])
@pytest.mark.parametrize('with_charity', [
    True, False
])
@pytest.mark.parametrize('with_final_cost_meta', [
    True, False
])
def test_sync_current_prices(with_cashback, with_charity, with_final_cost_meta):
    order_id = 'order-without-comp'
    new_version = 100000

    cp_doc = dbh.order_proc.Doc.order.current_prices
    proc_cp = {
        cp_doc.user_total_price.key: 200,
        cp_doc.user_total_display_price.key: 200,
        cp_doc.user_ride_display_price.key: 200,
        cp_doc.kind.key: 'taximeter'
    }

    if with_cashback:
        proc_cp[cp_doc.cashback_price.key] = 100

    if with_charity:
        proc_cp[cp_doc.charity_price.key] = 3

    if with_final_cost_meta:
        proc_cp[cp_doc.final_cost_meta.key] = {'user': {}, 'driver': {'a': 2}}

    proc = dbh.order_proc.Doc({
        dbh.order_proc.Doc._id: order_id,
        dbh.order_proc.Doc.order: {
            dbh.order_proc.Doc.order.version.key: new_version,
            dbh.order_proc.Doc.order.current_prices.key: proc_cp
        }
    })

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    yield order.sync_with_proc(proc)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order.version == new_version
    assert order.current_prices == proc_cp


@pytest.mark.parametrize(
    'order_id, family',
    [
        #  drop payment_tech.family
        ('order-with-family', None),
        #  add payment_tech.family
        (
            'order-without-family',
            {
                'is_owner': False,
                'owner_uid': "family_owner_uid",
                'limit': 250000,
                'expenses': 150000,
                'currency': 'RUB',
                'frame': 'month',
            }
        ),
        #  change family (unrealistic but JIC)
        (
            'order-with-family',
            {
                'is_owner': True,
            }
        ),
        #  None to None
        ('order-without-family', None),
    ]
)
@pytest.mark.filldb(orders='test_sync_payment_tech_family')
@pytest.inline_callbacks
def test_sync_payment_tech_family(order_id, family):
    new_version = 6
    order = yield dbh.orders.Doc.find_one_by_id(order_id)

    proc = dbh.order_proc.Doc({
        dbh.order_proc.Doc._id: order_id,
        dbh.order_proc.Doc.order: {
            dbh.order_proc.Doc.order.version.key: new_version,
        }
    })
    proc.preupdated_order_data.payment_method_info = [{
        'data': dbh.orders.PaymentMethodInfo(
            '', '', '', '', None, 'card', '', '', '', None, family,
        ),
        'tag': 'payment_method_info'
    }]

    yield order.sync_with_proc(proc)
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert order.version == new_version

    if family is not None:
        assert order.payment_tech.family == family
    else:
        assert 'family' not in order.payment_tech
