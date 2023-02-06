# pylint: disable=redefined-outer-name
import collections
from typing import Optional

import pytest

from taxi.stq import async_worker_ng

import billing_fin_payouts.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['billing_fin_payouts.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def process_payouts_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.fixture(autouse=True)
def create_payments_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.fixture(autouse=True)
def process_payments_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.fixture(autouse=True)
def process_tlog_transactions_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.fixture  # noqa: F405
def mock_yt_client():
    class MockTransaction:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockTablePath:
        def __init__(self, name, **kwargs):
            self.name = name

    # pylint: disable=too-many-instance-attributes
    class MockYtClient:
        Transaction = MockTransaction
        TablePath = MockTablePath

        def __init__(self, cluster_name, nodes=None):
            self.cluster_name = cluster_name
            self.config = {'write_retries': {'enable': False}}
            self.mkdir_calls = []
            self.exists_calls = []
            self.create_calls = []
            self.create_schemas = []
            self.create_calls_optimize_for_scan = True
            self.write_table_calls = collections.defaultdict(list)
            self.get_calls = []
            self.set_calls = []
            self.lock_calls = []

            self._nodes = {}
            if nodes is not None:
                self._nodes = nodes

        async def mkdir(self, folder, **kwargs):
            self.mkdir_calls.append(folder)

        async def exists(self, node):
            self.exists_calls.append(node)
            return node in self._nodes

        async def create(self, node_type, name, **kwargs):
            self.create_calls.append(name)
            schema = kwargs.get('attributes', {}).get('schema')
            if schema:
                self.create_schemas.append([item for item in schema])
            self.create_calls_optimize_for_scan = (
                self.create_calls_optimize_for_scan
                and (
                    kwargs.get('attributes', {}).get('optimize_for') == 'scan'
                )
            )

        async def write_table(self, table_path, rows):
            self.write_table_calls[table_path.name].extend(rows)

        async def get(self, path):
            self.get_calls.append(path)
            return self._nodes.get(path)

        async def set(self, path, value):
            self.set_calls.append({path: value})
            self._nodes[path] = value

        async def lock(self, path, attribute_key, **kwargs):
            self.lock_calls.append({path: attribute_key})

        async def list(self, path):
            result = []
            for existing_path in self._nodes:
                if existing_path.startswith(path):
                    name = existing_path[len(path) + 1 :].split('/')[0]
                    if name and not name.startswith('@'):
                        result.append(name)
            return result

    def _factory(cluster_name: str, nodes: Optional[dict] = None):
        return MockYtClient(cluster_name, nodes)

    return _factory
