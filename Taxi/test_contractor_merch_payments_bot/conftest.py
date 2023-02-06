# pylint: disable=redefined-outer-name
import contractor_merch_payments_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'contractor_merch_payments_bot.generated.service.pytest_plugins',
    'test_contractor_merch_payments_bot.mocks.authorization',
    'test_contractor_merch_payments_bot.mocks.contractor_merch_payments',
    'test_contractor_merch_payments_bot.mocks.telegram',
]
