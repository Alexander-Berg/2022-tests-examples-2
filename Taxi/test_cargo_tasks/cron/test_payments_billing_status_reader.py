# pylint: disable=redefined-outer-name
import pytest

from cargo_tasks.generated.cron import run_cron


LOCAL_WORK_DIR = (
    '//home/unittests/unittests'
    '/services/cargo-tasks/payments_billing_status_reader/tmp'
)
UNPROCESSED_DOCS_PATH = f'{LOCAL_WORK_DIR}/unprocessed_docs'
BILLING_STATUS_SENDER_PATH = f'{LOCAL_WORK_DIR}/result'


@pytest.fixture
def patch_yql(patch):
    class YqlSqlOperationRequest:
        def run(self):
            pass

        @property
        def web_url(self):
            return 'mocked_web_url'

        @property
        def share_url(self):
            return 'mocked_share_url'

        @property
        def status(self):
            return 'COMPLETED'

        @property
        def operation_id(self):
            return 'operation_id'

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def patch_yql_query(*args, **kwargs):
        context.last_query = args[0]
        return YqlSqlOperationRequest()

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlSqlOperationRequest')
    def patch_operation_request(*args, **kwargs):
        return YqlSqlOperationRequest()

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlOperationStatusRequest')
    def patch_status_request(*args, **kwargs):
        return YqlSqlOperationRequest()

    class Context:
        def __init__(self):
            self.last_query = None

    context = Context()
    return context


@pytest.fixture(name='mock_unprocessed_docs', autouse=True)
async def _mock_unprocessed_docs(mockserver):
    def _make_unprocessed_doc(
            *, operation_id, billing_doc_id, history_event_id, request_day=1,
    ):
        assert 0 < request_day < 30, 'unepxected day number'
        return {
            'history_event_id': history_event_id,
            'operation_id': operation_id,
            'billing_doc_id': billing_doc_id,
            'billing_request_time': (
                f'2021-07-{request_day:02}T10:10:00.100100+03:00'
            ),
        }

    @mockserver.json_handler('/cargo-payments/v1/billing/unprocessed-docs')
    def mock(request):
        context.requests.append(request.json)
        cursor = request.json.get('cursor', {'fetched_count': 0})
        docs = []
        if context.status_code == 200:
            for i in range(
                    cursor['fetched_count'],
                    min(
                        cursor['fetched_count'] + context.chunk_size,
                        context.total_records,
                    ),
            ):
                docs.append(
                    _make_unprocessed_doc(
                        operation_id=f'operation_id_{i}',
                        billing_doc_id=str(100000 + i),
                        request_day=i // 5 + 1,  # 5 new docs by day
                        history_event_id=i,
                    ),
                )
            return {
                'cursor': {
                    'fetched_count': len(docs) + cursor['fetched_count'],
                },
                'docs': docs,
            }

        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.chunk_size = 5
            self.total_records = 10
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock
            self.requests = []

    context = Context()

    return context


@pytest.fixture(name='mock_update_docs', autouse=True)
async def _mock_update_docs(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/billing/update-docs')
    def mock(request):
        context.requests.append(request.json)
        if context.status_code == 200:
            return {}

        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock
            self.requests = []

    context = Context()

    return context


def _yt_create_table(yt_client, *, table_path, schema, is_static_table=True):
    yt_client.create_table(
        table_path,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': not is_static_table,
            'optimize_for': 'scan',
            'schema': schema,
        },
    )


async def run_payments_cron():
    await run_cron.main(
        ['cargo_tasks.crontasks.payments_billing_status_reader', '-t', '0'],
    )


async def test_unprocessed_docs(
        yt_client, patch_yql, load_json, mock_unprocessed_docs,
):
    """
        Check
        - unprocessed docs fetching
        - unprocessed docs yt upload
    """
    await run_payments_cron()

    assert mock_unprocessed_docs.handler.times_called == 3
    assert sorted(
        yt_client.read_table(UNPROCESSED_DOCS_PATH),
        key=lambda x: x['billing_doc_id'],
    ) == load_json('expected_unprocessed_docs.json')


async def test_sender(yt_client, patch_yql, load_json, mock_update_docs):
    """
        Check
        - fetch yql operation result
        - sending updated docs to cargo-payments
    """
    # fill OEBS data
    yt_client.create_table(
        BILLING_STATUS_SENDER_PATH,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': load_json('result_schema.json'),
        },
    )
    yt_client.write_table(
        BILLING_STATUS_SENDER_PATH, load_json('result_test_data.json'),
    )

    # run cron
    await run_payments_cron()

    assert mock_update_docs.requests == load_json('expected_update_docs.json')


async def test_yql_preprocess(
        yt_client, patch_yql, load, mock_unprocessed_docs,
):
    """
        Check
        - start_date calculated from unprocessed docs
        - start_date replacement
    """
    await run_payments_cron()

    assert patch_yql.last_query == load(
        '../../../../cargo_tasks/storage'
        '/yql/queries/billing_status_by_payment_ids.yql',
    ).replace('{start_date}', '2021-07-01')
