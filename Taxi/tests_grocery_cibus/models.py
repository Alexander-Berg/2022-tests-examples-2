import dataclasses
import datetime
import enum
import typing

from . import consts


class TransactionType(enum.Enum):
    payment = 'payment'
    refund = 'refund'


class TransactionStatus(enum.Enum):
    success = 'success'
    pending = 'pending'
    fail = 'fail'


class PaymentStatus(enum.Enum):
    init = 'init'
    success = 'success'
    canceled = 'canceled'
    fail = 'fail'


class PaymentError(enum.Enum):
    unknown_error = 'unknown_error'
    token_expired = 'token_expired'
    user_inactive = 'user_inactive'
    user_blocked = 'user_blocked'
    payment_failed = 'payment_failed'
    bad_time = 'bad_time'
    limits_of_deals = 'limits_of_deals'
    budget_limit = 'budget_limit'
    restaurant_not_approved = 'restaurant_not_approved'
    exceed_system_price_limit = 'exceed_system_price_limit'


@dataclasses.dataclass
class Transaction:
    invoice_id: str = consts.ORDER_ID
    transaction_id: str = consts.TRANSACTION_ID
    transaction_type: TransactionType = TransactionType.payment
    items: list = dataclasses.field(default_factory=list)
    status: TransactionStatus = TransactionStatus.success
    error_code: typing.Optional[str] = None
    error_desc: typing.Optional[str] = None
    created: datetime.datetime = consts.NOW_DT


@dataclasses.dataclass
class Payment:
    order_id: str = consts.ORDER_ID
    invoice_id: str = consts.ORDER_ID
    token: str = consts.DEFAULT_TOKEN
    yandex_uid: str = consts.YANDEX_UID
    status: PaymentStatus = PaymentStatus.init
    deal_price: int = 0
    redirect_url: str = consts.REDIRECT_URL
    application_id: str = consts.APPLICATION_ID
    deal_id: typing.Optional[int] = None
    error_code: typing.Optional[str] = None
    error_desc: typing.Optional[str] = None


def make_transaction_item(item_id: str, amount: str):
    return {'item_id': item_id, 'amount': amount}
