import pytest

from grabber.stq.operations import operation_runner


@pytest.fixture
def _patch_yql_order_full(patch):
    @patch('yql.api.v1.client.YqlClient')
    def _yql_client(*args, **kwargs):
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
    def _yql_operation_status_request(operation_id):
        class YQLRequest:
            status = 'COMPLETED'
            json = {}

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlAbortOperationRequest')
    def _yql_operation_abort_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationShareIdRequest')
    def _yql_operation_share_id_request(op_id):
        class YQLRequest:
            json = 'public_link'

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationResultsRequest')
    def _yql_operation_results_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                pass

            def get_results(self):
                class Result:
                    def __init__(self):
                        self.rows = [
                            (1538564410.711, 1538565795.02, 'asdasdasd'),
                        ]
                        self.column_names = [
                            'driving_time',
                            'complete_time',
                            'performer_uuid',
                        ]

                    def fetch_full_data(self):
                        return self.rows

                return [Result()]

        return YQLRequest()


@pytest.mark.usefixtures('_patch_yql_order_full')
async def test_task(stq3_context, pgsql):
    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.tasks (task_id, order_id)'
        'VALUES (\'task_id\', \'order_id\')',
    )  # noqa E501

    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.operations (operation_id, operation_type, operation_status, task_id, operation_data_type)'  # noqa E501
        'VALUES (\'task_id1\', \'yql_query\', \'created\', \'task_id\', \'order/receipt\')',  # noqa E501
    )
    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.yql_operations (operation_id, yql_operation_id, yql_query)'  # noqa E501
        'VALUES (\'task_id1\', \'yql_id\', \'query\')',
    )

    await operation_runner.run(stq3_context, 'task_id1', 'yql_query')

    await operation_runner.run(stq3_context, 'task_id1', 'yql_query')

    with pgsql['grabber'].cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM grabber.operations_data
            WHERE operation_id = 'task_id1';
            """,
        )
        assert cursor.rowcount == 1
