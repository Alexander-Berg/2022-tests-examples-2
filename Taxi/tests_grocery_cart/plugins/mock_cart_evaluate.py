# pylint: disable=invalid-name
import json

import pytest

WALLET_ID = 'w/28c44321-16a3-5221-a0b1-3f823998bdff'


@pytest.fixture(name='cart_evaluate', autouse=True)
def mock_basic_cart_evaluate(mockserver):
    cashback_info_response = {}

    @mockserver.json_handler('/grocery-p13n/internal/v1/p13n/v1/cashback-info')
    def mock_cashback_info(request):
        if context.is_cashback_disabled or not cashback_info_response:
            return mockserver.make_response(
                json.dumps({'code': 'DISABLED_BY_EXPERIMENT', 'message': ''}),
                404,
            )
        return {
            'wallet_id': WALLET_ID,
            'complement_payment_types': ['card', 'applepay'],
            **cashback_info_response,
        }

    class Context:
        def __init__(self):
            self.is_cashback_disabled = False

        def times_called_info(self):
            return mock_cashback_info.times_called

        def set_cashback_info_response(
                self, payment_available, balance, availability_type='buy_plus',
        ):
            cashback_info_response['balance'] = str(balance)
            if not payment_available:
                cashback_info_response['unavailability'] = {
                    'charge_disabled_code': availability_type,
                }

        def remove_cashback_info(self):
            context.is_cashback_disabled = True

    context = Context()
    return context
