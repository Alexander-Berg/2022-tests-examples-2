import pytest
import requests

from grocery_tests import user_model


class GroceryOrdersService:
    def __init__(self):
        self.host = 'http://grocery-orders.lavka.yandex.net'

    def submit_v2(
            self, cart_json, user: user_model.GroceryUser,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/lavka/v1/orders/v2/submit',
            json={
                'cart_id': cart_json['cart_id'],
                'cart_version': cart_json['cart_version'],
                'offer_id': cart_json['offer_id'],
                'payment_method_type': 'card',
                'payment_method_id': 'card-x26e66e4d86fd3d070c6d7ffc',
                'position': {
                    'place_id': 'grocery',
                    'location': user.get_location(),
                },
                'flow_version': cart_json['order_flow_version'],
            },
            headers=user.get_headers(),
        )


@pytest.fixture
def orders():
    return GroceryOrdersService()
