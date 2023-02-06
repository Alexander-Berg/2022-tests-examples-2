# pylint: disable=import-error
import typing

from grocery_mocks.utils.handle_context import HandleContext
import pytest

from tests_grocery_payments import models

BANKS = [models.SbpBankInfo(bank_name=f'bank_name:{i}') for i in range(5)]


@pytest.fixture(name='grocery_payments_methods', autouse=True)
def mock_grocery_payments_methods(mockserver):
    class Context:
        def __init__(self):
            self.sbp_banks_info = HandleContext()
            self.banks = None

        def set_sbp_banks(self, banks: typing.List[models.SbpBankInfo]):
            self.banks = banks

    context = Context()

    @mockserver.json_handler(
        '/grocery-payments-methods/'
        'internal/payments-methods/v1/sbp-banks-info',
    )
    def _sbp_banks_info(request):
        context.sbp_banks_info(request)

        context_banks = context.banks or BANKS

        banks = [bank.to_raw_response() for bank in context_banks]
        return {'sbp_banks_info': banks}

    return context
