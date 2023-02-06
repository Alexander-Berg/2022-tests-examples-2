import pytest

from taxi.stq import async_worker_ng

from billing_bank_orders.stq import process_logbroker_transfer_orders


@pytest.mark.parametrize(
    'data_path',
    [
        'remittance_order_confirm_full.json',
        'remittance_order_confirm_part.json',
        'transfer_order_confirm_full.json',
        'transfer_order_confirm_part.json',
    ],
)
@pytest.mark.now('2021-08-01T12:34:00.000000+03:00')
async def test_contractor_balance_update(
        data_path, load_json, stq3_context, mockserver, monkeypatch,
):
    billing_docs_requests = []
    billing_orders_requests = []
    billing_reports_requests = []

    data = load_json(data_path)

    @mockserver.json_handler('/billing-docs/v1/docs/update')
    async def _docs_update(request):
        billing_docs_requests.append(request.json)
        response = data['billing_docs_response']
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-reports/v1/docs/by_id')
    async def _docs_by_id(request):
        billing_reports_requests.append(request.json)
        response = {'docs': []}
        for doc in data['billing_reports_docs']:
            if doc['doc_id'] in request.json['doc_ids']:
                response = {'docs': [doc]}
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-orders/v2/process/async')
    async def _process_async(request):
        billing_orders_requests.append(request.json)
        # Response doesn't matter, we only need it for validation
        response = {
            'orders': [
                {
                    'topic': 'taxi/topic',
                    'external_ref': '1',
                    'doc_id': 6196620153,
                },
            ],
        }
        return mockserver.make_response(json=response)

    task_meta_info = async_worker_ng.TaskInfo(
        id=751,
        exec_tries=0,
        reschedule_counter=0,
        queue='billing_bank_orders_process_logbroker_transfer_orders',
    )
    stq_params = data['stq_params']
    await process_logbroker_transfer_orders.task(
        stq3_context, **stq_params, task_meta_info=task_meta_info,
    )

    # Check requests in billing-orders
    assert billing_docs_requests == data['billing_docs_requests']
    assert billing_orders_requests == data['billing_orders_requests']
    assert billing_reports_requests == data['billing_reports_requests']
