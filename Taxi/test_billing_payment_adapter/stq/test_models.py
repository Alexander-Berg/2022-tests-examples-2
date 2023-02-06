# pylint: disable=protected-access

import datetime as dt
from typing import Optional

import pytest

from billing_payment_adapter.stq import config
from billing_payment_adapter.stq import models


@pytest.mark.parametrize(
    'order_doc, expected_invoice',
    [
        (
            {
                'billing_tech': {'version': 1, 'transactions': []},
                'payment_tech': {'type': 'applepay'},
                'performer': {'tariff': {'currency': 'RUB'}},
            },
            models.Invoice(
                version=1,
                payment_type='applepay',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yandex',
                is_roaming_user=False,
                billing_service=None,
            ),
        ),
        (
            {
                'billing_tech': {'version': 2, 'transactions': []},
                'payment_tech': {'type': 'card'},
                'performer': {'tariff': {'currency': 'USD'}},
                'source': 'uber',
                'request': {'is_roaming_user': True},
            },
            models.Invoice(
                version=2,
                payment_type='card',
                currency='USD',
                transactions=[],
                compensations=[],
                source='uber',
                is_roaming_user=True,
                billing_service=None,
            ),
        ),
    ],
)
def test_invoice_from_order_doc(
        order_doc: dict, expected_invoice: models.Invoice,
):
    assert expected_invoice == models.Invoice.from_order_doc(
        order_doc, config.PaymentsConfig({}, {}),
    )


@pytest.mark.parametrize(
    'invoice, expected_billing_type',
    [
        (
            models.Invoice(
                version=1,
                payment_type='card',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yandex',
                is_roaming_user=False,
                billing_service=None,
            ),
            models.BillingType.CARD,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='personal_wallet',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yandex',
                is_roaming_user=False,
                billing_service=None,
            ),
            models.BillingType.CARD,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='coop_account',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yandex',
                is_roaming_user=False,
                billing_service=None,
            ),
            models.BillingType.CARD,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='corp',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yandex',
                is_roaming_user=False,
                billing_service=None,
            ),
            models.BillingType.CORP,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='card',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='uber',
                is_roaming_user=False,
                billing_service=None,
            ),
            models.BillingType.UBER,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='card',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='uber',
                is_roaming_user=True,
                billing_service=None,
            ),
            models.BillingType.UBER_ROAMING,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='card',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yauber',
                is_roaming_user=False,
                billing_service=None,
            ),
            models.BillingType.UBER,
        ),
        (
            models.Invoice(
                version=1,
                payment_type='card',
                currency='RUB',
                transactions=[],
                compensations=[],
                source='yauber',
                is_roaming_user=False,
                billing_service='cargo',
            ),
            models.BillingType.UBER,
        ),
    ],
)
def test_invoice_get_billing_type(
        invoice: models.Invoice, expected_billing_type: models.BillingType,
):
    assert expected_billing_type == invoice.get_billing_type()


def _make_refund():
    return {
        'request_id': 'some_request_id',
        'status': 'clear_success',
        'refund_made_at': dt.datetime.utcnow(),
        'sum': {'ride': 1000000},
        'trust_refund_id': 'some_trust_refund_id',
    }


def _make_transaction_data(payload=None, refunds=None):
    result = {
        'request_id': 'some_request_id',
        'status': 'clear_success',
        'holded': dt.datetime.utcnow(),
        'cleared': dt.datetime.utcnow(),
        'sum': {'ride': 1000000},
        'trust_payment_id': 'some_trust_payment_id',
    }
    if payload is not None:
        result['transaction_payload'] = payload
    if refunds is not None:
        result['refunds'] = refunds
    return result


def _make_transaction_payload(
        alias_id='some_alias_id',
        tariff_class='econom',
        clid='some_clid',
        park_id: Optional[str] = 'some_db_id',
        driver_profile_id='some_db_id',
):
    result = {
        'alias_id': alias_id,
        'tariff_class': tariff_class,
        'driver': {'clid': clid, 'driver_profile_id': driver_profile_id},
    }
    if park_id is not None:
        result['driver']['park_id'] = park_id
    return result


@pytest.mark.parametrize(
    'payload, expected',
    [
        pytest.param(
            _make_transaction_payload(
                alias_id='some_alias_id',
                tariff_class='econom',
                clid='some_clid',
                park_id='some_db_id',
                driver_profile_id='some_uuid',
            ),
            models.TransactionPayload(
                alias_id='some_alias_id',
                tariff_class='econom',
                driver=models.Driver(
                    clid='some_clid', db_id='some_db_id', uuid='some_uuid',
                ),
            ),
            id='should parse dict into a dataclass',
        ),
        pytest.param(
            _make_transaction_payload(
                alias_id='some_alias_id',
                tariff_class='econom',
                clid='some_clid',
                park_id=None,
                driver_profile_id='some_uuid',
            ),
            models.TransactionPayload(
                alias_id='some_alias_id',
                tariff_class='econom',
                driver=models.Driver(
                    clid='some_clid', db_id=None, uuid='some_uuid',
                ),
            ),
            id='should parse dict into a dataclass when db_id is missing',
        ),
    ],
)
def test_transaction_payload_parse(payload, expected):
    actual = models.TransactionPayload.parse(payload)
    assert actual == expected


@pytest.mark.parametrize(
    'transaction_data, expected_is_none',
    [
        pytest.param(
            _make_transaction_data(payload=None),
            True,
            id='should work when transaction_payload is missing',
        ),
        pytest.param(
            _make_transaction_data(payload=_make_transaction_payload()),
            False,
            id='should work when transaction_payload is present',
        ),
    ],
)
def test_invoice_parse_transactions(transaction_data, expected_is_none):
    payments_config = _get_payments_config()

    # when we parse transactions with (maybe missing) payload
    parsed = models.Invoice._parse_transactions(
        transactions=[transaction_data], payments_config=payments_config,
    )

    # then we'll have 1 parsed transaction
    assert len(parsed) == 1

    # and this transaction.payload will be missing or present
    if expected_is_none:
        msg = 'transaction payload should be missing'
        assert parsed[0].payload is None, msg
    else:
        msg = 'transaction payload should be present'
        assert parsed[0].payload is not None, msg


@pytest.mark.parametrize(
    'transaction_data, expected_is_none',
    [
        pytest.param(
            _make_transaction_data(payload=None, refunds=[_make_refund()]),
            True,
            id='should work when transaction_payload is missing',
        ),
        pytest.param(
            _make_transaction_data(
                payload=_make_transaction_payload(), refunds=[_make_refund()],
            ),
            False,
            id='should work when transaction_payload is present',
        ),
    ],
)
def test_invoice_parse_transactions_with_refund(
        transaction_data, expected_is_none,
):
    payments_config = _get_payments_config()

    # when we parse transactions with (maybe missing) payload
    parsed = models.Invoice._parse_transactions(
        transactions=[transaction_data], payments_config=payments_config,
    )

    # then we'll have 2 parsed transactions (1 payment + 1 refund)
    assert len(parsed) == 2

    if expected_is_none:
        msg = 'transaction payload should be missing'
        assert parsed[0].payload is None, msg
        assert parsed[1].payload is None, msg
    else:
        msg = 'transaction payload should be present'
        assert parsed[0].payload is not None, msg
        assert parsed[1].payload is not None, msg


def _get_payments_config():
    payments_config = config.PaymentsConfig(
        {
            'ride': {
                'billing_orders_payment_kind': 'trip_payment',
                'is_ignored': False,
            },
        },
        {},
    )
    return payments_config
