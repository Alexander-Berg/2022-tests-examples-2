# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
import enum

from grocery_mocks.models import cart
from grocery_mocks.models import country

# pylint: disable=invalid-name
GroceryCartItem = cart.GroceryCartItem
GroceryCartSubItem = cart.GroceryCartSubItem
GroceryCartItemV2 = cart.GroceryCartItemV2
Country = country.Country


# pylint: enable=invalid-name


class ReceiptType(enum.Enum):
    Payment = 'payment'
    Refund = 'refund'


class ReceiptDataType(enum.Enum):
    Order = 'order'
    Delivery = 'delivery'
    Tips = 'tips'
    HelpingHand = 'helping_hand'


def receipt_item(
        item_id: str, price: str, quantity: str, item_type: str = 'product',
):
    return {
        'item_id': item_id,
        'price': price,
        'quantity': quantity,
        'item_type': item_type,
    }
