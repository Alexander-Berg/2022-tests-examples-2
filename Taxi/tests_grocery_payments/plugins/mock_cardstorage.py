import json

import pytest

DEFAULT_ERROR_BODY = json.dumps({'code': '', 'message': ''})

DEFAULT_CARD = {
    'billing_card_id': 'not used',
    'bound': False,
    'busy': False,
    'busy_with': [],
    'card_id': 'default-payment-id-123',
    'currency': 'not used',
    'expiration_month': 2,
    'expiration_year': 22,
    'from_db': True,
    'number': '465858****7039',
    'owner': 'not used',
    'permanent_card_id': 'not used',
    'possible_moneyless': False,
    'region_id': 'not used',
    'regions_checked': [],
    'system': 'VISA',
    'unverified': False,
    'valid': True,
}


@pytest.fixture(name='cardstorage')
def mock_cardstorage(mockserver):
    class Context:
        def __init__(self):
            self.mocks = {}
            self.check_card_data = {}
            self.card_response = {}
            self.errors_codes = {}

        def mock_card(self, **argv):
            assert 'card_id' in argv
            self.card_response[argv['card_id']] = DEFAULT_CARD.copy()
            for key in argv:
                self.card_response[argv['card_id']][key] = argv[key]

        def check_card_request(self, **argv):
            assert 'card_id' in argv
            self.check_card_data[argv['card_id']] = {}
            for key in argv:
                self.check_card_data[argv['card_id']][key] = argv[key]

        def set_error_code(self, handler, code):
            self.errors_codes[handler] = code

        def times_card_called(self):
            return self.mocks['card'].times_called

    context = Context()

    def _make_error_response(error_code: int):
        body = {'code': str(error_code), 'message': f'{error_code} error'}
        return mockserver.make_response(json=body, status=error_code)

    @mockserver.json_handler('cardstorage/v1/card')
    def _mock_card(request):
        error_code = context.errors_codes.get('card', None)
        if error_code is not None:
            return mockserver.make_response(DEFAULT_ERROR_BODY, error_code)

        card_id = request.json['card_id']
        if context.check_card_data.get(card_id) is not None:
            for key, value in context.check_card_data[card_id].items():
                assert request.json[key] == value, key

        if card_id in context.card_response:
            return context.card_response[card_id]

        return _make_error_response(404)

    context.mocks['card'] = _mock_card

    return context
