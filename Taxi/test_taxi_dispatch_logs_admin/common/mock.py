import typing as tp

import requests

from taxi.pg import pool as pool_module

from test_taxi_dispatch_logs_admin.common import common as test_common


class Expectation:
    def __init__(self, params, return_value=None):
        self.params = params
        self.return_value = return_value


class MockBase:
    def __init__(self):
        self.expectations = []
        self.call_counter = 0

    def saturated(self):
        for i in range(self.call_counter, len(self.expectations)):
            print(f'not met {self.expectations[i].params}')
        return self.call_counter == len(self.expectations)

    def expect(self, expectations: tp.List[Expectation]):
        self.expectations = expectations

    def check_and_return(self, actual):
        assert self.call_counter < len(self.expectations)

        expected = self.expectations[self.call_counter].params
        return_value = self.expectations[self.call_counter].return_value
        equals = actual == expected
        if not equals:
            print(f'error on call {self.call_counter}:')
            print(f'actual:   {actual}')
            print(f'expected: {expected}')
        self.call_counter += 1
        assert equals

        return return_value


class PgMock(MockBase):
    async def pg_perform(
            self,
            pool: pool_module.Pool,
            action: str,
            query: str,
            log_extra: tp.Optional[dict],
            *args,
    ):
        return self.check_and_return(PgCallParams(action, query, *args))


class PgCallParams:
    def __init__(self, action: str, query: str, *args):
        self.action = action
        self.query = query
        self.args = args

    def __eq__(self, other):
        return (
            other.action == self.action
            and test_common.compare_queries(other.query, self.query)
            and other.args == self.args
        )


class StqMock(MockBase):
    async def stq_client_put(
            self,
            queue,
            eta=None,
            task_id=None,
            args=None,
            kwargs=None,
            loop=None,
    ):
        return self.check_and_return((queue, task_id, kwargs['task_params']))


class YtMock:
    def __init__(self):
        self.configure_mock = MockBase()
        self.read_table_mock = MockBase()
        self.remove_mock = MockBase()
        self.get_table_mock = MockBase()
        self.cypress_tree = None

    def saturated(self):
        return (
            self.configure_mock.saturated()
            and self.read_table_mock.saturated()
            and self.read_table_mock.saturated()
            and self.remove_mock.saturated()
            and self.get_table_mock.saturated()
        )

    def expect_configure(self, expectation: Expectation):
        self.configure_mock.expect([expectation])

    def expect_read_table(self, expectations: tp.List[Expectation]):
        self.read_table_mock.expect(expectations)

    def expect_get_table(self, expectation: Expectation):
        self.get_table_mock.expect(expectation)

    def expect_remove(self, expectations: tp.List[Expectation]):
        self.remove_mock.expect(expectations)

    def yt_configure(self, url: str, token: str):
        return self.configure_mock.check_and_return((url, token))

    # pylint: disable=redefined-builtin
    def yt_read_table(
            self,
            table,
            format=None,
            table_reader=None,
            control_attributes=None,
            unordered=None,
            raw=None,
            response_parameters=None,
            enable_read_parallel=None,
            client=None,
    ):
        return self.read_table_mock.check_and_return((table, format))

    # pylint: enable=redefined-builtin

    def yt_remove(self, path, recursive=False, force=False, client=None):
        return self.remove_mock.check_and_return((path, force))

    def set_cypress_tree(self, cypress_tree: dict):
        self.cypress_tree = cypress_tree

    def yt_list_with_types(self, path) -> tp.List[dict]:
        assert self.cypress_tree is not None
        assert path[0] == '/'

        node = self.cypress_tree['/']
        if path != '/':
            for name in path[2:].split('/'):
                node = node['/'][name]

        return [
            {'name': key, 'type': value['type']}
            for key, value in node['/'].items()
        ]

    def yt_node_exists(self, path: str) -> bool:
        assert self.cypress_tree is not None
        assert path[0] == '/'

        node = self.cypress_tree['/']
        path_nodes = filter(lambda x: x, path.split('/'))

        for node_name in path_nodes:
            if node_name not in node['/']:
                return False
            node = node['/'][node_name]
        return True

    # pylint: disable=redefined-builtin
    def yt_get_table(self, table, format=None) -> str:
        return self.get_table_mock.check_and_return((table, format))


class YqlMock(MockBase):
    async def sync_run_yql_query(
            self,
            db: str,
            db_proxy: str,
            token: str,
            query: str,
            log_extra: tp.Optional[dict] = None,
    ):
        return self.check_and_return(YqlCallParams(db, db_proxy, token, query))


class YqlCallParams:
    def __init__(self, db: str, db_proxy: str, token: str, query: str):
        self.db = db
        self.db_proxy = db_proxy
        self.token = token
        self.query = query

    def __eq__(self, other):
        return (
            other.db == self.db
            and other.db_proxy == self.db_proxy
            and other.token == self.token
            and test_common.compare_queries(other.query, self.query)
        )


class PostMock(MockBase):
    def post(self, url: str, **kwargs) -> requests.models.Response:
        return self.check_and_return(PostCallParams(url, **kwargs))


class PostCallParams:
    def __init__(self, url: str, **kwargs):
        self.url = url
        self.headers = kwargs['headers']
        self.data = kwargs['data']

    def __eq__(self, other):
        return (
            other.url == self.url
            and other.headers == self.headers
            and test_common.compare_queries(other.data, self.data)
        )


class UuidMock:
    def __init__(self):
        self.counter = 0

    def generate_task_id(self):
        new_id = str(self.counter)
        self.counter += 1
        return new_id
