# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error

import dataclasses
import decimal
import enum
import typing

from grocery_mocks.models import country as country_models
from grocery_payments_shared import models as shared_models

from . import consts

# pylint: disable=invalid-name
Decimal = decimal.Decimal
Country = country_models.Country
InvoiceOriginator = shared_models.InvoiceOriginator


class PaymentType(enum.Enum):
    card = 'card'
    googlepay = 'googlepay'
    applepay = 'applepay'
    personal_wallet = 'personal_wallet'
    badge = 'badge'
    corp = 'corp'
    cibus = 'cibus'
    sbp = 'sbp'


@dataclasses.dataclass
class PaymentMethod:
    payment_type: PaymentType
    payment_id: str
    payment_meta: typing.Optional[dict] = None

    def _is_card_like(self):
        return self.payment_type in (
            PaymentType.card,
            PaymentType.applepay,
            PaymentType.googlepay,
            PaymentType.cibus,
        )

    def to_transactions(self):
        if self._is_card_like():
            return {'method': self.payment_id, 'type': self.payment_type.value}

        if self.payment_type == PaymentType.personal_wallet:
            return {
                'account': {'id': consts.PERSONAL_WALLET_ID},
                'method': consts.PERSONAL_WALLET_ID,
                'service': consts.WALLET_SERVICE,
                'type': self.payment_type.value,
            }

        if self.payment_type == PaymentType.badge:
            return {
                'method': consts.PAYMENT_ID,
                'payer_login': consts.STAFF_LOGIN,
                'type': self.payment_type.value,
            }

        if self.payment_type == PaymentType.corp:
            return {
                'method': self.payment_id,
                'type': self.payment_type.value,
                'billing_id': '',
            }

        if self.payment_type == PaymentType.sbp:
            return {'method': self.payment_id, 'type': self.payment_type.value}

        assert False, 'unimplemented payment_type: ' + self.payment_type.value
        return None

    def to_request(self):
        res = {'type': self.payment_type.value, 'id': self.payment_id}

        if self.payment_meta is not None:
            res['meta'] = self.payment_meta

        return res


@dataclasses.dataclass
class ReceiptInfo:
    title: str
    vat: str
    personal_tin_id: str

    def to_request(self):
        return {
            'title': self.title,
            'vat': self.vat,
            'personal_tin_id': self.personal_tin_id,
        }

    def to_transactions(self):
        res = {
            'title': self.title,
            'vat': f'nds_{self.vat}',
            'personal_tin_id': self.personal_tin_id,
        }
        return res


class ItemType(enum.Enum):
    product = 'product'
    delivery = 'delivery'
    tips = 'tips'
    helping_hand = 'helping_hand'
    service_fee = 'service_fee'


@dataclasses.dataclass
class Item:
    item_id: str
    price: str
    quantity: str
    item_type: ItemType = ItemType.product
    receipt_info: typing.Optional[ReceiptInfo] = None

    @property
    def amount(self) -> str:
        return str(Decimal(self.price) * Decimal(self.quantity))

    def copy(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

    def to_request_item(self):
        res = {
            'item_id': self.item_id,
            'price': self.price,
            'quantity': self.quantity,
        }

        if self.receipt_info is not None:
            res['receipt_info'] = self.receipt_info.to_request()

        if self.item_type is not None:
            res['item_type'] = self.item_type.value

        return res

    def to_operation_item(self, product_id=None):
        res = {
            'item_id': Item.typed_item_id(self.item_id, self.item_type),
            'amount': self.amount,
        }

        if product_id is not None:
            res['product_id'] = product_id

        if self.receipt_info is not None:
            res['fiscal_receipt_info'] = self.receipt_info.to_transactions()

        return res

    def to_transaction_item(self):
        res = {
            'item_id': Item.typed_item_id(self.item_id, self.item_type),
            'amount': self.amount,
        }

        return res

    @staticmethod
    def sub_item_id(item_id, index):
        return f'{item_id}::sub{index}'

    @staticmethod
    def typed_item_id(item_id, item_type: ItemType):
        if item_type == ItemType.product:
            return item_id
        return f'{item_id}:{item_type.value}'

    def to_sub(self, index, quantity=None):
        return self.copy(
            item_id=Item.sub_item_id(self.item_id, index),
            quantity=quantity or self.quantity,
        )

    def split_quantity(self):
        quantity = int(self.quantity)
        if quantity <= 0:
            return [self.to_sub(0, '0')]
        return [self.to_sub(i, '1') for i in range(0, quantity)]


@dataclasses.dataclass
class OperationSum:
    items: typing.List[Item]
    payment_type: PaymentType

    def to_object(self, product_id=None):
        return {
            'items': to_operation_items(self.items, product_id),
            'payment_type': self.payment_type.value,
        }

    def to_transaction_sum(self):
        return to_transaction_items(self.items)

    def amount(self):
        result = Decimal(0)
        for item in self.items:
            result += Decimal(item.amount)
        return str(result)

    def get(self, item_id):
        for item in self.items:
            if item.item_id == item_id:
                return item

        return None

    def clear(self):
        for item in self.items:
            item.quantity = '0'

    def remove_item(self, item_id, quantity=None):
        result = OperationSum([], self.payment_type)

        for item in self.items:
            if item.item_id == item_id:
                quantity = quantity or item.quantity
                item_quantity = Decimal(item.quantity) - Decimal(quantity)
                if item_quantity <= 0:
                    self.items.remove(item)
                else:
                    item.quantity = str(item_quantity)

                item_copy = item.copy(quantity=str(quantity))
                result.items.append(item_copy)
                break

        return result


@dataclasses.dataclass
class TransactionsCallback:
    invoice_id: str
    operation_id: str
    notification_type: str = consts.OPERATION_FINISH
    operation_status: str = consts.OPERATION_DONE


@dataclasses.dataclass
class DeferredTask:
    invoice_id: str
    task_id: str
    status: str = 'init'
    payload: typing.Optional[dict] = None


@dataclasses.dataclass
class InvoiceOperationPg:
    invoice_id: str
    operation_id: str


@dataclasses.dataclass
class SbpBankInfo:
    bank_name: str
    logo_url: str = 'logo_url'
    schema: str = 'schema'
    package_name: str = 'package_name'

    def to_raw(self):
        return dict(
            bankName=self.bank_name,
            logoURL=self.logo_url,
            schema=self.schema,
            package_name=self.package_name,
        )

    def to_raw_response(self):
        return dict(
            bank_name=self.bank_name,
            logo_url=self.logo_url,
            schema=self.schema,
            package_name=self.package_name,
        )

    def to_exp_meta(self):
        return dict(bank_name=self.bank_name)

    def to_dict(self):
        return dataclasses.asdict(self)


def to_sub_items(items: typing.List[Item]):
    result = []
    for item in items:
        result.extend(item.split_quantity())
    return result


def to_request_items(items: typing.List[Item]):
    return [item.to_request_item() for item in items]


def to_operation_items(items: typing.List[Item], product_id=None):
    return [item.to_operation_item(product_id) for item in to_sub_items(items)]


def to_transaction_items(items: typing.List[Item]):
    return [item.to_transaction_item() for item in to_sub_items(items)]


def to_invoices_callback_items(items: typing.List[Item]):
    return [item.to_request_item() for item in items]
