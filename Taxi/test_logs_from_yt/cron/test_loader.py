# pylint: disable=redefined-outer-name,unused-variable,no-self-use
import pytest

from logs_from_yt.generated.cron import run_cron


@pytest.fixture
def _patch_yql_operations(patch):
    status_request_run_count = 0
    abort_request_run_count = 0
    share_id_request_run_count = 0
    results_request_run_count = 0

    @patch('yql.api.v1.client.YqlClient')
    def yql_client(*args, **kwargs):
        class YqlClient:
            class YQLRequest:
                _operation_id = 'test_operation_id'
                json = {}

                @classmethod
                def run(cls):
                    pass

                @property
                def operation_id(self):
                    return self._operation_id

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def query(self, *args, **kwarg):
                return self.YQLRequest()

        return YqlClient()

    @patch('yql.client.operation.YqlOperationStatusRequest')
    def yql_operation_status_request(operation_id):
        class YQLRequest:
            status = 'COMPLETED'
            json = {}

            def run(self):
                assert operation_id in ['operation_id_3', 'operation_id_4']
                nonlocal status_request_run_count
                status_request_run_count += 1

        return YQLRequest()

    @patch('yql.client.operation.YqlAbortOperationRequest')
    def yql_operation_abort_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                assert operation_id == 'operation_id_2'
                nonlocal abort_request_run_count
                abort_request_run_count += 1

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationShareIdRequest')
    def yql_operation_share_id_request(op_id):
        class YQLRequest:
            json = 'public_link'

            def run(self):
                nonlocal share_id_request_run_count
                share_id_request_run_count += 1

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationResultsRequest')
    def yql_operation_results_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                if operation_id == 'operation_id_4':
                    raise Exception
                assert operation_id == 'operation_id_3'
                nonlocal results_request_run_count
                results_request_run_count += 1

            def get_results(self):
                return []

        return YQLRequest()

    yield
    assert status_request_run_count == 2
    assert abort_request_run_count == 1
    assert share_id_request_run_count == 1
    assert results_request_run_count == 1


@pytest.mark.usefixtures('_patch_yql_operations')
@pytest.mark.config(ADMIN_LOGS_FROM_YT_MAX_TASK_COUNT=3)
async def test_loader(cron_context, patch):
    @patch('logs_from_yt.components.elastic.ElasticClient')
    def upload_docs(*args, **kwargs):
        class ElasticClient:
            def __init__(self, *args, **kwargs):
                pass

            def upload_docs(self, *args, **kwargs):
                return 1

        return ElasticClient(*args, **kwargs)

    await run_cron.main(['logs_from_yt.crontasks.loader', '-t', '0'])
    collection = cron_context.mongo.logs_from_yt_tasks
    docs = await collection.find().to_list(None)
    docs_by_id = {doc['_id']: doc for doc in docs}
    assert docs_by_id['task_1']['status'] == 'started'
    assert 'started_at' in docs_by_id['task_1']['yql_operation']
    assert 'started_at' in docs_by_id['task_1']
    assert docs_by_id['task_2']['status'] == 'cancelled'
    assert 'finished_at' in docs_by_id['task_2']
    assert docs_by_id['task_3']['status'] == 'finished'
    assert docs_by_id['task_3']['log_count'] == 1
    assert 'finished_at' in docs_by_id['task_3']['yql_operation']
    assert 'finished_at' in docs_by_id['task_3']
    assert docs_by_id['task_4']['status'] == 'failed'
