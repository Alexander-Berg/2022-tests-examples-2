import pytest

# pylint: disable=import-only-modules
from grocery_mocks.utils.handle_context import HandleContext


DEFAULT_CARD = {
    'billing_card_id': 'xb10sss57c12aaabe8345ac74',
    'bound': False,
    'busy': False,
    'busy_with': [],
    'card_id': 'card-xb10sss57c12aaabe8345ac74',
    'currency': 'RUB',
    'expiration_month': 2,
    'expiration_year': 22,
    'from_db': True,
    'number': '123456****1234',
    'owner': 'not used',
    'permanent_card_id': 'card-xb10sss57c12aaabe8345ac74',
    'possible_moneyless': False,
    'region_id': 'not used',
    'regions_checked': [],
    'system': 'VISA',
    'unverified': False,
    'valid': True,
}


class PaymentVerificationsContext(HandleContext):
    def __init__(self):
        HandleContext.__init__(self)
        self.retry_after = None

    def mock_error(self, status_code, retry_after):
        self.status_code = status_code
        self.retry_after = retry_after


@pytest.fixture(name='cardstorage', autouse=True)
def mock_cardstorage(mockserver):
    class Context:
        def __init__(self):
            self.card = HandleContext()
            self.payment_verifications = PaymentVerificationsContext()

    context = Context()

    @mockserver.json_handler('cardstorage/v1/card')
    def _mock_card(request):
        handler = context.card
        handler(request)

        if not handler.is_ok:
            return mockserver.make_response(
                status=handler.status_code, json={},
            )

        return handler.response_with(DEFAULT_CARD)

    @mockserver.json_handler('cardstorage/v1/payment_verifications')
    def _mock_payment_verifications(request):
        handler = context.payment_verifications

        handler.process(
            request_body=request.json, request_headers=request.headers,
        )

        if not handler.is_ok:
            headers = None

            if handler.retry_after is not None:
                headers = {'Retry-After': handler.retry_after}

            return mockserver.make_response(
                json={'error': {'text': 'error'}},
                status=handler.status_code,
                headers=headers,
            )

        return handler.response

    return context
