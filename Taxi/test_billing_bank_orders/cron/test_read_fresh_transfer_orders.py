from typing import List

import pytest

from billing_bank_orders.generated.cron import run_cron


@pytest.mark.config(
    BILLING_BANK_ORDERS_READ_FRESH_TRANSFER_ORDERS_ENABLED=True,
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_requests_path, expected_docs_path, expected_updated_docs_path,'
    'docs_select_docs_path,expected_orders_events_path',
    [
        (
            'yt_requests_confirm.json',
            'new_cursor.json',
            'updated_confirm_documents.json',
            'existing_documents.json',
            'orders_confirm_documents.json',
        ),
        (
            'yt_requests_confirm_cancel.json',
            'new_cursor.json',
            'updated_cancel_confirm_documents.json',
            'existing_documents.json',
            'orders_cancel_confirm_documents.json',
        ),
        (
            'yt_requests_confirm_cancel_and_delta.json',
            'new_cursor.json',
            'updated_cancel_confirm_with_delta_documents.json',
            'existing_documents.json',
            'orders_cancel_and_delta_confirm_documents.json',
        ),
        (
            'yt_requests_reject.json',
            'new_cursor.json',
            'updated_reject_documents.json',
            'existing_documents.json',
            'orders_reject_documents.json',
        ),
        (
            'yt_requests_confirm_remittance_order.json',
            'new_cursor.json',
            'updated_remittance_order_documents.json',
            'existing_documents.json',
            'orders_confirm_remittance_order.json',
        ),
    ],
    ids=[
        'payment confirm event',
        'payment cancel confirm event',
        'payment cancel confirm event with delta confirm',
        'payment reject event',
        'remittance_order confirm event',
    ],
)
async def test_read_fresh_transfer_orders(
        mockserver,
        cron_runner,
        load_json,
        yt_requests_path,
        expected_docs_path,
        expected_updated_docs_path,
        docs_select_docs_path,
        expected_orders_events_path,
        patch,
):
    yt_table_data = load_json(yt_requests_path)
    expected_created_docs = load_json(expected_docs_path)
    expected_updated_docs = load_json(expected_updated_docs_path)
    docs_select_docs = load_json(docs_select_docs_path)
    expected_orders_docs = load_json(expected_orders_events_path)

    created_docs = []
    updated_docs = []
    finished_docs = []
    orders_docs = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        class MockedTable:
            def fetch_full_data(self):
                pass

            @property
            def rows(self):
                return [['2020-07-01', '2020-07-02']]

        class MockedResult:
            @property
            def status(self) -> str:
                return 'COMPLETED'

            @property
            def is_success(self) -> bool:
                return True

            @property
            def errors(self) -> List[Exception]:
                return []

            def run(self):
                pass

            def get_results(self, *args, **kwargs):
                return self

            @property
            def share_url(self):
                return ''

            def __iter__(self):
                yield MockedTable()

        del query_str  # unused
        del kwargs  # unused
        return MockedResult()

    @patch(
        'billing_bank_orders.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'read_table',
    )
    async def read_table(table_path):
        start = table_path.ranges[0]['lower_limit']['row_index']
        end = table_path.ranges[0]['upper_limit']['row_index']
        return yt_table_data[start:end]

    @patch(
        'billing_bank_orders.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'row_count',
    )
    async def row_count(*args, **kwargs):
        return len(yt_table_data)

    @patch(
        'billing_bank_orders.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'list',
    )
    async def yt_list(*args, **kwargs):
        return ['2020-07-01', '2020-07-02']

    @mockserver.json_handler('/billing-docs/v1/docs/create')
    async def _docs_create(request):
        created_docs.append(request.json)
        response = {
            'doc_id': 1,
            'created': '2020-01-23T00:00:00+00:03',
            'process_at': '2020-01-23T00:00:00+00:03',
            'tags': [],
            **request.json,
        }
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-docs/v1/docs/update')
    async def _docs_update(request):
        updated_docs.append(request.json)
        # Response doesn't matter, we only need it for validation
        response = {
            'doc_id': 1,
            'data': {},
            'event_at': '2020-07-01T03:43:31.000000+00:00',
            'external_event_ref': '69118711',
            'external_obj_id': '69118712',
            'journal_entries': [],
            'kind': 'transfer_order',
            'service': 'billing-bank-orders',
            'status': 'new',
            'created': '2020-07-01T03:43:31.000000+00:00',
            'tags': [],
            'process_at': '2020-07-01T03:43:31.000000+00:00',
        }
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-docs/v1/docs/select')
    async def _docs_select(request):
        docs = []
        for doc in docs_select_docs:
            if doc['external_obj_id'] == request.json['external_obj_id']:
                docs.append(doc)
                break
        response = {'docs': docs, 'cursor': '', 'limit': request.json['limit']}
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-docs/v1/docs/search')
    async def _docs_search(request):
        key = 'external_obj_id'
        docs = []
        for doc in docs_select_docs:
            if doc[key] == request.json[key]:
                docs.append(doc)
        response = {'docs': docs}
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-reports/v1/docs/by_id')
    async def _docs_by_id(request):
        docs = []
        for doc in docs_select_docs:
            if doc['doc_id'] in request.json['doc_ids']:
                entry = {}
                for key, val in doc.items():
                    new_key = key
                    if key == 'external_obj_id':
                        new_key = 'topic'
                    elif key == 'external_event_ref':
                        new_key = 'external_ref'
                    entry[new_key] = val
                docs.append(entry)
        response = {'docs': docs}
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-orders/v2/process/async')
    async def _process_async(request):
        orders_docs.append(request.json)
        # Response doesn't matter, we only need it for validation
        response = {
            'orders': [
                {
                    'topic': (
                        'taxi/periodic_payment_confirm/clid/40321877546/5677'
                    ),
                    'external_ref': '102',
                    'doc_id': 6196620153,
                },
            ],
        }
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-docs/v1/docs/finish_processing')
    async def _docs_finish(request):
        finished_docs.append(request.json['doc_id'])
        response = {'finished': True, 'status': 'complete'}
        return mockserver.make_response(json=response)

    await run_cron.main(
        [
            'billing_bank_orders.crontasks.read_fresh_transfer_orders',
            '-t',
            '0',
        ],
    )

    _cmp_docs(created_docs, expected_created_docs)
    updated_docs = sorted(updated_docs, key=lambda x: x['idempotency_key'])
    assert updated_docs == expected_updated_docs
    orders_docs = sorted(
        orders_docs, key=lambda x: x['orders'][0]['external_ref'],
    )
    assert orders_docs == expected_orders_docs


def _cmp_docs(actual, expected, key_fields=None):
    if key_fields is None:
        key_fields = ['external_obj_id', 'external_event_ref']

    def _key(doc):
        return tuple(doc[key] for key in key_fields)

    actual_dict = {_key(doc): doc for doc in actual}
    expected_dict = {_key(doc): doc for doc in expected}
    assert actual_dict == expected_dict
