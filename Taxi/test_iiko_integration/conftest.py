# pylint: disable=redefined-outer-name
import asyncio
import dataclasses
import json

import asyncpg
import pytest

import iiko_integration.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from test_iiko_integration import transactions_stubs


pytest_plugins = ['iiko_integration.generated.service.pytest_plugins']


def _pgrecord_to_dict(record):
    if isinstance(record, asyncpg.Record):
        record = dict(record)
    if isinstance(record, dict):
        return {key: _pgrecord_to_dict(val) for key, val in record.items()}
    if isinstance(record, list):
        return [_pgrecord_to_dict(x) for x in record]
    if isinstance(record, str):
        try:
            return json.loads(record)
        except json.JSONDecodeError:
            return record
    return record


@pytest.fixture
def mock_invoice_retrieve(mockserver):
    def _mock_invoice_retrieve(
            invoice_id, response_data=None, response_code=200,
    ):
        if response_data is None:
            response_data = (
                transactions_stubs.DEFAULT_INVOICE_RETRIEVE_RESPONSE
            )

        @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
        def _invoice_retrieve(request):
            assert request.json == {
                'id': invoice_id,
                'prefer_transactions_data': False,
            }
            if response_code == 200:
                data = {**response_data, 'id': invoice_id}
            else:
                data = {'code': 'c', 'message': 'm'}
            return mockserver.make_response(status=response_code, json=data)

        return _invoice_retrieve

    return _mock_invoice_retrieve


@pytest.fixture(name='mock_invoice_update')
def mock_invoice_update(mockserver):
    def _mock_invoice_update(expected_request_data=None, response_code=200):
        @mockserver.json_handler('/transactions-eda/v2/invoice/update')
        def _invoice_update(request):
            if expected_request_data:
                assert request.json == {**expected_request_data}
            return mockserver.make_response(
                status=response_code,
                json={'code': 'c', 'message': 'm'}
                if response_code != 200
                else {},
            )

        return _invoice_update

    return _mock_invoice_update


@pytest.fixture
def get_db_item(web_context):
    async def _get_db(table_name, fields, **kwargs):
        query_fields = ', '.join(fields)
        kwargs_arr = [f'{key}=\'{value}\'' for key, value in kwargs.items()]
        query_kwargs = 'AND '.join(kwargs_arr)
        async with web_context.pg.ro_pool.acquire() as connection:
            record = await connection.fetchrow(
                f'SELECT {query_fields} FROM {table_name} '
                f'WHERE {query_kwargs}',
            )
            return _pgrecord_to_dict(record)

    return _get_db


@pytest.fixture
def get_db_order(get_db_item):
    async def _get_db_order(fields, **kwargs):
        return await get_db_item(
            table_name='iiko_integration.orders', fields=fields, **kwargs,
        )

    return _get_db_order


@pytest.fixture
def simple_secdist(simple_secdist):
    # в нужные секции дописываем свои значения
    simple_secdist['settings_override'].update(
        {
            'IIKO_API_KEY_SALT': 'WORST_SALT_TO_USE',
            'S3MDS_TAXI_IIKO_INTEGRATION': {
                'url': '',
                'bucket': '',
                'access_key_id': '',
                'secret_key': '',
            },
        },
    )
    return simple_secdist


@pytest.fixture
def check_metrics(patch):
    def _check_metrics(expected_metrics):
        @patch('taxi.clients.solomon.SolomonClient.push_data')
        async def _push_data(push_data, *args, **kwargs):
            assert expected_metrics == push_data.as_dict()['sensors']

    return _check_metrics


@pytest.fixture(name='wait_for_ucommunications_task')
def _wait_for_ucommunications_task_fixture():
    async def wait_for_ucommunications_task():
        all_tasks = asyncio.all_tasks()
        ucommunications_task = None
        for task in all_tasks:
            task_name = str(task)
            if (
                    '_send_notification()' in task_name
                    or '_send_notification_for_status_change()' in task_name
            ):
                ucommunications_task = task
        if ucommunications_task is not None:
            await asyncio.wait([ucommunications_task])

    return wait_for_ucommunications_task


@dataclasses.dataclass
class CallCounter:
    count: int = 0

    def inc(self):
        self.count += 1


@pytest.fixture
def mock_stats(patch):
    def setup_stats(sensor, restaurant=None, restaurant_group=None):
        call_counter = CallCounter()

        @patch('taxi.stats.Stats.get_counter')
        def patched_func(labels):  # pylint: disable=unused-variable
            if labels['sensor'] != sensor:
                return CallCounter()
            if restaurant and restaurant_group:
                assert labels['restaurant_id'] == restaurant
                assert labels['restaurant_group'] == restaurant_group
            return call_counter

        return call_counter

    return setup_stats
