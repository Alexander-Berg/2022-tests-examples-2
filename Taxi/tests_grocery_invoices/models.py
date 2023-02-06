# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
import dataclasses
import datetime
import decimal
import enum
import typing

from grocery_mocks.models import cart
from grocery_mocks.models import country as country_models

from tests_grocery_invoices import consts

# pylint: disable=invalid-name
GroceryCartItem = cart.GroceryCartItem
GroceryCartSubItem = cart.GroceryCartSubItem
GroceryCartItemV2 = cart.GroceryCartItemV2
Country = country_models.Country
# pylint: enable=invalid-name


class ItemType(enum.Enum):
    product = 'product'
    delivery = 'delivery'
    tips = 'tips'
    charity = 'charity'
    service_fee = 'service_fee'


@dataclasses.dataclass
class Item:
    item_id: str
    price: str
    quantity: str
    vat: typing.Optional[str] = consts.DEFAULT_VAT
    title: typing.Optional[str] = None
    full_price: typing.Optional[str] = None
    item_type: typing.Optional[str] = None

    def price_with_vat(self):
        price = decimal.Decimal(self.price)

        return '{0:.2f}'.format(price)

    def total(self):
        price = decimal.Decimal(self.price)
        quantity = decimal.Decimal(self.quantity)

        return '{0:.2f}'.format(price * quantity)

    def total_vat(self):
        total_without_vat = decimal.Decimal(self.total_without_vat())
        total = decimal.Decimal(self.total())

        return '{0:.2f}'.format(total - total_without_vat)

    def total_without_vat(self):
        total = decimal.Decimal(self.total())
        vat = decimal.Decimal(self.vat)
        percent100 = decimal.Decimal(100)

        return '{0:.2f}'.format(total * percent100 / (percent100 + vat))

    def to_json(self):
        return {
            'item_id': self.item_id,
            'price': self.price,
            'quantity': self.quantity,
            'item_type': self.item_type,
        }


def items_to_json(items: typing.List[Item]):
    return [it.to_json() for it in items]


class PaymentType(enum.Enum):
    card = 'card'
    applepay = 'applepay'
    googlepay = 'googlepay'
    badge = 'badge'
    corp = 'corp'
    cibus = 'cibus'
    sbp = 'sbp'


class ReceiptType(enum.Enum):
    payment = 'payment'
    refund = 'refund'


@dataclasses.dataclass
class PaymentMethod:
    payment_type: PaymentType
    payment_method_id: str


def receipt_payload(country=Country.Russia, **kwargs):
    return {'country': country.name, **kwargs}


@dataclasses.dataclass
class Receipt:
    order_id: str = consts.ORDER_ID
    receipt_id: str = 'receipt_id'
    receipt_data_type: str = consts.ORDER_RECEIPT_DATA_TYPE
    items: list = dataclasses.field(default_factory=list)
    total: decimal.Decimal = decimal.Decimal(0)
    receipt_type: str = ReceiptType.payment.name
    link: str = 'https://url.pdf'
    receipt_source: str = consts.EATS_RECEIPTS
    payload: dict = dataclasses.field(default_factory=receipt_payload)
    created: datetime.datetime = consts.NOW_DT

    def to_json(self):
        result = dataclasses.asdict(self)
        result.update(
            item_id=self.order_id,
            total=str(self.total),
            created=self.created.isoformat(),
        )
        return result


@dataclasses.dataclass
class EasyCountPayment:
    payment_sum: str
    payment_type: int
    cc_deal_type: typing.Optional[int]
    cc_number: typing.Optional[str]
    cc_type: typing.Optional[int]
    other_payment_type_name: typing.Optional[str]

    def to_json(self):
        res = {
            'payment_sum': self.payment_sum,
            'payment_type': self.payment_type,
        }

        if self.cc_deal_type is not None:
            res['cc_deal_type'] = self.cc_deal_type

        if self.cc_number is not None:
            res['cc_number'] = self.cc_number

        if self.cc_type is not None:
            res['cc_type'] = self.cc_type

        if self.other_payment_type_name is not None:
            res['other_payment_type_name'] = self.other_payment_type_name

        return res


class TaskType(enum.Enum):
    invoice_callback = 'invoice_callback'
    receipt_polling = 'receipt_polling'


class TaskStatus(enum.Enum):
    in_process = 'in_process'
    failed = 'failed'
    canceled = 'canceled'
    success = 'success'
    pending_cancel = 'pending_cancel'


@dataclasses.dataclass
class Task:
    task_id: str
    task_type: str
    order_id: str
    status: str
    args: dict
    result_payload: dict
    params: dict
    created: typing.Optional[datetime.datetime] = consts.NOW_DT
