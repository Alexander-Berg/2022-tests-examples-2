import dataclasses
import decimal
import enum
import typing

from tests_eats_payments import configs
from tests_eats_payments import consts


class ItemType(enum.Enum):
    delivery = 'delivery'
    product = 'product'
    tips = 'tips'
    option = 'option'
    assembly = 'assembly'
    retail = 'retail'
    service_fee = 'service_fee'


@dataclasses.dataclass
class Complement:
    amount: str
    item_types_amount: typing.Optional[list] = None
    payment_type: str = 'personal_wallet'
    payment_id: str = 'complement-id'
    service: str = consts.DEFAULT_SERVICE
    need_wallet_payload: bool = True

    def get_transaction_payment(self):
        return {
            'account': {'id': self.payment_id},
            'method': self.payment_id,
            'service': configs.PERSONAL_WALLET_SERVICE[self.service],
            'type': self.payment_type,
        }

    def is_have_wallet_payload(self):
        return self.need_wallet_payload


@dataclasses.dataclass
class ComplementCorp:
    amount: str
    payment_type: str = 'corp'
    payment_id: str = 'complement-id'
    billing_id: str = ''
    need_wallet_payload: bool = False

    def get_transaction_payment(self):
        return {
            'billing_id': self.billing_id,
            'method': self.payment_id,
            'type': self.payment_type,
        }

    def is_have_wallet_payload(self):
        return self.need_wallet_payload


@dataclasses.dataclass
class BillingInfo:
    place_id: str = 'some_place_id'
    balance_client_id: str = 'balance_client_id'
    item_type: ItemType = ItemType.product

    def to_json_object(self):
        return {
            'place_id': self.place_id,
            'balance_client_id': self.balance_client_id,
            'item_type': self.item_type.value,
        }


@dataclasses.dataclass
class TestItem:
    price: typing.Optional[str] = None
    quantity: typing.Optional[str] = None
    amount: typing.Optional[str] = None
    by_complement: typing.Optional[str] = None
    item_type: ItemType = ItemType.product
    billing_info: typing.Optional[BillingInfo] = None
    item_id: typing.Optional[str] = None
    product_id: typing.Optional[str] = None

    def price_without_complement(self):
        by_complement = decimal.Decimal(
            self.by_complement if self.by_complement is not None else '0',
        )

        if self.amount is not None:
            return str(decimal.Decimal(self.amount) - by_complement)
        if self.price is not None and self.quantity is not None:
            price_without_complement = (
                decimal.Decimal(self.price) - by_complement
            )
            price_without_complement *= decimal.Decimal(self.quantity)

            return str(price_without_complement)
        return None

    def billing_info_as_json_object(self):
        if self.billing_info is None:
            return None
        return self.billing_info.to_json_object()
