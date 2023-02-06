import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.email import message
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.template.template_info import TemplateData
from test_order_notify.conftest import DEFAULT_TEMPLATE_DATA


@pytest.fixture(name='mock_functions')
def mock_get_template_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_template_data = Counter()
            self.get_template_vars = Counter()
            self.send = Counter()

    counters = Counters()

    @patch(
        'order_notify.repositories.template.template_info.'
        'get_template_data',
    )
    async def _get_template_data(
            context: stq_context.Context,
            brand: str,
            country: str,
            locale: str,
    ) -> TemplateData:
        counters.get_template_data.call()
        return DEFAULT_TEMPLATE_DATA

    @patch(
        'order_notify.repositories.template.template_vars.'
        'get_template_vars',
    )
    async def _get_template_vars(
            context: stq_context.Context,
            order_data: OrderData,
            template_data: TemplateData,
            locale: str,
            confirmation_code: typing.Optional[str],
            is_corp_report: bool,
    ) -> dict:
        counters.get_template_vars.call()
        return {'template': 'data'}

    return counters


async def test_construct_message(
        stq3_context: stq_context.Context, mock_functions,
):
    report = await message._construct_message(  # pylint: disable=W0212
        context=stq3_context,
        email='vbifaa@yandex-team.ru',
        order_data=OrderData(
            brand='', country='', order={'nz': 'moscow'}, order_proc={},
        ),
        locale='ru',
    )
    assert report.campaign_slug == 'camplslug'
    assert report.from_name == 'sn'
    assert report.from_email == 'sm@yandex-team.ru'
    assert report.to_email == 'vbifaa@yandex-team.ru'
    assert report.template_vars == {'template': 'data'}

    assert mock_functions.get_template_data.times_called == 1
    assert mock_functions.get_template_vars.times_called == 1
