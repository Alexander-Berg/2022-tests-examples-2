import pytest

PROMO_CAN_BE_VALID = {'error_code': 'ERROR_INVALID_CITY', 'valid': False}
PROMO_ERROR_INVALID_CODE = {'error_code': 'ERROR_NOT_FOUND', 'valid': False}
PROMO_ERROR_ALREADY_USED = {'error_code': 'ERROR_USED', 'valid': False}
PROMO_ERROR_NO_PAYMENT_METHOD = {
    'error_code': 'ERROR_CREDITCARD_REQUIRED',
    'valid': False,
}
PROMO_ERROR_INVALID_CITY = {'error_code': 'ERROR_INVALID_CITY', 'valid': False}

ERROR_500 = {'code': '500', 'message': 'Internal Server Error'}
ERROR_400 = {'code': '400', 'message': 'Bad request'}
ERROR_429 = {'code': '429', 'message': 'Too Many Requests'}


def _get_promocode_desc(promocode_type, value, purpose):
    return {
        'valid': True,
        'promocode_info': {
            'currency_code': 'RUB',
            'format_currency': True,
            'value': value,
            'type': promocode_type,
            'series_purpose': purpose,
        },
    }


@pytest.fixture(name='grocery_coupons')
def mock_grocery_coupons(mockserver):
    state = {'check_status_code': 200, 'check_response_body': {}}

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/check')
    def check_promocode(request):
        body = request.json

        assert 'promocode' in body
        assert 'depot_id' in body
        assert 'cart_id' in body
        assert 'cart_version' in body
        assert 'cart_cost' in body
        assert 'cart_items' in body

        if 'check_check_request' in state:
            for key, value in state['check_check_request'].items():
                assert body[key] == value, key

        return mockserver.make_response(
            status=state['check_status_code'],
            json=state['check_response_body'],
        )

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/list')
    def coupons_list(request):
        body = request.json

        assert 'depot_id' in body

        if 'check_list_request' in state:
            for key, value in state['check_list_request'].items():
                assert body.get(key) == value

        return mockserver.make_response(
            status=state['list_status_code'], json=state['list_response_body'],
        )

    class Context:
        def check_times_called(self):
            return check_promocode.times_called

        def list_times_called(self):
            return coupons_list.times_called

        def check_check_request(self, **kwargs):
            state['check_check_request'] = kwargs

        def check_list_request(self, **kwargs):
            state['check_list_request'] = kwargs

        def set_check_response(self, status_code=200, response_body=None):
            state['check_status_code'] = status_code
            if not response_body:
                state['check_response_body'] = {}
            else:
                state['check_response_body'] = response_body

        def set_check_response_custom(
                self,
                value,
                promocode_type='percent',
                purpose='support',
                status_code=200,
        ):
            state['check_status_code'] = status_code
            state['check_response_body'] = _get_promocode_desc(
                promocode_type, value, purpose,
            )

        def set_list_response(self, status_code=200, response_body=None):
            state['list_status_code'] = status_code
            if not response_body:
                state['list_response_body'] = {}
            else:
                state['list_response_body'] = response_body

    context = Context()
    return context
