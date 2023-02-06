# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks.models import cart
# pylint: enable=import-error

# pylint: disable=invalid-name
GroceryCartItem = cart.GroceryCartItem
GroceryCartSubItem = cart.GroceryCartSubItem
GroceryCartItemV2 = cart.GroceryCartItemV2
# pylint: enable=invalid-name


class Product:
    def __init__(self, product_id, name, price, count):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._count = count

    def get_json(self):
        return {
            'name': self._name,
            'cost': self._price,
            'count': self._count,
            'product_id': self._product_id,
        }


class OverlordCategory:
    def __init__(self, category_id, parent_category_id=None):
        self._id = category_id
        self._parent_id = parent_category_id

    def get_json(self):
        return {'id': self._id, 'category_parent_id': self._parent_id}


class OverlordProduct:
    def __init__(self, product_id, category_ids):
        self._id = product_id
        self._category_ids = category_ids

    def get_json(self):
        return {
            'id': self._id,
            'category_ids': self._category_ids,
            'full_price': '0',
            'rank': 0,
        }


class Pricing:
    def __init__(self, price):
        self.price = price

    def get_data(self):
        return {'price': self.price}


class MarketProduct:
    def __init__(self, product_id, price, discount_price, restrictions):
        self.type = 'market-good'
        self.product_id = product_id
        self.title = 'some-good-title'
        self.available = True
        self.image_url_templates = ['some-image-url-template']
        self.pricing = Pricing(price)
        self.discount_pricing = Pricing(discount_price)
        self.restrictions = restrictions
        self.market_product_url = 'some-market-product-url'

    def get_data(self):
        return {
            'type': self.type,
            'id': self.product_id,
            'title': self.title,
            'available': self.available,
            'image_url_templates': self.image_url_templates,
            'pricing': self.pricing.get_data(),
            'discount_pricing': self.discount_pricing.get_data(),
            'restrictions': self.restrictions,
            'market_product_url': self.market_product_url,
        }
