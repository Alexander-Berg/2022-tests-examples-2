# pylint: disable=unused-variable
import pytest


@pytest.mark.parametrize(
    ['headers', 'json', 'expected_status', 'expected_json'],
    [
        (
            {'X-YaTaxi-Api-Key': 'foo'},
            {},
            403,
            {'code': 'AUTHORIZATION_ERROR', 'message': 'bad token'},
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                'start_time': '2019-06-24T14:30:00+03:00',
                'end_time': '2019-06-24T16:30:00+03:00',
                'filters': [
                    {
                        'key': 'meta_order_id',
                        'value': 'test_order_id',
                        'service_names': ['protocol'],
                    },
                    {
                        'key': 'meta_user_id',
                        'value': 'test_user_id',
                        'service_names': ['protocol'],
                    },
                ],
            },
            200,
            {
                'status': 'queued',
                'author': 'nevladov',
                'created_at': '2019-06-24T14:30:00+03:00',
                'message': '',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                # query validation error (too early range, see below)
                'start_time': '2018-06-24T14:30:00+03:00',
                'end_time': '2018-06-24T16:30:00+03:00',
                'filters': [
                    {
                        'key': 'meta_order_id',
                        'value': 'test_order_id',
                        'service_names': ['protocol'],
                    },
                    {
                        'key': 'meta_user_id',
                        'value': 'test_user_id',
                        'service_names': ['protocol'],
                    },
                ],
            },
            400,
            {
                'code': 'NO_TABLES_WITH_LOGS',
                'message': (
                    'tables with logs for this range are already '
                    'expired or not created yet'
                ),
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                'start_time': '2019-06-24T14:30:00+03:00',
                'end_time': '2019-06-24T16:30:00+03:00',
                'filters': [
                    {
                        'key': 'meta_order_id',
                        'value': 'test_order_id_1',
                        'service_names': ['protocol'],
                    },
                    {
                        'key': 'meta_order_id',
                        'value': 'test_order_id_2',
                        'service_names': ['protocol'],
                    },
                ],
            },
            400,
            {
                'message': 'key "meta_order_id" is specified multiple times',
                'code': 'REQUEST_ERROR',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                'start_time': '2019-06-24T14:30:00+03:00',
                'end_time': '2019-06-24T16:30:00+03:00',
                'filters': [
                    {
                        'key': 'meta_user_id',
                        'value': 'test_user_id',
                        'service_names': ['protocol'],
                    },
                ],
            },
            409,
            {
                'code': 'SIMILAR_TASK_IS_ALREADY_RUNNING',
                'message': 'similar task "task_1" is already running',
            },
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                'start_time': '2019-06-24T14:30:00+03:00',
                'end_time': '2019-06-24T16:30:00+03:00',
                'filters': [
                    {
                        # unsupported field
                        'key': 'meta_unknown_id',
                        'value': 'test_user_id',
                        'service_names': ['protocol'],
                    },
                ],
            },
            400,
            None,
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                'start_time': '2019-06-24T14:30:00+03:00',
                'end_time': '2019-06-24T16:30:00+03:00',
                'filters': [
                    {
                        # unsupported service
                        'key': 'meta_user_id',
                        'value': 'test_user_id',
                        'service_names': ['UNKNOWN'],
                    },
                ],
            },
            400,
            None,
        ),
        (
            {'X-YaTaxi-Api-Key': 'secret', 'X-Yandex-Login': 'nevladov'},
            {
                'start_time': '2019-06-24T14:30:00+03:00',
                'end_time': '2019-06-25T16:30:00+03:00',
                'filters': [
                    {
                        'key': 'meta_order_id',
                        'value': 'test_order_id',
                        'service_names': ['protocol'],
                    },
                ],
            },
            400,
            {'message': 'too long interval', 'code': 'REQUEST_ERROR'},
        ),
    ],
)
@pytest.mark.now('2019-06-24T14:30:00+03:00')
async def test_create_task(
        patch, web_app_client, headers, json, expected_status, expected_json,
):
    @patch('yql.client.explain.YqlSqlValidateRequest')
    def yql_sql_validate_request(*args, **kwargs):
        class YQLRequest:
            operation_id = None

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationResultsRequest')
    def yql_operation_results_request(operation_id):
        class YQLRequest:
            def run(self):
                pass

            def get_results(self):
                class Results:
                    json = {
                        'errors': [
                            {
                                'column': 0,
                                'file': '<main>',
                                'message': 'Pre type annotation',
                                'row': 0,
                            },
                            {
                                'column': 15,
                                'file': '<main>',
                                'message': 'The list of tables is empty',
                                'row': 11,
                            },
                        ],
                    }

                    @property
                    def status(self):
                        if '2018' in json['start_time']:
                            return 'ERROR'
                        return 'COMPLETED'

                return Results()

        return YQLRequest()

    response = await web_app_client.post(
        '/v1/tasks/', headers=headers, json=json,
    )
    assert response.status == expected_status
    if expected_json is not None:
        result = await response.json()
        if response.status == 200:
            result.pop('task_id')
            request = result.pop('request')
            assert request == json
        assert expected_json == result
