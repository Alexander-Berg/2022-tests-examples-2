import datetime
import decimal

from taxi.billing.clients.models import billing_orders as orders_models

from taxi_billing_subventions.common import models

_DEFAULT_KWARGS = {
    'amount': '100',
    'currency': 'RUB',
    'invoice_date': datetime.datetime(2019, 12, 1, 21),
    'contract_id': '',
    'billing_client_id': 'billing_client_id',
    'payload': {},
}


def make_subvention_payment(attrs: dict) -> orders_models.PaymentEntry:
    default_kwargs = dict(_DEFAULT_KWARGS, payment_kind='subvention')
    default_kwargs.update(attrs)
    return orders_models.PaymentEntry(**default_kwargs)  # type: ignore


def make_commission_payment(attrs: dict) -> orders_models.PaymentEntry:
    default_kwargs = dict(
        _DEFAULT_KWARGS, payment_kind='commission/driver_fix',
    )
    default_kwargs.update(attrs)
    return orders_models.PaymentEntry(**default_kwargs)  # type: ignore


def make_payout_info(attrs: dict) -> models.PayoutInfo:
    default_kwargs = dict(
        payments=[],
        amount_for_park_commission=decimal.Decimal(0),
        driver_income_info=None,
    )
    default_kwargs.update(attrs)
    return models.PayoutInfo(**default_kwargs)  # type: ignore


def make_driver_income_info(attrs: dict) -> models.DriverIncomeInfo:
    default_kwargs = dict(
        on_order_minutes=decimal.Decimal(0),
        free_minutes=decimal.Decimal(0),
        payout=None,
    )
    default_kwargs.update(attrs)
    return models.DriverIncomeInfo(**default_kwargs)  # type: ignore
