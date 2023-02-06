import datetime
import decimal

import pytest

from taxi.core import async
from taxi.external import transactions

_INVOICE_CREATE_RESPONSE = object()
_INVOICE_RETRIEVE_RESPONSE = object()
_INVOICE_UPDATE_RESPONSE = object()
_COMPENSATION_CREATE_RESPONSE = object()
_COMPENSATION_REFUND_RESPONSE = object()


@pytest.mark.parametrize('payment,expected', [
    (
        transactions.CardLikePayment('card', 'card-01', '01'),
        {
            'type': 'card',
            'method': 'card-01',
            'billing_id': '01',
        },
    ),
    (
        transactions.WalletPayment('wallet_method', 'taxi',
                                   'wallet_account_id'),
        {
            'type': 'personal_wallet',
            'method': 'wallet_method',
            'service': 'taxi',
            'account': {
                'id': 'wallet_account_id',
            }
        },
    ),
    (
        transactions.AgentPayment('007'),
        {'type': 'agent', 'agent_id': '007'},
    )
])
@pytest.mark.filldb(_fill=False)
def test_payment_serialize(payment, expected):
    assert payment.serialize() == expected


@pytest.inline_callbacks
def test_v2_invoice_create(patch):
    request_data = {
        'id': 'invoice_id',
        'invoice_due': '2020-02-12T12:01:02.300000',
        'billing_service': 'taxi',
        'payments': [
            {
                'type': 'card',
                'method': 'card-01',
                'billing_id': '01'
            }
        ],
        'currency': 'RUB',
        'yandex_uid': '666',
        'pass_params': {},
        'service': 'taxi',
        'user_ip': '::1/128',
        'invoice_tz_id': 'Europe/Moscow',
        'metric_namespaces': ['rus'],
        'personal_phone_id': 'some_personal_phone_id',
        'automatic_clear_delay': 10800,
        'login_id': 't:1234',
    }
    _patch_perform_request(
        patch,
        'v2/invoice/create',
        request_data,
        _Response(_INVOICE_CREATE_RESPONSE)
    )
    response = yield transactions.v2_invoice_create(
        id_='invoice_id',
        invoice_due=datetime.datetime(2020, 2, 12, 12, 1, 2, 300000),
        billing_service='taxi',
        payments=[
            transactions.CardLikePayment('card', 'card-01', '01'),
        ],
        currency='RUB',
        yandex_uid='666',
        pass_params={},
        invoice_tz_id='Europe/Moscow',
        country_id='rus',
        personal_phone_id='some_personal_phone_id',
        automatic_clear_delay=10800,
        user_ip='::1/128',
        service='taxi',
        tvm_src_service='stq',
        log_extra={'_link': {}},
        user_login_id='t:1234'
    )
    assert response == _INVOICE_CREATE_RESPONSE


@pytest.mark.parametrize('prefer_transactions_data,expected_json_request', [
    (
        None,
        {
            'id': 'invoice_id'
        },
    ),
    (
        True,
        {
            'id': 'invoice_id',
            'prefer_transactions_data': True,
        },
    )
])
@pytest.inline_callbacks
def test_v2_invoice_retrieve(
        patch, prefer_transactions_data, expected_json_request
):
    _patch_perform_request(
        patch,
        'v2/invoice/retrieve',
        expected_json_request,
        _Response(_INVOICE_RETRIEVE_RESPONSE),
    )
    response = yield transactions.v2_invoice_retrieve(
        id_='invoice_id',
        prefer_transactions_data=prefer_transactions_data,
        tvm_src_service='stq',
        log_extra={'_link': {}},
    )
    assert response == _INVOICE_RETRIEVE_RESPONSE


@pytest.inline_callbacks
def test_v2_invoice_update(patch):
    request_data = {
        'id': 'invoice_id',
        'operation_id': '1',
        'originator': 'processing',
        'items_by_payment_type': [
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': 'ride',
                        'product_id': 'some_product_id',
                        'region_id': 225,
                        'amount': '100',
                        'fiscal_receipt_info': {
                            'personal_tin_id': 'some_personal_tin_id',
                            'vat': 'nds_20',
                            'title': 'some_title',
                        },
                        'merchant': {
                            'id': 'some_merchant_id',
                            'order_id': 'some_merchant_order_id',
                        }
                    }
                ]
            }
        ],
        'version': 2,
        'user_ip': '::1/128',
        'yandex_uid': '666',
        'pass_params': {
            'some_pass_param': 'some_value'
        },
        'antifraud_payload': {
            'antifraud_payload_field': 'antifraud_payload_value',
        },
        'payments': [
            {
                'type': 'card',
                'method': 'card-01',
                'billing_id': '01'
            }
        ],
        'need_cvn': False,
        'login_id': 't:1234',
        'transaction_payload': {
            'alias_id': 'some_alias_id',
            'tariff_class': 'some_tariff_class',
            'driver': {
                'clid': 'some_park_id',
                'park_id': 'some_park_id',
                'driver_profile_id': 'some_driver_profile_id',
            }
        }
    }
    _patch_perform_request(
        patch,
        'v2/invoice/update',
        request_data,
        _Response(_INVOICE_UPDATE_RESPONSE)
    )
    fiscal_receipt_info = transactions.FiscalReceiptInfo(
        personal_tin_id='some_personal_tin_id',
        vat='nds_20',
        title='some_title',
        cashregister_params=None,
    )
    merchant = transactions.Merchant(
        'some_merchant_id', 'some_merchant_order_id'
    )
    response = yield transactions.v2_invoice_update(
        id_='invoice_id',
        operation_id='1',
        originator='processing',
        version=2,
        user_ip='::1/128',
        yandex_uid='666',
        pass_params={
            'some_pass_param': 'some_value',
        },
        antifraud_payload={
             'antifraud_payload_field': 'antifraud_payload_value'
        },
        items_by_payment_type=[
            transactions.PaymentItemsList(
                payment_type='card',
                items=[
                    transactions.Item(
                        item_id='ride',
                        product_id='some_product_id',
                        amount=decimal.Decimal(100),
                        region_id=225,
                        fiscal_receipt_info=fiscal_receipt_info,
                        merchant=merchant,
                    )
                ]
            )
        ],
        payments=[
            transactions.CardLikePayment('card', 'card-01', '01'),
        ],
        need_cvn=False,
        tvm_src_service='stq',
        transaction_payload={
            'alias_id': 'some_alias_id',
            'tariff_class': 'some_tariff_class',
            'driver': {
                'clid': 'some_park_id',
                'park_id': 'some_park_id',
                'driver_profile_id': 'some_driver_profile_id',
            }
        },
        user_login_id='t:1234', log_extra={'_link': {}},
    )
    assert response == _INVOICE_UPDATE_RESPONSE


@pytest.inline_callbacks
def test_invoice_compensation_create(patch):
    request_data = {
        'invoice_id': 'some_invoice_id',
        'operation_id': 'some_operation_id',
        'originator': 'processing',
        'version': 2,
        'gross_amount': '300.5',
        'acquiring_rate': '0.02',
        'product_id': 'taxi_100500_ride',
        'region_id': 225,
        'gateway_name': 'trust',
        'pass_params': {'foo': 'bar'},
    }
    _patch_perform_request(
        patch,
        'v2/invoice/compensation/create',
        request_data,
        _Response(_COMPENSATION_CREATE_RESPONSE),
    )
    yield transactions.invoice_compensation_create(
        api_version='v2',
        invoice_id='some_invoice_id',
        operation_id='some_operation_id',
        originator='processing',
        version=2,
        gross_amount=decimal.Decimal('300.5'),
        acquiring_rate=decimal.Decimal('0.02'),
        product_id='taxi_100500_ride',
        region_id=225,
        gateway_name='trust',
        pass_params={'foo': 'bar'},
        tvm_src_service='stq',
        log_extra={'_link': {}},
    )


@pytest.inline_callbacks
def test_invoice_compensation_refund(patch):
    request_data = {
        'invoice_id': 'some_invoice_id',
        'operation_id': 'some_operation_id',
        'originator': 'processing',
        'version': 2,
        'trust_payment_id': 'some_trust_payment_id',
        'net_amount': '200.5'
    }
    _patch_perform_request(
        patch,
        'v2/invoice/compensation/refund',
        request_data,
        _Response(_COMPENSATION_REFUND_RESPONSE),
    )
    yield transactions.invoice_compensation_refund(
        api_version='v2',
        invoice_id='some_invoice_id',
        operation_id='some_operation_id',
        originator='processing',
        version=2,
        trust_payment_id='some_trust_payment_id',
        net_amount=decimal.Decimal('200.5'),
        tvm_src_service='stq',
        log_extra={'_link': {}},
    )


def _patch_perform_request(
        patch, expected_location, expected_json_request, response
):
    @patch('taxi.external.transactions._perform_request')
    @async.inline_callbacks
    def _perform_request(method, location, json, tvm_src_service,
                         tvm_dst_service, log_extra):
        assert method == 'POST'
        assert location == expected_location
        assert json == expected_json_request
        assert tvm_src_service == 'stq'
        assert tvm_dst_service == 'transactions'
        assert log_extra == {'_link': {}}
        async.return_value(response)
        yield

    return _perform_request


class _Response(object):
    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json
