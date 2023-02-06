# pylint: disable=redefined-outer-name
import collections

import pytest

import taxi_billing_tlog.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_billing_tlog.generated.service.pytest_plugins']


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

        def __init__(self, cluster_name):
            self.cluster_name = cluster_name
            self.config = {'write_retries': {'enable': False}}
            self.mkdir_calls = []
            self.exists_calls = []
            self.create_calls = []
            self.create_calls_optimize_for_scan = True
            self.write_table_calls = collections.defaultdict(list)
            self.get_calls = []
            self.set_calls = []
            self.lock_calls = []

            self._nodes = {}

        def mkdir(self, folder, **kwargs):
            self.mkdir_calls.append(folder)

        def exists(self, node):
            self.exists_calls.append(node)
            return node in self._nodes

        def create(self, node_type, name, **kwargs):
            self.create_calls.append(name)
            self.create_calls_optimize_for_scan = (
                self.create_calls_optimize_for_scan
                and (
                    kwargs.get('attributes', {}).get('optimize_for') == 'scan'
                )
            )

        def write_table(self, table_path, rows):
            self.write_table_calls[table_path.name].extend(rows)

        def get(self, path):
            self.get_calls.append(path)
            return self._nodes.get(path)

        def set(self, path, value):
            self.set_calls.append({path: value})
            self._nodes[path] = value

        def lock(self, path, attribute_key, **kwargs):
            self.lock_calls.append({path: attribute_key})

    def _factory(cluster_name: str):
        return MockYtClient(cluster_name)

    return _factory


@pytest.fixture  # noqa: F405
def mock_psycopg2(patch):
    class Psycopg2Mock:
        fetchall_results = []
        fetchone_results = []

        execute_calls = []

    class Cursor:
        def __init__(self, mock):
            self.mock = mock

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def execute(self, query, *args, **kwargs):
            call = None
            if args:
                call = args[0]
            self.mock.execute_calls.append(call)

        def fetchall(self):
            return self.mock.fetchall_results.pop(0)

        def fetchone(self):
            return self.mock.fetchone_results.pop(0)

    class Connection:
        def __init__(self, mock):
            self.mock = mock

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def cursor(self):
            return Cursor(self.mock)

    result = Psycopg2Mock()

    # pylint: disable=unused-variable
    @patch('psycopg2.connect')
    def connect(*args, **kwargs):
        return Connection(result)

    return result


@pytest.fixture
def mock_tvm(patch):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good':
            return 'dst_service_name'
        return None

    return get_service_name
