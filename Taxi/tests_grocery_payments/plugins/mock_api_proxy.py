import copy

import pytest


MERCHANT_ID_LIST = ['value1', 'value2', 'value3']
SERVICE = 'grocery'
LOCATION = [37.62, 55.75]

CARD: dict = {
    'available': True,
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
}

APPLE_PAY = {'type': 'applepay'}

GOOGLE_PAY = {'type': 'googlepay'}

BADGE = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'оплата бейджиком',
    'id': 'badge:yandex_badge:RUB',
    'name': 'Yandex Badge',
    'type': 'corp',
}

CORP = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'eats 3796 of 10000 RUB',
    'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
    'name': 'corp-test',
    'type': 'corp',
}

CIBUS = {'type': 'cibus'}

SBP = {'type': 'sbp', 'id': 'sbp_qr'}


@pytest.fixture(name='api_proxy')
def mock_api_proxy(mockserver):
    class Context:
        def __init__(self):
            self.card_data = copy.deepcopy(CARD)
            self.applepay_data = copy.deepcopy(APPLE_PAY)
            self.googlepay_data = copy.deepcopy(GOOGLE_PAY)
            self.badge_data = copy.deepcopy(BADGE)
            self.corp_data = copy.deepcopy(CORP)
            self.cibus_data = copy.deepcopy(CIBUS)
            self.sbp_data = copy.deepcopy(SBP)
            self.extra_data = []

        def add_payment_method(self, data):
            self.extra_data.append(data)

        def lpm_times_called(self):
            return lpm_mock.times_called

        def flush(self):
            lpm_mock.flush()

    context = Context()

    @mockserver.json_handler(
        '/api-proxy-superapp-critical/4.0/payments/v1/list-payment-methods',
    )
    def lpm_mock(request):
        assert request.json == {'location': LOCATION}

        payment_methods = [
            context.card_data,
            context.applepay_data,
            context.googlepay_data,
            context.badge_data,
            context.corp_data,
            context.cibus_data,
            context.sbp_data,
        ] + context.extra_data

        payment_methods = [it for it in payment_methods if it is not None]

        return {
            'merchant_id_list': MERCHANT_ID_LIST,
            'payment_methods': payment_methods,
            'last_used_payment_method': {
                'id': 'badge:yandex_badge:RUB',
                'type': 'corp',
            },
        }

    return context
