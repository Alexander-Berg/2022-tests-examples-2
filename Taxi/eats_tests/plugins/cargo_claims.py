import pytest
import requests


CARGO_CLAIMS_HOST = 'http://b2b.taxi.yandex.net'


class CargoClaims:
    @staticmethod
    def add_performer_for_user(
            user_phone: str,
            yandex_uid: str,
            courier_id: int,
            name: str,
            legal_name: str,
    ):
        response = requests.post(
            url=CARGO_CLAIMS_HOST + '/add_performer',
            json={
                'user_phone': user_phone,
                'yandex_uid': yandex_uid,
                'courier_id': courier_id,
                'name': name,
                'legal_name': legal_name,
            },
        )
        assert response.status_code == 200

    @staticmethod
    def mark_order_as_delivered(order_nr: str):
        response = requests.post(
            url=CARGO_CLAIMS_HOST + '/mark_order_as_delivered',
            json={'order_nr': order_nr},
        )
        assert response.status_code == 200


@pytest.fixture
def cargo_claims():
    return CargoClaims()
