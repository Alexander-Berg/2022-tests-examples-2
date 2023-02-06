import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.template import template_vars


DEFAULT_UNSUBSCRIBE_HOST = (
    'taxi.yandex.com/email/unsubscribe/?confirmation_code=dqaxqxqs13e'
)


@pytest.fixture(name='mock_functions')
def mock_url_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_receipt_url = Counter()

    counters = Counters()

    @patch('order_notify.repositories.receipt.get_receipt_url')
    async def _get_receipt_url(
            context: stq_context.Context, order_data: OrderData,
    ) -> typing.Optional[str]:
        counters.get_receipt_url.call()
        return 'receipt_url'

    return counters


@pytest.mark.parametrize(
    'logo_host, expected_logo_host',
    [
        pytest.param(None, 'taxi.yandex.com/?lang=ru', id='None_logo_host'),
        pytest.param('go.yandex', 'go.yandex', id='exist_logo_host'),
    ],
)
async def test_get_url_vars(
        stq3_context: stq_context.Context,
        mock_functions,
        logo_host,
        expected_logo_host,
):
    expected_vars = {
        'receipt_url': 'receipt_url',
        'logo_host': expected_logo_host,
        'unsubscribe_host': f'{DEFAULT_UNSUBSCRIBE_HOST}&lang=ru',
    }
    url_vars = await template_vars._get_url_vars(  # pylint: disable=W0212
        context=stq3_context,
        order_data=OrderData(brand='', country='', order={}, order_proc={}),
        taxi_host='taxi.yandex.com',
        logo_host=logo_host,
        locale='ru',
        confirmation_code='dqaxqxqs13e',
    )
    assert url_vars == expected_vars
