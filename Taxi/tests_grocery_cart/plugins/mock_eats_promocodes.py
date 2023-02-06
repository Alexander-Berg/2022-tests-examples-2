import pytest


@pytest.fixture(name='eats_promocodes')
def mock_eats_promocodes(mockserver):
    discount_body = discount_payload(discount=0)
    check_request_values = {}

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def validate_promocode(_request):
        body = _request.json

        for key, value in check_request_values.items():
            assert body[key] == value
        return discount_body

    class Context:
        def set_discount(self, discount):
            discount_body.update(discount_payload(discount))

        def times_called(self):
            return validate_promocode.times_called

        def set_valid(self, valid):
            discount_body['payload']['validationResult']['valid'] = valid

        def check_request(self, **kwargs):
            check_request_values.update(kwargs)

        def set_response(
                self,
                discount,
                valid,
                discount_percent,
                discount_type='fixed',
                discount_limit='500',
        ):
            discount_body.update(
                {
                    'payload': {
                        'validationResult': {
                            'valid': valid,
                            'message': '1',
                            'promocode': {
                                'discount': (
                                    '0'
                                    if discount_type == 'fixed'
                                    else str(discount_percent)
                                ),
                                'discountType': discount_type,
                                'discountLimit': discount_limit,
                                'discountResult': str(discount),
                            },
                        },
                    },
                },
            )

    context = Context()
    return context


def discount_payload(discount):
    return {
        'payload': {
            'validationResult': {
                'valid': True,
                'message': '1',
                'promocode': {
                    'discount': '0',
                    'discountType': 'fixed',
                    'discountLimit': '500',
                    'discountResult': str(discount),
                },
            },
        },
    }
