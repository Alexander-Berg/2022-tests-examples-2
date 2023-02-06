from typing import List

import pytest

from billing_bank_orders.generated.cron import run_cron


@pytest.mark.config(
    BILLING_BANK_ORDERS_READ_FRESH_PAYMENT_REQUESTS_ENABLED=True,
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_requests_path, expected_docs_path, expected_updated_docs_path,'
    'docs_select_docs_path',
    [
        (
            'yt_requests.json',
            'new_cursor.json',
            'update_cursor_and_children.json',
            '200_300_400_children_requests.json',
        ),
        (
            'yt_requests.json',
            'new_cursor.json',
            'update_cursor_and_children_and_finish_parent.json',
            '200_300_children_requests.json',
        ),
    ],
    ids=['update-children-requests', 'finish-parent-request'],
)
async def test_read_fresh_payment_requests(
        mockserver,
        cron_runner,
        load_json,
        yt_requests_path,
        expected_docs_path,
        expected_updated_docs_path,
        docs_select_docs_path,
        patch,
):
    yt_table_data = load_json(yt_requests_path)
    expected_created_docs = load_json(expected_docs_path)
    expected_updated_docs = load_json(expected_updated_docs_path)
    docs_select_docs = load_json(docs_select_docs_path)

    created_docs = []
    updated_docs = []
    finished_docs = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        class MockedTable:
            def fetch_full_data(self):
                pass

            @property
            def rows(self):
                return [['2020-01-30', '2020-01-31']]

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
        return ['2020-01-29', '2020-01-30']

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
            'event_at': '2020-01-16T03:43:31.000000+00:00',
            'external_event_ref': '69118711',
            'external_obj_id': '69118712',
            'journal_entries': [],
            'kind': 'billing_bank_orders_payment',
            'service': 'billing-bank-orders',
            'status': 'new',
            'created': '2020-01-16T03:43:31.000000+00:00',
            'tags': [],
            'process_at': '2020-01-16T03:43:31.000000+00:00',
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

    @mockserver.json_handler('/billing-docs/v1/docs/finish_processing')
    async def _docs_finish(request):
        finished_docs.append(request.json['doc_id'])
        response = {'finished': True, 'status': 'complete'}
        return mockserver.make_response(json=response)

    await run_cron.main(
        [
            'billing_bank_orders.crontasks.read_fresh_payment_requests',
            '-t',
            '0',
        ],
    )
    _cmp_docs(created_docs, expected_created_docs)
    _cmp_docs(updated_docs, expected_updated_docs, key_fields=['doc_id'])


@pytest.mark.config(
    BILLING_BANK_ORDERS_READ_FRESH_PAYMENT_REQUESTS_ENABLED=True,
    BILLING_BANK_ORDERS_READ_FRESH_PAYMENT_REQUESTS_SETTINGS={
        'payment_requests_path': 'features/oebs/pmt_export/pmt_requests/',
        'yt_clusters': ['hahn'],
        'requests_load_chunk_size': 10000,
        'update_cursor_chunk_size': 2500,
        'save_requests_docs_chunk_size': 50,
        'cursor_max_updates': 200,
        'max_fails_count': 10,
    },
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_requests_path, expected_docs_path, expected_updated_docs_path,'
    'docs_select_docs_path',
    [
        (
            'yt_request_with_invalid_status.json',
            'failed_payment_request.json',
            'empty_docs.json',
            'empty_docs.json',
        ),
    ],
    ids=['save-failed-payment'],
)
async def test_read_failed_payment_requests(
        mockserver,
        cron_runner,
        load_json,
        yt_requests_path,
        expected_docs_path,
        expected_updated_docs_path,
        docs_select_docs_path,
        patch,
):
    yt_table_data = load_json(yt_requests_path)
    expected_created_docs = load_json(expected_docs_path)
    expected_updated_docs = load_json(expected_updated_docs_path)
    docs_select_docs = load_json(docs_select_docs_path)

    created_docs = []
    updated_docs = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        class MockedTable:
            def fetch_full_data(self):
                pass

            @property
            def rows(self):
                return [['2020-01-30', '2020-01-31']]

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
        return ['2020-01-29', '2020-01-30']

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
            'event_at': '2020-01-16T03:43:31.000000+00:00',
            'external_event_ref': '69118711',
            'external_obj_id': '69118712',
            'journal_entries': [],
            'kind': 'billing_bank_orders_payment',
            'service': 'billing-bank-orders',
            'status': 'new',
            'created': '2020-01-16T03:43:31.000000+00:00',
            'tags': [],
            'process_at': '2020-01-16T03:43:31.000000+00:00',
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

    await run_cron.main(
        [
            'billing_bank_orders.crontasks.read_fresh_payment_requests',
            '-t',
            '0',
        ],
    )
    _cmp_docs(created_docs, expected_created_docs)
    _cmp_docs(updated_docs, expected_updated_docs, key_fields=['doc_id'])


def _cmp_docs(actual, expected, key_fields=None):
    if key_fields is None:
        key_fields = ['external_obj_id', 'external_event_ref']

    def _key(doc):
        return tuple(doc[key] for key in key_fields)

    actual_dict = {_key(doc): doc for doc in actual}
    expected_dict = {_key(doc): doc for doc in expected}
    assert actual_dict == expected_dict
