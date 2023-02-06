# pylint: disable=import-error
from grocery_mocks.utils.handle_context import HandleContext
import pytest

from .. import consts
from .. import helpers

DEFAULT_DEBT = dict(
    id=consts.DEBT_ID,
    metadata={},
    service=consts.SERVICE,
    debtors=[],
    version=1,
    invoice=consts.INVOICE_INFO,
    collection=dict(
        strategy=consts.DEBT_NULL_STRATEGY, installed_at=consts.NOW,
    ),
    transactions_params={},
    reason=helpers.make_reason(),
    currency=consts.CURRENCY,
    items_by_payment_type=dict(debt=[], total=[]),
    created_at=consts.NOW,
    updated_at=consts.NOW,
)


@pytest.fixture(name='debt_collector', autouse=True)
def mock_debt_collector(mockserver):
    class Context:
        def __init__(self):
            self.create = HandleContext()
            self.update = HandleContext()
            self.pay = HandleContext()
            self.by_id = HandleContext()
            self.list = HandleContext()

            self.by_id.response = {}
            self.list.response = {}

    context = Context()

    def _make_error_response(handler: HandleContext):
        error_code = handler.status_code
        body = handler.response_with(
            {'code': str(error_code), 'message': f'{error_code} error'},
        )
        return mockserver.make_response(json=body, status=error_code)

    @mockserver.json_handler('/debt-collector/v1/debt/create')
    def _mock_create(request):
        handler = context.create
        handler.process(request.json['debt'])

        if not handler.is_ok:
            return _make_error_response(handler)
        return handler.response or {}

    @mockserver.json_handler('/debt-collector/v1/debt/update')
    def _mock_update(request):
        handler = context.update
        handler.process(request.json['debt'])

        if not handler.is_ok:
            return _make_error_response(handler)
        return handler.response or {}

    @mockserver.json_handler('/debt-collector/v1/debt/pay')
    def _mock_pay(request):
        handler = context.pay
        handler.process(request.json['debt'])

        if not handler.is_ok:
            return _make_error_response(handler)
        return handler.response or {}

    @mockserver.json_handler('/debt-collector/v1/debts/by_id')
    def _mock_by_id(request):
        handler = context.by_id
        handler(request)

        debts = []
        if handler.response is not None:
            debts.append(handler.response_with(DEFAULT_DEBT))

        return dict(debts=debts)

    @mockserver.json_handler('/debt-collector/v1/debts/list')
    def _mock_list(request):
        handler = context.list
        handler(request)

        debts = []
        if handler.response is not None:
            debts.append(handler.response_with(DEFAULT_DEBT))

        return dict(debts=debts)

    return context
