import pytest
import requests


class EatsCart:
    def __init__(self):
        self.host = None
        self.headers = {'Content-Type': 'application/json'}

    def set_host(self, host: str):
        self.host = host

    def add_item(
            self,
            item_id: str,
            eater_id: int,
            passport_uid: int,
            phone_id: str,
            email_id: str,
            latitude: float,
            longitude: float,
    ):
        return requests.post(
            url=f'{self.host}/api/v1/cart',
            params={
                'latitude': latitude,
                'longitude': longitude,
            },
            json={'item_id': item_id, 'quantity': 1, 'item_options': []},
            headers={
                'X-YaTaxi-Session': 'eats:in',
                'X-Eats-User': (
                    f'user_id={eater_id},'
                    f'personal_phone_id={phone_id},'
                    f'personal_email_id={email_id}'
                ),
                'X-YaTaxi-Bound-UserIds': '',
                'X-YaTaxi-Bound-Sessions': '',
                'X-Yandex-UID': str(passport_uid),
            },
        )


@pytest.fixture
def eats_cart():
    return EatsCart()
