import dataclasses
import datetime
import decimal
from typing import Dict
from typing import List
from typing import Optional


@dataclasses.dataclass
class Compensation:
    compensation_id: str
    order_id: str
    payload: Dict
    status: str
    created: datetime.datetime
    updated: Optional[datetime.datetime]
    compensation_type: str


@dataclasses.dataclass
class Reward:
    order_id: str
    reward_id: str
    yandex_uid: str
    type: str
    amount: decimal.Decimal


@dataclasses.dataclass
class TransactionItem:
    item_id: str
    quantity: str
    amount: str

    def get_price(self):
        return str(
            decimal.Decimal(self.amount) / decimal.Decimal(self.quantity),
        )


@dataclasses.dataclass
class Transaction:
    items: List[TransactionItem]
    status: str


@dataclasses.dataclass
class Product:
    item_id: str
    quantity: str
    amount: str

    def get_price(self):
        return str(
            decimal.Decimal(self.amount) / decimal.Decimal(self.quantity),
        )
