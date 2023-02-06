import dataclasses
import typing

from tests_grocery_invoices import helpers
from tests_grocery_invoices import models


@dataclasses.dataclass
class SubItem:
    price: str
    quantity: str
    full_price: typing.Optional[str] = None


class ItemsContext:
    def __init__(self, country: models.Country):
        self.country = country
        self.items_v2: typing.List[models.GroceryCartItemV2] = []
        self.stq_items: typing.List[dict] = []

    def add_sub_items(
            self,
            item_id: str,
            items: typing.List[SubItem],
            vat=None,
            supplier_tin=None,
    ) -> models.GroceryCartItemV2:
        if vat is None:
            vat = helpers.get_vat(self.country)

        sub_items = []
        for idx, item in enumerate(items):
            sub_item = models.GroceryCartSubItem(
                item_id=f'{item_id}_{idx}',
                price=item.price,
                full_price=item.full_price,
                quantity=item.quantity,
            )
            sub_items.append(sub_item)

            self.stq_items.append(
                {
                    'item_id': sub_item.item_id,
                    'price': sub_item.price,
                    'quantity': sub_item.quantity,
                    'item_type': models.ItemType.product.name,
                },
            )

        self.items_v2.append(
            models.GroceryCartItemV2(
                item_id=item_id,
                sub_items=sub_items,
                title=item_id,
                vat=vat,
                supplier_tin=supplier_tin,
            ),
        )

        return self.items_v2[-1]
