import pytest


@pytest.fixture(name='antifraud')
def mock_antifraud(mockserver):
    class Context:
        def __init__(self):
            self.is_fraud = True
            self.is_suspicious = False
            self.lavka_users = None
            self.antifraud_request = None
            self.order_nr = None
            self.personal_phone_id = None
            self.error_code = None
            self.short_address = None
            self.truncated_short_address = None
            self.frauder_short_address = None
            self.requests_with_full_flat = 0
            self.requests_with_truncated_flat = 0

        def set_error_code(self, code):
            self.error_code = code

        def set_is_fraud(self, is_fraud):
            self.is_fraud = is_fraud

        def set_frauder_address(self, short_address):
            self.frauder_short_address = short_address

        def set_is_suspicious(self, is_suspicious):
            self.is_suspicious = is_suspicious

        def set_lavka_users(self, lavka_users):
            self.lavka_users = lavka_users

        def times_antifraud_called(self):
            return _mock_antifraud.times_called

        def times_user_antifraud_called(self):
            return _mock_user_antifraud.times_called

        def times_order_antifraud_called(self):
            return _mock_order_antifraud.times_called

        def times_discount_antifraud_called(self):
            return _mock_discount_antifraud.times_called

        def times_full_flat_called(self):
            return self.requests_with_full_flat

        def times_truncated_flat_called(self):
            return self.requests_with_truncated_flat

        def check_antifraud_request(self, **kwargs):
            self.antifraud_request = kwargs

        def check_user_antifraud_request(self, personal_phone_id):
            self.personal_phone_id = personal_phone_id

        def check_order_antifraud_request(self, order_nr, short_address=None):
            self.order_nr = order_nr
            self.short_address = short_address

        def check_discount_antifraud(
                self, truncated_short_address=None, **kwargs,
        ):
            self.short_address = kwargs['short_address']
            self.truncated_short_address = truncated_short_address
            self.antifraud_request = kwargs

    context = Context()

    @mockserver.json_handler('/rt-xaron/lavka')
    def _mock_antifraud(request):
        if context.antifraud_request is not None:
            for key, value in context.antifraud_request.items():
                assert request.json[key] == value, key

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        if context.is_fraud:
            return {'result': [{'name': 'fraud', 'value': True}]}
        return {'result': []}

    @mockserver.json_handler('/rt-xaron/lavka/support-abuse-scoring/order')
    def _mock_order_antifraud(request):
        if context.order_nr is not None:
            assert context.order_nr == request.json['order_nr']

        if context.short_address is not None:
            assert context.short_address == request.json['short_address']

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        if context.is_fraud:
            return {'result': [{'name': 'eats_red', 'value': True}]}
        if context.is_suspicious:
            return {'result': [{'name': 'eats_grey', 'value': True}]}
        return {'result': [{'name': 'eats_green', 'value': True}]}

    @mockserver.json_handler('/rt-xaron/lavka/support-abuse-scoring/user')
    def _mock_user_antifraud(request):
        if context.personal_phone_id is not None:
            assert (
                context.personal_phone_id
                == request.json['user_personal_phone_id']
            )

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        values = []
        if context.is_fraud:
            values.append({'name': 'eats_red', 'value': True})
        elif context.is_suspicious:
            values.append({'name': 'eats_grey', 'value': True})
        else:
            values.append({'name': 'eats_green', 'value': True})

        if context.lavka_users:
            values.append({'name': 'lavka_users', 'value': True})

        return {'result': values}

    @mockserver.json_handler('/rt-xaron/lavka/discount-offer')
    def _mock_discount_antifraud(request):
        if context.antifraud_request is not None:
            for key, value in context.antifraud_request.items():
                if key == 'short_address':
                    if context.truncated_short_address == request.json[key]:
                        context.requests_with_truncated_flat += 1
                    elif context.short_address == request.json[key]:
                        context.requests_with_full_flat += 1
                    else:
                        assert False
                else:
                    assert request.json[key] == value, key

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        print('Hello')
        print(context.frauder_short_address)
        print(request.json['short_address'])
        if context.is_fraud:
            return {'result': [{'name': 'test_fraud', 'value': True}]}
        if context.frauder_short_address == request.json['short_address']:
            return {'result': [{'name': 'test_fraud', 'value': True}]}
        return {'result': []}

    return context
