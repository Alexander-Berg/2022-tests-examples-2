from typing import List

import pytest

from billing_bank_orders.generated.cron import run_cron


@pytest.mark.config(
    BILLING_BANK_ORDERS_READ_FRESH_ADDITIONAL_DATA_ENABLED=True,
    BILLING_DRIVER_PARTNER_TAXES_BCLID_SELECTOR={
        '__default__': '2000-01-01T00:00+03:00',
    },
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'data_path, expected_data_path',
    [
        (
            'payment_confirmed_data.json',
            'expected_data_payment_confirmed.json',
        ),
        ('payment_void_data.json', 'expected_data_payment_void.json'),
    ],
    ids=['payment-confirm-withdraw', 'payment-void-cancel'],
)
async def test_read_add_data(
        mockserver,
        cron_runner,
        load_json,
        data_path,
        expected_data_path,
        patch,
):
    data = load_json(data_path)
    yt_table_data = data['yt_payments']
    cursor_docs = data['cursor_docs']
    existing_docs = data['existing_docs']
    yt_tables_list = data['yt_tables_list']

    expected_data = load_json(expected_data_path)
    expected_created_docs = expected_data['expected_created_docs']
    expected_updated_docs = expected_data['expected_updated_docs']
    expected_process_async = expected_data['expected_process_async']

    created_docs = []
    updated_docs = []
    actual_process_async = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        class MockedTable:
            def fetch_full_data(self):
                pass

            @property
            def rows(self):
                return [['2020-01-30', '2020-01-31', 100000]]

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
        return yt_tables_list

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
            'read_fresh_add_data_cursor',
            'v1/billing_bank_orders_failed_additional_data',
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

    @mockserver.json_handler('/billing-orders/v2/process/async')
    async def _process_async(request):
        actual_process_async.append(request.json)
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'topic': order['topic'],
                        'external_ref': order['external_ref'],
                        'doc_id': 322,
                    }
                    for order in request.json['orders']
                ],
            },
        )

    @mockserver.json_handler(
        '/parks-replica/v1/parks/by_billing_client_id/retrieve_bulk',
    )
    def get_v1_parks_billing_client_id(request):
        clids_by_bclid = {'228': ['322'], '229': ['323']}
        return mockserver.make_response(
            json={
                'parks': [
                    {'park_id': clid, 'billing_client_id': billing_client_id}
                    for billing_client_id in request.json['billing_client_ids']
                    for clid in clids_by_bclid.get(billing_client_id, [])
                ],
            },
        )

    await run_cron.main(
        [
            'billing_bank_orders.crontasks.read_fresh_additional_data',
            '-t',
            '0',
        ],
    )
    assert expected_process_async == actual_process_async
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
