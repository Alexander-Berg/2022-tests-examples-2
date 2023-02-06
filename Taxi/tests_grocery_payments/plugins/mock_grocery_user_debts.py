# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest

from .. import consts

DEBT = {
    'debt_id': consts.ORDER_ID,
    'created': consts.NOW,
    'items': [],
    'version': 1,
}


@pytest.fixture(name='grocery_user_debts', autouse=True)
def mock_grocery_user_debts(mockserver):
    class Context:
        def __init__(self):
            self.request = HandleContext()
            self.retrieve = HandleContext()
            self.set_pay_strategy = HandleContext()
            self.init = HandleContext()
            self.create = HandleContext()
            self.update = HandleContext()
            self.cancel = HandleContext()
            self.clear = HandleContext()
            self.set_status = HandleContext()
            self.append_prediction = HandleContext()

            self.reason_to_context = {
                'init': self.init,
                'create': self.create,
                'update': self.update,
                'cancel': self.cancel,
                'clear': self.clear,
                'set-status': self.set_status,
                'append-prediction': self.append_prediction,
            }

            self.debt_available = False

    context = Context()

    @mockserver.json_handler('/grocery-user-debts/internal/debts/v1/request')
    def _mock_request(request):
        handler = context.request
        handler(request)

        return {'debt_available': context.debt_available}

    @mockserver.json_handler('/grocery-user-debts/internal/debts/v1/retrieve')
    def _mock_retrieve(request):
        handler = context.retrieve
        handler(request)

        if handler.response is None:
            return mockserver.make_response(status=404, json={})

        return handler.response_with(DEBT)

    @mockserver.json_handler(
        '/grocery-user-debts/internal/debts/v1/set-pay-strategy',
    )
    def _mock_set_pay_strategy(request):
        handler = context.set_pay_strategy
        handler(request)

        return {}

    @mockserver.json_handler('/processing/v1/grocery/debts_v2/create-event')
    def _mock_processing(request):
        handler = context.reason_to_context[request.json['reason']]
        handler(request)

        return {'event_id': 'event_id'}

    return context
