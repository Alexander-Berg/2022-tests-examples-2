# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
# pylint: disable=invalid-name

import dataclasses
import datetime
import typing

from grocery_payments_shared import models as shared_models

from . import consts

InvoiceOriginator = shared_models.InvoiceOriginator


def debt_reason(**kwargs):
    return {
        'payment_type': 'card',
        'error_reason_code': 'error_reason_code',
        'is_technical_error': True,
        **kwargs,
    }


def debt_payload(originator=InvoiceOriginator.grocery, **kwargs):
    return {
        'reason': debt_reason(),
        'user': consts.USER_INFO,
        'originator': originator.name,
        **kwargs,
    }


def prediction_payload(originator=InvoiceOriginator.grocery, **kwargs):
    return {'originator': originator.name, **kwargs}


class DebtStatus:
    init = 'init'
    canceled = 'canceled'
    cleared = 'cleared'
    forgiven = 'forgiven'

    values = (init, canceled, cleared, forgiven)


@dataclasses.dataclass
class Debt:
    debt_id: str = consts.DEBT_ID
    status: str = DebtStatus.init
    priority: typing.Optional[int] = None
    payload: dict = dataclasses.field(default_factory=debt_payload)
    order_id: typing.Optional[str] = None
    invoice_id: typing.Optional[str] = None
    created: datetime.datetime = datetime.datetime.now()
    updated: datetime.datetime = datetime.datetime.now()

    def __post_init__(self):
        if self.order_id is None:
            self.order_id = self.debt_id
        if self.invoice_id is None:
            self.invoice_id = self.debt_id

    def copy(self, **kwargs):
        return dataclasses.replace(self, **kwargs)


@dataclasses.dataclass
class Prediction:
    order_id: str
    debt_id: str
    yandex_uid: str
    expected: str
    actual: str
    payload: typing.Optional[dict]
    created: datetime.datetime = datetime.datetime.now()
    updated: datetime.datetime = datetime.datetime.now()
