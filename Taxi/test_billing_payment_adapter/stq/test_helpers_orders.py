from aiohttp import web
import pytest

from generated import models
from taxi.util import dates

from billing_payment_adapter.stq import helpers


@pytest.mark.config(
    BILLING_PAYMENT_ADAPTER_ORDERS_SENDING_SETTINGS={
        'bulk_limit': 4,
        'delay_ms': 1,
    },
)
async def test_orders_partitioning(stq3_context, mock_billing_orders):
    @mock_billing_orders('/v2/process/async')
    def _process_async(request):
        return web.json_response(
            {'orders': [{'doc_id': 0, 'external_ref': '', 'topic': ''}]},
        )

    orders = [_make_empty_event() for _ in range(10)]
    await helpers.orders.send_payout_orders_in_chunks(stq3_context, orders)
    assert _process_async.times_called == 3
    assert len(_process_async.next_call()['request'].json['orders']) == 4
    assert len(_process_async.next_call()['request'].json['orders']) == 4
    assert len(_process_async.next_call()['request'].json['orders']) == 2


def _make_empty_event():
    return models.billing_orders.InvoiceTransactionCleared(
        data=models.billing_orders.InvoiceTransactionClearedDataV1(
            entries=[],
            event_version=1,
            payments=[],
            schema_version='v1',
            topic_begin_at=dates.utcnow(),
        ),
        event_at=dates.utcnow(),
        external_ref='external_ref',
        kind='invoice_transaction_cleared',
        topic='topic',
    )
