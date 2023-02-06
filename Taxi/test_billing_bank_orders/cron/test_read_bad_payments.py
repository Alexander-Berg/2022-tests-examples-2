from typing import List

import pytest

from billing_bank_orders.generated.cron import run_cron


@pytest.mark.config(BILLING_BANK_ORDERS_READ_BAD_PAYMENTS_ENABLED=True)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_payments_path, expected_docs_path, expected_updated_docs_path,'
    'existing_docs_path',
    [
        (
            'payment_history.json',
            'payment_doc.json',
            'finish_bad_doc.json',
            'existing_bad_payment.json',
        ),
        (
            'payment_history_wo_billing_client_id.json',
            'empty_docs.json',
            'empty_docs.json',
            'existing_bad_payment.json',
        ),
    ],
    ids=['reupload-and-finish-bad-payment', 'do-nothing-if-payment-still-bad'],
)
async def test_read_bad_payments(
        mockserver,
        cron_runner,
        load_json,
        yt_payments_path,
        expected_docs_path,
        expected_updated_docs_path,
        existing_docs_path,
        patch,
):
    yt_table_data = load_json(yt_payments_path)
    expected_created_docs = load_json(expected_docs_path)
    expected_updated_docs = load_json(expected_updated_docs_path)
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
        assert request.json['external_obj_id'] in (
            'v1/billing_bank_orders_failed_payments',
        )
        docs = []
        if existing_docs and not request.json.get('cursor'):
            obj_id = request.json['external_obj_id']
            for doc in existing_docs:
                if doc['external_obj_id'] == obj_id:
                    docs.append(doc)
        response = {
            'docs': docs,
            'cursor': 'some_cursor',
            'limit': request.json['limit'],
        }
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _reports_docs_select(request):
        result = []
        if existing_docs:
            obj_id = request.json['external_obj_id']
            ref = request.json['external_event_ref']
            for doc in existing_docs:
                if (
                        doc['external_obj_id'] == obj_id
                        and doc['external_event_ref'] == ref
                ):
                    result.append(doc)
        return mockserver.make_response(json={'docs': result, 'cursor': {}})

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
        ['billing_bank_orders.crontasks.read_bad_payments', '-t', '0'],
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
