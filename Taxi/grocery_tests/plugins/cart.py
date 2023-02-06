import pytest
import requests

from grocery_tests import user_model


class GroceryCartService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    # def retrieve(self, user: user_model.GroceryUser) -> requests.Response:
    #    return requests.post

    def add_product(
            self,
            offer_id: str,
            item_id: str,
            price: str,
            user: user_model.GroceryUser,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/lavka/v1/cart/v1/update',
            json={
                'offer_id': offer_id,
                'position': {'location': user.get_location()},
                'items': [
                    {
                        'id': item_id,
                        'quantity': '1',
                        'price': price,
                        'title': '',
                        'currency': 'RUB',
                    },
                ],
            },
            headers={'X-Idempotency-Token': 'we', **user.get_headers()},
        )

    def set_payment_method(
            self,
            offer_id: str,
            cart_id: str,
            cart_version: int,
            idempotency_token: str,
            user: user_model.GroceryUser,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/lavka/v1/cart/v1/set-payment',
            json={
                'offer_id': offer_id,
                'cart_id': cart_id,
                'cart_version': cart_version,
                'position': {'location': user.get_location()},
                'payment_method': {
                    'type': 'card',
                    'id': 'card-x26e66e4d86fd3d070c6d7ffc',
                },
            },
            headers={
                'X-Idempotency-Token': idempotency_token,
                **user.get_headers(),
            },
        )


@pytest.fixture
def cart():
    return GroceryCartService()
