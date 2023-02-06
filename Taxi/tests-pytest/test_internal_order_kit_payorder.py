import datetime
import pytest
import uuid
import copy

from taxi import config
from taxi.core import db
from taxi.internal import dbh
from taxi.internal import card_operations
from taxi.internal.order_kit import const
from taxi.internal.order_kit import order_helpers
from taxi.internal.order_kit import payment_handler
from taxi.internal.order_kit import payment_helpers
from taxi.internal.order_kit import payorder


@pytest.mark.parametrize('order_manual_price', [(None), (5670)])
@pytest.mark.parametrize('order_payment_type', [
    (const.CASH), (const.CARD), (const.APPLE)])
@pytest.mark.parametrize('order_finished', [(True), (False)])
@pytest.mark.parametrize('order_debt', [(True), (False)])
@pytest.mark.parametrize('order_had_invalid_payment_method', [(True), (False)])
@pytest.mark.parametrize('payment_type,payment_method_id,payment_billing_id,'
                         'payment_method_ok', [
    (const.CARD, 'card-fine', 'fine', True),
    (const.CARD, 'card-blocked', 'blocked', False),
    (const.APPLE, 'applepay_terminal_token', 'token', True),
])
@pytest.mark.parametrize('tips', [
    (None),
    ({'type': 'percent', 'value': 12.7}),
])
@pytest.mark.parametrize('order_last_known_region_id', [(None), (42)])
@pytest.mark.parametrize('order_payorder_created,order_deprecated', [
    (datetime.datetime(2019, 1, 1, 20, 10, 00), False),
    (datetime.datetime(2019, 1, 1, 19, 50, 00), True)
])
@pytest.mark.now('2019-01-01T20:10:00')
@pytest.inline_callbacks
def test_payorder(patch, payment_type, payment_method_id, payment_billing_id,
                  payment_method_ok, order_manual_price, order_payment_type,
                  order_finished, order_debt, tips,
                  order_had_invalid_payment_method, order_last_known_region_id,
                  order_payorder_created, order_deprecated, mock_send_event):
    user_id = 'mock-user-id'
    user_ip = '127.0.0.1'
    user_phone_id = 'mock-phone-id'
    user_yandex_uid = 'mock-yandex-uid'

    @patch('taxi.internal.order_kit.brand_helpers.brand_from_order')
    def _brand_from_order(*args, **kwargs):
        order = args[0]
        assert order.statistics['application'] == 'test_application'
        return 'does not matter here'

    @patch('taxi.internal.card_operations.get_card')
    def _get_card(*args, **kwargs):
        return card_operations.create_card_object(
            owner=user_yandex_uid,
            card_id=payment_method_id,
            system='visa',
            number='1234-5678-0987-6543',
            billing_card_id=payment_billing_id,
            currency='rub',
            name='',
            blocking_reason='' if payment_method_ok else 'frauder',
            valid=payment_method_ok,
            service_labels=[
                'taxi:persistent_id:persistent_id-' + payment_method_id
            ],
            persistent_id='persistent_id-' + payment_method_id,
            region_id='moscow',
            possible_moneyless=False,
            from_db=True,
        )

    # store mocked order documents
    order_id = uuid.uuid4().hex
    order, proc = _make_order_docs(
        order_id, user_id, user_ip, user_yandex_uid, user_phone_id,
        payment_type, payment_method_id, order_manual_price, order_payment_type,
        order_debt, tips, order_finished, order_had_invalid_payment_method,
        order_last_known_region_id, order_payorder_created)
    yield db.orders.insert(order)
    yield db.order_proc.insert(proc)

    # run payorder task
    yield payorder.task(order_id)

    # fetch documents states
    order_doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    proc_doc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    if payment_type == const.CARD and payment_method_ok:
        card_obj = yield card_operations.get_card(
            payment_method_id, user_yandex_uid)
        assert card_obj
    else:
        card_obj = None

    assert order_doc
    assert proc_doc

    # check if this path is a happy or a sad one
    status_update = proc_doc.order_info.statistics.status_updates[0]
    assert status_update.reason_code == dbh.order_proc.STATUS_UPDATE_PAYORDER
    request = status_update.reason_arg
    assert request
    assert request['request_id'] == 'id'

    not_happy_path = (
        'status' in request and request['status']['code'] != 'success'
    )
    sad_path_expected = (
        not order_finished or not payment_method_ok or order_deprecated or
        (not order_debt and
            order_payment_type in order_helpers.DEBTABLE_PAYMENT_TYPES)
    )

    assert not_happy_path == sad_path_expected

    # check effects
    if not_happy_path:
        assert order_doc == dbh.orders.Doc(order)
        if order_deprecated:
            assert request['status']['code'] == 'deprecated'
        else:
            assert request['status']['code'] != 'deprecated'
    else:
        assert order_doc.user_id == user_id
        assert not order_doc.payment_tech.need_cvn
        assert order_doc.payment_tech.type == order_payment_type
        assert proc_doc.payment_tech.type == order_payment_type
        assert len(proc_doc.order_info.statistics.status_updates) == 2
        status_update = proc_doc.order_info.statistics.status_updates[1]
        assert status_update.reason_code == (
            dbh.order_proc.STATUS_UPDATE_CHANGE_PAYMENT)
        expected_tips = {
            'type': order_doc.creditcard.tips.type,
            'value': order_doc.creditcard.tips.value,
        } if tips else {
            'type': 'flat',
            'value': 0.0,
        }
        assert status_update.reason_arg == {
            'change_value': {
                'ip': user_ip,
                'yandex_uid': user_yandex_uid,
                'tips': expected_tips,
                'invalidate_transactions': True,
                'paid_by_user': True,
                'payorder_request_id': 'id',
            },
            'billing_card_id': payment_billing_id,
            'card_id': payment_method_id,
            'persistent_id': card_obj.persistent_id if card_obj else None,
            'payment_type': payment_type,
        }
        assert status_update.need_handling
        assert not [
            i for i in order_doc.billing_tech.invalid_payment_methods
            if i.payment_id == payment_method_id]
        payment_tech = order_doc.payment_tech
        if order_manual_price:
            assert payment_tech.without_vat_to_pay['ride'] == order_manual_price
            assert payment_tech.sum_to_pay['ride'] == order_manual_price
            assert payment_tech.user_to_pay['ride'] == order_manual_price
        else:
            expected_to_pay = payment_helpers.cost2inner(order_doc.cost)
            assert payment_tech.without_vat_to_pay['ride'] == expected_to_pay
            assert payment_tech.sum_to_pay['ride'] == expected_to_pay
            assert payment_tech.user_to_pay['ride'] == expected_to_pay


@pytest.mark.filldb(
    orders='for_idempotency',
    order_proc='for_idempotency',
)
@pytest.mark.parametrize('check_enabled', [
    (True,),
    (False,),
])
@pytest.inline_callbacks
def test_payorder_idempotency(patch, check_enabled):
    if check_enabled:
        config.PAYORDER_CHECK_REQUEST_ID.save(True)
    order_id = '46dcc06602b14fca8a438762681bf474'

    @patch('taxi.internal.card_operations.get_card')
    def _get_card(*args, **kwargs):
        return card_operations.create_card_object(
            owner='123refdgfesr',
            card_id='card-1234',
            system='visa',
            number='1234-5678-0987-6543',
            billing_card_id='1234',
            currency='rub',
            name='',
            blocking_reason='',
            valid=True,
            service_labels=[
                'taxi:persistent_id:persistent_id-1234'
            ],
            persistent_id='persistent_id-1234',
            region_id='moscow',
            possible_moneyless=False,
            from_db=True,
        )

    order = yield dbh.orders.Doc.find_one_by_exact_id(order_id)
    order_proc = yield dbh.order_proc.Doc.find_one_by_exact_id(order_id)
    request = order_proc.order_info.statistics.status_updates[0].reason_arg
    args = (order, order_proc, request['user_id'], request['user_ip'],
        request['user_yandex_uid'], request['payment_type'],
        request['payment_method_id'], request['user_initiated'],
        request['request_id'], order_id)
    # first call
    payment_info = yield payment_handler.pay_after_finish(*args)
    assert payment_info == {
        'payment_billing_id': '1234',
        'payment_persistent_id': 'persistent_id-1234',
    }
    # second call
    if check_enabled:
        payment_info = yield payment_handler.pay_after_finish(*args)
        assert payment_info == {
            'payment_billing_id': '1234',
            'payment_persistent_id': 'persistent_id-1234',
        }
    else:
        with pytest.raises(payment_handler.TransactionInProgress):
            yield payment_handler.pay_after_finish(*args)


def _make_order_docs(order_id, user_id, user_ip, user_yandex_uid, user_phone_id,
                     payment_type, payment_method_id, order_manual_price,
                     order_payment_type, order_debt, tips, order_finished,
                     order_had_invalid_payment_method,
                     order_last_known_region_id, order_payorder_created):
    PAYMENT_IDS = {
        const.CASH: None,
        const.CARD: 'card-x1234',
        const.APPLE: 'applepay_123_456',
    }
    BILLING_IDS = {
        const.CASH: None,
        const.CARD: 'x1234',
        const.APPLE: '456',
    }
    PERSISTENT_IDS = {
        const.CASH: None,
        const.CARD: '1234567890',
        const.APPLE: None,
    }

    coupon_value = 1000
    order_cost = 12345 - coupon_value
    to_pay = order_manual_price or order_cost

    dbh_order = dbh.orders.Doc
    order = {
        dbh_order._id: order_id,
        dbh_order.shard_id: 0,
        dbh_order.user_id: user_id,
        dbh_order.yandex_uid: user_yandex_uid,
        dbh_order.phone_id: user_phone_id,
        dbh_order.status: (dbh.orders.STATUS_FINISHED
            if order_finished else dbh.orders.STATUS_ASSIGNED),
        dbh_order.taxi_status: (dbh.orders.TAXI_STATUS_COMPLETE
            if order_finished else dbh.orders.TAXI_STATUS_TRANSPORTING),
        dbh_order.status_updated: (
            datetime.datetime(2019, 1, 1, 20, 00, 00, 000000)),
        dbh_order.created: datetime.datetime(2019, 1, 1, 10, 00, 00, 000000),
        dbh_order.updated: datetime.datetime(2019, 1, 1, 10, 00, 00, 000000),
        dbh_order.payment_tech: {
            dbh_order.payment_tech.type.key: order_payment_type,
            dbh_order.payment_tech.main_card_payment_id.key: (
                PAYMENT_IDS.get(order_payment_type)),
            dbh_order.payment_tech.main_card_billing_id.key: (
                BILLING_IDS.get(order_payment_type)),
            dbh_order.payment_tech.main_card_persistent_id.key: (
                PERSISTENT_IDS.get(order_payment_type)),
            dbh_order.payment_tech.debt.key: order_debt,
            dbh_order.payment_tech.hold_initiated.key: False,
            dbh_order.payment_tech.without_vat_to_pay.key: {'ride': to_pay},
            dbh_order.payment_tech.sum_to_pay.key: {'ride': to_pay},
            dbh_order.payment_tech.user_to_pay.key: {'ride': to_pay},
        },
        dbh_order.cost: order_cost,
        dbh_order.billing_tech: {},
        dbh_order.creditcard: {},
        dbh_order.current_prices: {
            'final_cost_meta': {
                'user': {'use_cost_includes_coupon': True,
                         'coupon_value': coupon_value}
            }
        },
        dbh_order.coupon: {
            'was_used': True,
            'value': coupon_value,
            'valid': True
        },
        dbh_order.statistics: {
            'application': 'test_application',
        }
    }
    if order_had_invalid_payment_method:
        ipm = dbh_order.billing_tech.invalid_payment_methods
        order[dbh_order.billing_tech].update({
            ipm.key: [
                {
                    ipm.payment_id.key: payment_method_id
                }
            ]
        })
    if order_manual_price:
        order[dbh_order.payment_tech].update({
            dbh_order.payment_tech.history.key: [
                {
                    dbh_order.payment_tech.history.decision.key: (
                        order_helpers.DECISION_CHARGE),
                }
            ]
        })
    if tips:
        order[dbh_order.creditcard].update({
            dbh_order.creditcard.tips.key: tips
        })
    if order_last_known_region_id:
        order[dbh_order.payment_tech].update({
            dbh_order.payment_tech.last_known_region_id.key: (
                order_last_known_region_id)
        })

    order_refined = copy.deepcopy(order)
    order_refined.pop(dbh_order._id)
    order_refined.pop(dbh_order.shard_id)
    order_refined.pop(dbh_order.payment_tech)
    dbh_proc = dbh.order_proc.Doc
    status_updates = dbh_proc.order_info.statistics.status_updates
    proc = {
        dbh_proc._id: order_id,
        dbh_proc.shard_id: 0,
        dbh_proc.status: order[dbh_order.status],
        dbh_proc.created: datetime.datetime(2019, 1, 1, 10, 00, 00, 000000),
        dbh_proc.payment_tech: {
            dbh_proc.payment_tech.type.key: order_payment_type,
            dbh_proc.payment_tech.main_card_payment_id.key: (
                PAYMENT_IDS.get(order_payment_type)),
            dbh_proc.payment_tech.main_card_billing_id.key: (
                BILLING_IDS.get(order_payment_type)),
            dbh_proc.payment_tech.main_card_persistent_id.key: (
                PERSISTENT_IDS.get(order_payment_type)),
        },
        dbh_proc.order: order_refined,
        dbh_proc.order_info: {
            dbh_proc.order_info.statistics.key: {
                dbh_proc.order_info.statistics.status_updates.key: [
                    {
                        status_updates.created.key: order_payorder_created,
                        status_updates.reason_code.key: (
                            dbh.order_proc.STATUS_UPDATE_PAYORDER
                        ),
                        status_updates.reason_arg.key: {
                            'request_id': 'id',
                            'user_id': user_id,
                            'user_ip': user_ip,
                            'user_phone_id': user_phone_id,
                            'user_yandex_uid': user_yandex_uid,
                            'payment_type': payment_type,
                            'payment_method_id': payment_method_id,
                            'user_initiated': True,
                        }
                    }
                ]
            }
        }
    }

    return order, proc
