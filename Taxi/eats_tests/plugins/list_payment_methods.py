import typing

import pytest
import requests


PAYMENT_METHODS_HOST = (
    'http://eats-payment-methods-availability.eda.yandex.net'
)


class ListPaymentMethods:
    @staticmethod
    def set_payment_methods(data: typing.List):
        response = requests.post(
            PAYMENT_METHODS_HOST + '/set_payment_methods',
            json=data,
        )
        assert response.status_code == 200


@pytest.fixture
def list_payment_methods():
    return ListPaymentMethods()
