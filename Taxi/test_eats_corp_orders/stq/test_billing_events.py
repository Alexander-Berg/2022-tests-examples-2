import pytest

from eats_corp_orders.stq import billing_events


@pytest.mark.config(EATS_CORP_ORDERS_BILLING_EVENTS_SETTINGS={'enabled': True})
async def test_success(stq3_context, order_id, mock_eda_billing_storage):
    @mock_eda_billing_storage('/internal-api/v1/billing-storage/create')
    async def handler(request):
        return {}

    await billing_events.task(stq3_context, order_id)

    assert handler.has_calls


async def test_not_sent_if_disabled(
        stq3_context, order_id, mock_eda_billing_storage,
):
    await billing_events.task(stq3_context, order_id)
