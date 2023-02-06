import dataclasses
import decimal
import typing
from typing import List
from typing import Optional

DEFAULT_DEPOT_ID = '2809'


@dataclasses.dataclass
class GroceryCartItem:
    item_id: str
    title: str = 'title'
    price: str = '10.15'
    full_price: Optional[str] = None
    quantity: str = '3'
    currency: str = 'RUB'
    vat: str = '20'
    refunded_quantity: str = '0'
    gross_weight: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    depth: Optional[int] = None
    dropoff_point: Optional[int] = 2
    cashback_per_unit: Optional[str] = None

    def as_object(self):
        full_price = {}
        if self.full_price:
            full_price = {'full_price': self.full_price}
        measurements = {}
        if self.gross_weight:
            measurements['gross_weight'] = self.gross_weight
        if self.width:
            measurements['width'] = self.width
        if self.height:
            measurements['height'] = self.height
        if self.depth:
            measurements['depth'] = self.depth

        return {
            'id': self.item_id,
            'product_key': {
                'id': _get_raw_item_id(self.item_id),
                'shelf_type': _get_shelf_type(self.item_id),
            },
            'title': self.title,
            'price': self.price,
            'price_template': _to_template(self.price),
            'quantity': self.quantity,
            'currency': self.currency,
            'vat': self.vat,
            'refunded_quantity': self.refunded_quantity,
            'cashback_per_unit': self.cashback_per_unit,
            **full_price,
            **measurements,
        }

    def as_object_v2(self):
        info = {
            'item_id': self.item_id,
            'shelf_type': _get_shelf_type(self.item_id),
            'title': self.title,
            'refunded_quantity': self.refunded_quantity,
            # ~220 tests break without this 'or' for some reason
            'vat': self.vat or '17',
        }

        full_price = self.full_price or self.price
        sub_items = [
            {
                'item_id': self.item_id + '_0',
                'price': self.price,
                'full_price': full_price,
                'quantity': self.quantity,
            },
        ]

        return {'info': info, 'sub_items': sub_items}

    def as_cargo_object(self):
        weight = {}

        divisor = 1000
        if self.gross_weight:
            weight = {'weight': self.gross_weight / divisor}
        size = {}
        if self.width and self.height and self.depth:
            size = {
                'size': {
                    'width': self.width / divisor,
                    'height': self.height / divisor,
                    'length': self.depth / divisor,
                },
            }

        return {
            'extra_id': self.item_id,
            'title': self.title,
            'cost_value': self.price,
            'quantity': int(self.quantity),
            'cost_currency': self.currency,
            'pickup_point': 1,
            'droppof_point': self.dropoff_point,
            **weight,
            **size,
        }

    def total_price(self):
        price = decimal.Decimal(self.price)
        quantity = decimal.Decimal(self.quantity)

        return str(price * quantity)

    def discount(self):
        quantity = decimal.Decimal(self.quantity)

        if self.full_price is not None:
            full_price = self.full_price
        else:
            full_price = self.price

        full_total = decimal.Decimal(full_price) * quantity
        total = decimal.Decimal(self.total_price())
        return str(full_total - total)

    def set_refunded_quantity(self, quantity):
        self.refunded_quantity = quantity


@dataclasses.dataclass
class GroceryCartSubItem:
    item_id: str
    price: str
    full_price: str
    quantity: str
    paid_with_cashback: typing.Optional[str] = None
    paid_with_promocode: typing.Optional[str] = None
    price_exchanged: typing.Optional[str] = None

    def amount_full_price(self):
        full_price = decimal.Decimal(self.full_price)
        quantity = decimal.Decimal(self.quantity)

        return str(full_price * quantity)

    def amount_discounts(self):
        full_price = decimal.Decimal(self.full_price)
        price = decimal.Decimal(self.price)
        paid_with_cashback = decimal.Decimal(self.paid_with_cashback or '0')
        paid_with_promocode = decimal.Decimal(self.paid_with_promocode or '0')
        quantity = decimal.Decimal(self.quantity)
        discout = full_price - price - paid_with_cashback - paid_with_promocode

        return str(discout * quantity)

    def amount_paid_with_cashback(self):
        paid_with_cashback = decimal.Decimal(self.paid_with_cashback or '0')
        quantity = decimal.Decimal(self.quantity)

        return str(paid_with_cashback * quantity)

    def amount_paid_with_promocode(self):
        paid_with_promocode = decimal.Decimal(self.paid_with_promocode or '0')
        quantity = decimal.Decimal(self.quantity)

        return str(paid_with_promocode * quantity)


@dataclasses.dataclass
class GroceryCartItemV2:
    item_id: str
    sub_items: List[GroceryCartSubItem]
    title: str = 'title'
    shelf_type: str = 'store'
    vat: str = '20'
    refunded_quantity: str = '0'
    supplier_tin: typing.Optional[str] = None

    def amount_full_price(self):
        amount = decimal.Decimal(0)
        for sub_item in self.sub_items:
            amount += sub_item.amount_full_price()
        return str(amount)

    def amount_discounts(self):
        amount = decimal.Decimal(0)
        for sub_item in self.sub_items:
            amount += sub_item.amount_discounts()
        return str(amount)

    def amount_paid_with_cashback(self):
        amount = decimal.Decimal(0)
        for sub_item in self.sub_items:
            amount += sub_item.amount_paid_with_cashback()
        return str(amount)

    def amount_paid_with_promocode(self):
        amount = decimal.Decimal(0)
        for sub_item in self.sub_items:
            amount += sub_item.amount_paid_with_promocode()
        return str(amount)

    def as_object(self):
        supplier_tin = {}
        if self.supplier_tin is not None:
            supplier_tin['supplier_tin'] = self.supplier_tin

        info = {
            'item_id': self.item_id,
            'title': self.title,
            'shelf_type': self.shelf_type,
            'refunded_quantity': self.refunded_quantity,
            'vat': self.vat,
            **supplier_tin,
        }

        sub_items = list(
            map(
                lambda x: {
                    'item_id': x.item_id,
                    'price': x.price,
                    'full_price': x.full_price,
                    'quantity': x.quantity,
                    'paid_with_cashback': x.paid_with_cashback,
                    'paid_with_promocode': x.paid_with_promocode,
                    'price_exchanged': x.price_exchanged,
                },
                self.sub_items,
            ),
        )

        return {'info': info, 'sub_items': sub_items}


def _get_raw_item_id(item_id):
    return item_id.split(':')[0]


def _get_shelf_type(item_id):
    if 'st-pa' in item_id:
        return 'parcel'
    if 'st-md' in item_id:
        return 'markdown'
    return 'store'


def _to_template(price):
    return f'{str(price)} $SIGN$$CURRENCY$'
