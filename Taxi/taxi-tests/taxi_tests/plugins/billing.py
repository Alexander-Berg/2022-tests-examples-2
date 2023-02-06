import uuid

import pytest

from taxi_tests.utils import log_requests

BILLING_HOST = 'http://balance-simple.yandex.net:8018'


class Billing:

    @property
    def default_paymnet_methods(self):
        card = self.gen_any_success_card('x1111')
        return {'card-x1111': card}

    @staticmethod
    def gen_any_success_card(card_id=None):
        card_id = card_id or str(uuid.uuid1())
        card = {
            'auth_type': 'token',
            'name': '',
            'expiration_year': '2022',
            'proto': 'fake',
            'type': 'card',
            'expired': 0,
            'system': 'VISA',
            'number': '411111****1111',
            'expiration_month': '11',
            'currency': 'RUB',
            'binding_ts': 1484049108.142617,
            'service_labels': [],
            'holder': 'vvv',
            'id': card_id,
            'region_id': '225',
        }
        return card

    @staticmethod
    def change_payment_methods(uid, payment_methods, status='success',
                               rules=None):
        data = {
            'uid': uid,
            'status': status,
            'rules': rules or {},
            'payment_methods': payment_methods,
        }
        response = log_requests.post(BILLING_HOST + '/change_payment_methods',
                                     json=data)
        assert response.status_code == 200

    @staticmethod
    def get_data(uid):
        response = log_requests.post(BILLING_HOST + '/get_data',
                                     json={'uid': uid})
        assert response.status_code == 200
        return response.json()

    @staticmethod
    def set_basket_status(uid, trust_payment_id, status, extra=None):
        data = {
            'uid': uid,
            'trust_payment_id': trust_payment_id,
            'status': status,
        }
        if extra:
            data['extra'] = extra
        res = log_requests.post(BILLING_HOST + '/set_basket_status', json=data)
        assert res.status_code == 200


@pytest.fixture
def billing():
    return Billing()
