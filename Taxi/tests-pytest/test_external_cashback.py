import decimal

import pytest

from taxi.core import async
from taxi.external import plus_wallet


@pytest.inline_callbacks
@pytest.mark.filldb(_fill=False)
def test_payment_split(patch):
    perform_request_mock = _patch_perform_request(patch)

    split = yield plus_wallet.payment_split(
        sum_to_pay=_make_sum_to_pay(),
        payment=_make_payment(),
        yandex_uid='some_yandex_uid',
        currency='RUB',
        brand='yataxi',
        status='finished',
        taxi_status='complete',
        fixed_price=True,
        tvm_src_service='stq',
        order_id='order_id',
        zone='zone',
        log_extra={'_link': {}},
    )
    assert split == _expected_split()
    assert len(perform_request_mock.calls) == 1


def _patch_perform_request(patch):
    @patch('taxi.external.plus_wallet._perform_request')
    @async.inline_callbacks
    def _perform_request(method, location, json, tvm_src_service,
                         tvm_dst_service, log_extra):
        assert method == 'POST'
        assert location == 'v1/internal/payment/split'
        assert json == _expected_json_request()
        assert tvm_src_service == 'stq'
        assert tvm_dst_service == 'plus-wallet'
        assert log_extra == {'_link': {}}
        async.return_value(_make_response())
        yield

    return _perform_request


class _Response(object):
    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


def _make_response():
    json = {
        'sum_to_pay': {
            'ride': [
                _card_response_split(100),
                _wallet_response_split(50)
            ],
            'tips': [_card_response_split(15)]
        },
        'currency': 'RUB'
    }
    return _Response(json)


def _expected_json_request():
    return {
        'sum_to_pay': {
            'ride': '150',
            'tips': '15',
        },
        'payment': {
            'type': 'card',
            'payment_method_id': 'card-1',
            'complements': [
                {
                    'type': 'personal_wallet',
                    'payment_method_id': 'wallet_id/2',
                    'withdraw_amount': '33',
                }
            ]
        },
        'yandex_uid': 'some_yandex_uid',
        'currency': 'RUB',
        'brand': 'yataxi',
        'status': 'finished',
        'taxi_status': 'complete',
        'fixed_price': True,
        'order_id': 'order_id',
        'zone': 'zone'
    }


def _make_sum_to_pay():
    return plus_wallet.SumToPay(
        ride=decimal.Decimal(150),
        tips=decimal.Decimal(15),
    )


def _make_payment():
    wallet = plus_wallet.ComplementPaymentMethod(
        type='personal_wallet',
        payment_method_id='wallet_id/2',
        withdraw_amount=33,
    )
    return plus_wallet.Payment(
        type='card',
        payment_method_id='card-1',
        complements=[wallet]
    )


def _expected_split():
    elements = [_card_split(100, 'ride'), _wallet_split(50, 'ride'),
                _card_split(15, 'tips')]
    return plus_wallet.PaymentSplit(
        elements=elements,
        currency='RUB'
    )


def _card_split(sum_, sum_type):
    return plus_wallet.SplitElement(
        type='card',
        payment_method_id='card-1',
        sum=decimal.Decimal(sum_),
        sum_type=sum_type,
    )


def _card_response_split(sum_):
    return {
        'type': 'card',
        'payment_method_id': 'card-1',
        'sum': str(sum_),
    }


def _wallet_response_split(sum_):
    return {
        'type': 'personal_wallet',
        'payment_method_id': 'wallet_id/2',
        'sum': str(sum_),
    }


def _wallet_split(sum_, sum_type):
    return plus_wallet.SplitElement(
        type='personal_wallet',
        payment_method_id='wallet_id/2',
        sum=decimal.Decimal(sum_),
        sum_type=sum_type,
    )
