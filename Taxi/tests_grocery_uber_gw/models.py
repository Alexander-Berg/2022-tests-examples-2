import random
import string
import uuid

STORE_CURSOR_LENGTH = 4
MERCHANT_STORE_ID_LENGTH = 10


class Store:
    def __init__(self, store_id=None, status=None, merchant_store_id=None):
        if store_id is None:
            store_id = str(uuid.uuid4())
        if status is None:
            status = 'ONLINE'
        if merchant_store_id is None:
            merchant_store_id = ''.join(
                random.choice(string.digits)
                for _ in range(MERCHANT_STORE_ID_LENGTH)
            )

        self.store_id = store_id
        self.status = status
        self.merchant_store_id = merchant_store_id
        self.cursor = ''.join(
            random.choice(string.digits + string.ascii_letters)
            for _ in range(STORE_CURSOR_LENGTH)
        )

    def get_data(self):
        data = {
            'store_id': self.store_id,
            'status': self.status,
            'merchant_store_id': self.merchant_store_id,
        }
        return data


class Order:
    def __init__(
            self,
            order_id=None,
            store_id=None,
            items=None,
            eater_phone=None,
            eater_phone_code=None,
            current_state=None,
            external_reference_id=None,
            store_external_reference_id=None,
    ):
        if order_id is None:
            order_id = str(uuid.uuid4())
        if store_id is None:
            store_id = str(uuid.uuid4())
        if items is None:
            items = []
        if current_state is None:
            current_state = 'CREATED'
        if external_reference_id is None:
            external_reference_id = str(uuid.uuid4())
        if store_external_reference_id is None:
            store_external_reference_id = ''.join(
                random.choice(string.digits)
                for _ in range(MERCHANT_STORE_ID_LENGTH)
            )
        self.order_id = order_id
        self.store = {
            'id': store_id,
            'external_reference_id': store_external_reference_id,
        }
        self.external_reference_id = external_reference_id
        self.current_state = current_state
        location = {'type': 'GOOGLE_PLACE', 'google_place_id': 'some_place_id'}
        eater = {
            'delivery': {'type': 'DELIVER_TO_DOOR', 'location': location},
            'phone': eater_phone,
            'phone_code': eater_phone_code,
        }
        eaters = [{'id': 'some_eater_id'}]
        self.eater = eater
        self.eaters = eaters
        self.cart = {'items': items}
        # TODO: add more fields from what @vinatorul sent me

    def get_data(self):
        data = {
            'id': self.order_id,
            'store': self.store,
            'external_reference_id': self.external_reference_id,
            'current_state': self.current_state,
            'eater': self.eater,
            'eaters': self.eaters,
            'cart': self.cart,
        }
        return data


class MenuItem:
    def __init__(
            self, item_id=None, title=None, price=None, suspend_until=None,
    ):
        if item_id is None:
            item_id = str(uuid.uuid4())
        if title is None:
            title = {'en': 'uber-item-title'}
        if price is None:
            price = 100

        self.item_id = item_id
        self.title = title
        self.price = price
        self.suspend_until = suspend_until

    def get_data(self):
        data = {
            'id': self.item_id,
            'title': self.title,
            'price_info': {'price': self.price},
        }
        if self.suspend_until is not None:
            data['suspension_info'] = {
                'suspension': {'suspend_until': self.suspend_until},
            }
        return data


class Menu:
    def __init__(self, store_id=None, menus=None, categories=None, items=None):
        if store_id is None:
            store_id = str(uuid.uuid4())
        if menus is None:
            menus = []
        if categories is None:
            categories = []
        if items is None:
            items = []

        self.store_id = store_id
        self.menus = menus
        self.categories = categories
        self.items = items

    def get_data(self):
        menus_data = []
        for menu in self.menus:
            menus_data.append(menu.get_data())

        categories_data = []
        for category in self.categories:
            categories_data.append(category.get_data())

        items_data = []
        for item in self.items:
            items_data.append(item.get_data())

        data = {
            'menus': menus_data,
            'categories': categories_data,
            'items': items_data,
        }
        return data
