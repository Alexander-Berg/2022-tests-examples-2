from typing import List

import pytest

from billing_bank_orders.generated.cron import run_cron


@pytest.mark.config(BILLING_BANK_ORDERS_READ_FRESH_BALANCES_ENABLED=True)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_balances_path, expected_docs_path, expected_updated_docs_path,'
    'docs_select_docs_path, existing_docs_path',
    [
        (
            'yt_balance.json',
            'balance_doc_and_new_cursor.json',
            'update_cursor.json',
            'empty_docs.json',
            None,
        ),
        (
            'yt_balance.json',
            'balance_doc_and_new_cursor.json',
            'update_cursor.json',
            'existing_balance_doc.json',
            'existing_balance_doc.json',
        ),
    ],
    ids=['create-balance-doc', 'do-not-update-existing-balance-doc'],
)
async def test_read_balances(
        mockserver,
        cron_runner,
        load_json,
        yt_balances_path,
        expected_docs_path,
        expected_updated_docs_path,
        docs_select_docs_path,
        existing_docs_path,
        patch,
):
    yt_table_data = load_json(yt_balances_path)
    expected_created_docs = load_json(expected_docs_path)
    expected_updated_docs = load_json(expected_updated_docs_path)
    docs_select_docs = load_json(docs_select_docs_path)
    if existing_docs_path is None:
        existing_docs = []
    else:
        existing_docs = load_json(existing_docs_path)
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
        response = {}
        if existing_docs:
            obj_id = request.json['external_obj_id']
            ref = request.json['external_event_ref']
            for doc in existing_docs:
                if (
                        doc['external_obj_id'] == obj_id
                        and doc['external_event_ref'] == ref
                ):
                    response = doc
        if not response:
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
        assert request.json['limit'] == 1
        docs = []
        for doc in docs_select_docs:
            if doc['external_obj_id'] == request.json['external_obj_id']:
                docs.append(doc)
                break
        response = {'docs': docs, 'cursor': '', 'limit': 1}
        return mockserver.make_response(json=response)

    @mockserver.json_handler(
        '/parks-replica/v1/parks/by_billing_client_id/retrieve_bulk',
    )
    def get_v1_parks_billing_client_id(request):
        return mockserver.make_response(
            json={
                'parks': [
                    {
                        'park_id': billing_client_id,
                        'billing_client_id': billing_client_id,
                    }
                    for billing_client_id in request.json['billing_client_ids']
                ],
            },
        )

    await run_cron.main(
        ['billing_bank_orders.crontasks.read_fresh_balances', '-t', '0'],
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
