from typing import List

import pytest

from billing_bank_orders.generated.cron import run_cron


@pytest.mark.config(BILLING_BANK_ORDERS_READ_FRESH_PAYMENTS_ENABLED=True)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_payments_path, expected_docs_path, expected_updated_docs_path,'
    'cursor_docs_path, existing_docs_path, yt_tables_list',
    [
        (
            'payment_history.json',
            'all_payment_docs_and_new_cursor.json',
            'empty_docs.json',
            'empty_docs.json',
            None,
            None,
        ),
        (
            'payment_history.json',
            'all_payment_docs.json',
            'update_history_id.json',
            'cursor_in_past.json',
            None,
            None,
        ),
        (
            'empty_docs.json',
            'empty_docs.json',
            'update_last_date.json',
            'cursor_in_past.json',
            None,
            None,
        ),
        (
            'payment_with_changed_status.json',
            'empty_docs.json',
            'update_history_id_and_payment_status.json',
            'cursor_in_past.json',
            'existing_payment_doc.json',
            None,
        ),
        (
            'empty_docs.json',
            'new_cursor_doc.json',
            'finish_cursor.json',
            'cursor_with_max_updates.json',
            None,
            None,
        ),
        (
            'empty_docs.json',
            'empty_docs.json',
            'empty_docs.json',
            'cursor_in_past.json',
            None,
            ['2020-01-29'],
        ),
        (
            'payment_with_same_status.json',
            'empty_docs.json',
            'update_history_id.json',
            'cursor_in_past.json',
            'existing_payment_doc.json',
            None,
        ),
        (
            'old_payment_data.json',
            'empty_docs.json',
            'update_history_id_old.json',
            'cursor_in_past.json',
            'existing_payment_doc.json',
            None,
        ),
        (
            'payment_with_same_status.json',
            'empty_docs.json',
            'update_history_id.json',
            'cursor_in_past.json',
            'existing_complete_payment_doc.json',
            None,
        ),
        (
            'payment_with_reconciled_status.json',
            'empty_docs.json',
            'update_history_id.json',
            'cursor_in_past.json',
            'existing_returned_payment_doc.json',
            None,
        ),
        (
            'payment_with_returned_status.json',
            'payment_with_returned_status_doc.json',
            'update_history_id_and_main_doc_status.json',
            'cursor_in_past.json',
            'existing_created_payment_doc.json',
            None,
        ),
        (
            'payment_with_zero_amount_confirmed.json',
            'payment_with_zero_amount_confirmed_complete_doc.json',
            'update_history_id.json',
            'cursor_in_past.json',
            None,
            None,
        ),
        (
            'payment_with_zero_amount_reconciled.json',
            'empty_docs.json',
            'update_history_id.json',
            'cursor_in_past.json',
            'existing_confirmed_payment_with_zero_amount_complete_doc.json',
            None,
        ),
        (
            'payment_with_zero_amount_confirmed.json',
            'empty_docs.json',
            'update_history_id_and_payment.json',
            'cursor_in_past.json',
            'existing_created_payment_with_zero_amount_new_doc.json',
            None,
        ),
    ],
    ids=[
        'create-payment-docs-and-cursor',
        'update-cursor-history-id',
        'update-cursor-last-date',
        'update-payment-status',
        'maxed-cursor-switches-to-new-doc',
        'do-not-update-last-date-if-last-table',
        'do-not-update-payment-if-status-remains-the-same',
        'do-not-update-payment-if-history-id-lower',
        'do-not-update-complete-payment-if-new-non-terminal-status',
        'do-not-update-returned-payment-if-new-status-is-reconciled',
        'finish-main-doc-if-returned',
        'create-complete-doc-if-zero-amount',
        'do-not-update-complete-doc-if-zero-amount',
        'update-new-doc-if-zero-amount',
    ],
)
async def test_read_payments(
        mockserver,
        cron_runner,
        load_json,
        yt_payments_path,
        expected_docs_path,
        expected_updated_docs_path,
        cursor_docs_path,
        existing_docs_path,
        yt_tables_list,
        patch,
):
    yt_table_data = load_json(yt_payments_path)
    expected_created_docs = load_json(expected_docs_path)
    expected_updated_docs = load_json(expected_updated_docs_path)
    cursor_docs = load_json(cursor_docs_path)
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
        if yt_tables_list is not None:
            return yt_tables_list
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
        assert request.json['external_obj_id'] in (
            'taxi_billing_bank_orders_read_fresh_payments_counting_cursor',
            'v1/billing_bank_orders_failed_payments',
        )
        if 'cursor' in request.json['external_obj_id']:
            assert request.json['limit'] == 1
            response = {'docs': cursor_docs, 'cursor': '', 'limit': 1}
        else:
            response = {
                'docs': [],
                'cursor': '',
                'STATUSES': [],
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
        ['billing_bank_orders.crontasks.read_fresh_payments', '-t', '0'],
    )
    _cmp_docs(created_docs, expected_created_docs)
    _cmp_docs(updated_docs, expected_updated_docs, key_fields=['doc_id'])


@pytest.mark.config(
    BILLING_BANK_ORDERS_READ_FRESH_PAYMENTS_ENABLED=True,
    BILLING_BANK_ORDERS_READ_FRESH_PAYMENTS_SETTINGS={
        'max_fails_count': 100,
        'payment_history_path': 'features/oebs/payment_history/',
        'payment_batches_path': 'features/oebs/payment_batches/',
        'yt_clusters': ['hahn'],
        'payments_load_chunk_size': 10000,
        'update_cursor_chunk_size': 2500,
        'save_payment_docs_chunk_size': 100,
        'cursor_max_updates': 500,
    },
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'yt_table_data_path, created_docs_path,'
    'existing_docs_path, retrieve_bulk_response_path',
    [
        (
            'yt_payment_data_without_bclids.json',
            'cursor_and_bclid_not_found_info.json',
            'empty_docs.json',
            'retrieve_bulk_response.json',
        ),
        (
            'yt_payment_data.json',
            'cursor_and_updating_complete_payment_info.json',
            'existing_complete_doc.json',
            'retrieve_bulk_response.json',
        ),
        (
            'yt_payment_data.json',
            'cursor_and_clid_not_found_info.json',
            'empty_docs.json',
            'retrieve_bulk_response_empty.json',
        ),
    ],
    ids=['no-batches', 'invalid-status', 'clid-not-found'],
)
async def test_read_failed_payments(
        mockserver,
        cron_runner,
        load_json,
        yt_table_data_path,
        created_docs_path,
        existing_docs_path,
        retrieve_bulk_response_path,
        patch,
):
    created_docs = []
    yt_table_data = load_json(yt_table_data_path)
    expected_created_docs = load_json(created_docs_path)
    retrieve_bulk_response = load_json(retrieve_bulk_response_path)
    if existing_docs_path is None:
        existing_docs = []
    else:
        existing_docs = load_json(existing_docs_path)

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

    @mockserver.json_handler('/billing-docs/v1/docs/select')
    async def _docs_select(request):
        assert request.json['external_obj_id'] in (
            'taxi_billing_bank_orders_read_fresh_payments_counting_cursor',
            'v1/billing_bank_orders_failed_payments',
        )
        if 'cursor' in request.json['external_obj_id']:
            assert request.json['limit'] == 1
        response = {'docs': [], 'cursor': '', 'limit': request.json['limit']}
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
        return mockserver.make_response(json=retrieve_bulk_response)

    await run_cron.main(
        ['billing_bank_orders.crontasks.read_fresh_payments', '-t', '0'],
    )
    _cmp_docs(created_docs, expected_created_docs)


def _cmp_docs(actual, expected, key_fields=None):
    if key_fields is None:
        key_fields = ['external_obj_id', 'external_event_ref']

    def _key(doc):
        return tuple(doc[key] for key in key_fields)

    actual_dict = {_key(doc): doc for doc in actual}
    expected_dict = {_key(doc): doc for doc in expected}
    assert actual_dict == expected_dict
