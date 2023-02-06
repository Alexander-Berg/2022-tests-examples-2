import decimal

import pytest
from taxi.core import async

from taxi.external import plus_wallet
from taxi.internal import dbh
from taxi.internal.order_kit import cashback_handler
from taxi.internal.order_kit import payment_handler


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
)
@pytest.inline_callbacks
def test_build_payment_split(patch):
    payment_split_mock = _patch_plus_wallet_service_payment_split(
        patch, has_complements=True
    )
    split = yield _call_build_payment_split(has_complements=True)
    assert _same_splits(split, _EXPECTED_CASHBACK_PAYMENT_SPLIT)
    assert len(payment_split_mock.calls) == 1


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
)
@pytest.inline_callbacks
def test_build_payment_split_extra_sum(patch):
    payment_split_mock = _patch_plus_wallet_service_payment_split(
        patch, has_complements=True
    )
    extra_sum_dict = {
        'first': decimal.Decimal(30),
        'second': decimal.Decimal(40),
    }
    split = yield _call_build_payment_split(
        has_complements=True, extra_sum_dict=extra_sum_dict)
    extra_elements = [
        _card_split(decimal.Decimal(30), 'first'),
        _card_split(decimal.Decimal(40), 'second')
    ]
    assert _same_splits(split, _with_extra_elements(
        _EXPECTED_CASHBACK_PAYMENT_SPLIT, extra_elements))
    assert len(payment_split_mock.calls) == 1


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=False,
)
@pytest.mark.parametrize('extra_sum_dict', [
    {},
    {'first': decimal.Decimal(30), 'second': decimal.Decimal(40)}
])
@pytest.inline_callbacks
def test_build_payment_split_without_plus_wallet_config(
        patch, extra_sum_dict):
    payment_split_mock = _patch_plus_wallet_service_payment_split(
        patch,
        has_complements=True
    )
    split = yield _call_build_payment_split(has_complements=True,
                                            extra_sum_dict=extra_sum_dict)
    assert _same_splits(split, _expected_split_without_plus_wallet_service(
        extra_sum_dict))
    assert len(payment_split_mock.calls) == 0


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    TAKE_PAYMENT_SPLIT_FROM_PLUS_WALLET_SERVICE=True,
)
@pytest.inline_callbacks
def test_build_payment_split_without_plus_wallet_service_empty_complements(patch):
    payment_split_mock = _patch_plus_wallet_service_payment_split(
        patch,
        has_complements=False
    )
    split = yield _call_build_payment_split(has_complements=False)
    assert _same_splits(split, _expected_split_without_plus_wallet_service())
    assert len(payment_split_mock.calls) == 0


@async.inline_callbacks
def _call_build_payment_split(has_complements, extra_sum_dict=None):
    order_doc = _make_order_dict(has_complements)
    payable = payment_handler.PayableOrder(order_doc)
    order = dbh.orders.Doc(order_doc)
    sum_to_pay_dict = {
        'ride': decimal.Decimal(150),
        'tips': decimal.Decimal(15),
    }
    if extra_sum_dict is not None:
        sum_to_pay_dict.update(extra_sum_dict)
    split = yield cashback_handler.build_payment_split(
        sum_to_pay_dict=sum_to_pay_dict,
        payable=payable,
        order=order,
        paid_complements={},
        tvm_src_service='stq',
        log_extra={'_link': {}},
    )
    async.return_value(split)


def _patch_plus_wallet_service_payment_split(patch, has_complements):
    @patch('taxi.external.plus_wallet.payment_split')
    def payment_split(
            sum_to_pay, payment, yandex_uid, currency, brand, status,
            taxi_status,
            fixed_price, tvm_src_service, order_id, zone, log_extra=None
    ):
        assert sum_to_pay == _expected_sum_to_pay()
        assert payment == _expected_payment(has_complements)
        assert yandex_uid == 'some_yandex_uid'
        assert currency == 'RUB'
        assert brand == 'yataxi'
        assert status == 'finished'
        assert taxi_status == 'complete'
        assert fixed_price
        assert tvm_src_service == 'stq'
        assert log_extra == {'_link': {}}
        assert order_id == 'order_id'
        assert zone == 'zone'
        return _CASHBACK_PAYMENT_SPLIT_MOCK

    return payment_split


def _expected_split_without_plus_wallet_service(extra_sum_dict=None):
    elements = [_card_split(150, 'ride'), _card_split(15, 'tips')]
    if extra_sum_dict is None:
        extra_sum_dict = {}

    for sum_type, sum_ in extra_sum_dict.iteritems():
        elements.append(_card_split(sum_, sum_type))
    return plus_wallet.PaymentSplit(
        elements=elements,
        currency='RUB',
    )


def _expected_sum_to_pay():
    return plus_wallet.SumToPay(decimal.Decimal(150), decimal.Decimal(15))


def _expected_payment(has_complements):
    if has_complements:
        wallet = plus_wallet.ComplementPaymentMethod(
            type='personal_wallet',
            payment_method_id='wallet_id/2',
            withdraw_amount=None,
        )
        complements = [wallet]
    else:
        complements = []
    return plus_wallet.Payment(
        type='card',
        payment_method_id='card-1',
        complements=complements,
    )


def _make_order_dict(has_complements):
    if has_complements:
        complements = [
            {
                'type': 'personal_wallet',
                'payment_method_id': 'wallet_id/2',
            }
        ]
    else:
        complements = []
    return {
        '_id': 'order_id',
        'user_uid': 'some_yandex_uid',
        'status': 'finished',
        'taxi_status': 'complete',
        'performer': {
            'tariff': {
                'currency': 'RUB'
            }
        },
        'fixed_price': {
            'price': 500
        },
        'payment_tech': {
            'type': 'card',
            'main_card_payment_id': 'card-1',
            'complements': complements
        },
        'nz': 'zone'
    }


def _card_split(sum_, sum_type):
    return plus_wallet.SplitElement(
        type='card',
        payment_method_id='card-1',
        sum=decimal.Decimal(sum_),
        sum_type=sum_type,
    )


def _wallet_split(sum_, sum_type):
    return plus_wallet.SplitElement(
        type='wallet',
        payment_method_id='wallet_id/2',
        sum=decimal.Decimal(sum_),
        sum_type=sum_type,
    )


def _same_splits(left, right):
    return _with_sorted_elements(left) == _with_sorted_elements(right)


def _with_sorted_elements(split):
    return split._replace(elements=sorted(split.elements))


def _with_extra_elements(split, elements):
    return split._replace(elements=split.elements + elements)


_CASHBACK_PAYMENT_SPLIT_MOCK = plus_wallet.PaymentSplit(
    elements=[
        _card_split(100, 'ride'),
        _wallet_split(50, 'ride'),
        _card_split(15, 'tips'),
        _card_split(0, 'whatever'),
    ],
    currency='RUB',
)

_EXPECTED_CASHBACK_PAYMENT_SPLIT = plus_wallet.PaymentSplit(
    elements=[
        _card_split(100, 'ride'),
        _wallet_split(50, 'ride'),
        _card_split(15, 'tips'),
    ],
    currency='RUB',
)
