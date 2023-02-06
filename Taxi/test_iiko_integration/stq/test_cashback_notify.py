import pytest

from test_iiko_integration import transactions_stubs


@pytest.mark.parametrize(
    'invoice_id, expected_status',
    [
        pytest.param('invoice_01', 'processing_extra', id='processing_extra'),
        pytest.param('invoice_02', 'done', id='done'),
    ],
)
async def test_stq_cashback_notify(
        stq_runner,
        stq3_context,
        mockserver,
        mock_invoice_retrieve,
        load_json,
        invoice_id,
        expected_status,
):
    mock_invoice_retrieve(
        invoice_id=invoice_id,
        response_data=transactions_stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE,
    )

    @mockserver.json_handler(
        '/eda-billing/internal-api/v1/billing-storage/create',
    )
    def _billing_storage_create(request):
        assert (
            request.json
            == load_json('request_billing_storage_create.json')[invoice_id]
        )
        return {}

    await stq_runner.restaurant_order_cashback_notify.call(
        task_id=invoice_id, args=(invoice_id,),
    )

    order = await stq3_context.order_manager.get_order_by_invoice(
        invoice_id=invoice_id,
    )
    assert order.changelog[-1].status.value == expected_status
