import datetime

import pytest

from taxi.util import dates as date_utils

from payments_eda.generated.stq3 import stq_context
from payments_eda.stq import close_order

DATE_TIME = datetime.datetime(2019, 6, 4, 3, 11, 22)


@pytest.mark.now(DATE_TIME.isoformat())
async def test_basic(stq3_context: stq_context.Context, mockserver):
    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def invoice_clear(request):
        assert request.json == {
            'id': 'my-order',
            'clear_eta': date_utils.localize(DATE_TIME).isoformat(),
        }
        return {}

    await close_order.task(stq3_context, 'my-order')
    assert invoice_clear.times_called == 1
