# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import dataclasses
import typing
import uuid

import pytest

import taxi_billing_audit.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'taxi_billing_audit.generated.cron.pytest_plugin',
    'taxi_billing_audit.generated.service.pytest_plugins',
]


STATUS_COMPLETED = 'COMPLETED'
STATUS_CANCELLED = 'CANCELLED'
STATUS_ERROR = 'ERROR'

YT_DIR = '//home/taxi/unittests/services/taxi-billing-audit/'
YT_DIR_ACCOUNTS = '//home/taxi/unittests/services/taxi-billing-accounts/'

RESULTS_TABLE = YT_DIR + 'results'
RESULTS_COLUMNS = ['id', 'session_id', 'check_type', 'outcome', 'details']
RESULTS_TYPES = ['String', 'String', 'String', 'String', 'Yson']


class _DummyUUID:
    hex = 'hex'


@pytest.fixture
def dummy_uuid4_hex(monkeypatch):
    monkeypatch.setattr(uuid, 'uuid4', _DummyUUID)


@pytest.fixture
def patched_secdist(simple_secdist):
    simple_secdist['settings_override']['STARTRACK_API_PROFILES'] = {
        'billing-audit': {
            'url': 'http://startrack/',
            'org_id': 0,
            'oauth_token': 'STARTRACK_TOKEN',
        },
    }
    return simple_secdist


STRequest = typing.NamedTuple(
    'STRequest', [('method', str), ('url', str), ('json', typing.Any)],
)

# pylint: disable=invalid-name
STRequestList = typing.List[STRequest]


class StartrackCatcher:
    def __init__(self):
        self._coll: STRequestList = []

    def clear(self) -> None:
        self._coll = []

    def add(self, obj: STRequest) -> None:
        self._coll.append(obj)

    @property
    def requests(self) -> STRequestList:
        return self._coll


class MockedTable:
    def __init__(
            self,
            data: typing.List[typing.List[typing.Any]],
            names: typing.Optional[typing.List[str]] = None,
            types: typing.Optional[typing.List[str]] = None,
    ):
        self._data: typing.List[typing.List[typing.Any]] = data
        self._names: typing.List[str] = names or []
        self._types: typing.List[str] = types or []

    def fetch_full_data(self):
        pass

    @property
    def rows(self) -> typing.List[typing.List[typing.Any]]:
        return self._data

    @property
    def column_names(self) -> typing.List[str]:
        return self._names

    @property
    def column_types(self) -> typing.List[str]:
        return self._types

    @property
    def is_good(self) -> bool:
        if len(self.column_names) != len(self.column_types):
            return False
        for row in self.rows:
            if len(row) != len(self.column_names):
                return False
        return True


class MockedResult:
    def __init__(self, status: str, data: typing.List[MockedTable]):
        self._status = status
        self._data = data

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_success(self) -> bool:
        return self._status == STATUS_COMPLETED

    @property
    def errors(self) -> typing.List[Exception]:
        return (
            [Exception('The nastiest error')]
            if self.status == STATUS_ERROR
            else []
        )

    def __iter__(self) -> typing.Iterator:
        yield from self._data


class MockedRequest:
    def __init__(self, result: MockedResult):
        self._result = result

    def run(self):
        pass

    def subscribe(self, *args, **kwargs):
        pass

    def get_results(self, *args, **kwargs):
        return self._result

    @property
    def share_url(self) -> str:
        return 'https://localhost/FakeOperation/001'


class MockedDB:
    def __init__(self):
        self.reset()

    def reset(self):
        self._db: typing.Dict[str, MockedTable] = {
            YT_DIR
            + 'sessions': MockedTable(
                data=[],
                names=[
                    'id',
                    'session_type',
                    'check_at',
                    'begin',
                    'end',
                    'task_id',
                    'base_id',
                ],
                types=[
                    'String',
                    'String',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'String',
                    'String?',
                ],
            ),
            YT_DIR
            + 'results': MockedTable(
                data=[],
                names=['id', 'session_id', 'check_type', 'outcome', 'details'],
                types=['String', 'String', 'String', 'String', 'Yson'],
            ),
            YT_DIR
            + 'tickets': MockedTable(
                data=[],
                names=['created', 'session_id', 'ticket_id'],
                types=['Uint64', 'String', 'String'],
            ),
            YT_DIR
            + 'sessions_fixed': MockedTable(
                data=[],
                names=['created', 'session_id', 'notes'],
                types=['Uint64', 'String', 'String?'],
            ),
            YT_DIR
            + 'journal_vs_yt/requests': MockedTable(
                data=[],
                names=[
                    'created',
                    'interval_begin',
                    'interval_end',
                    'cursor',
                    'items',
                ],
                types=['UInt64', 'Uint64', 'Uint64', 'Yson', 'Yson'],
            ),
            YT_DIR
            + 'journal_vs_yt/blocks': MockedTable(
                data=[],
                names=[
                    'created',
                    'interval_begin',
                    'interval_end',
                    'aggregated',
                ],
                types=['UInt64', 'Uint64', 'Uint64', 'Yson'],
            ),
            YT_DIR_ACCOUNTS
            + 'rollup_journal_by_shard': MockedTable(
                data=[],
                names=[
                    'created',
                    'rollup_start',
                    'rollup_end',
                    'shard_id',
                    'min_id',
                    'max_id',
                    'result',
                ],
                types=[
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'Yson',
                ],
            ),
        }

    def write_table(
            self,
            path: str,
            data_iterator: typing.Iterable,
            column_names: typing.List[str],
            column_types: typing.List[str],
            append: bool = True,
            **kwargs,
    ):
        if path not in self._db or not append:
            self._db[path] = MockedTable(
                data=[], names=column_names, types=column_types,
            )
        print(f'append to {path}')
        for row in data_iterator:
            print(f'  {repr(row)}')
            self._db[path].rows.append(row)
        print('... done')
        assert self._db[path].is_good, f'inconsistent table: {path}'

    def read_table(self, path: str) -> MockedTable:
        assert path in self._db, f'path "{path}" not in {self._db.keys()}'
        print(f'--- {path} ---')
        for row in self._db[path].rows:
            print(f'  {repr(row)}')
        print('--- end of data ---')
        return self._db[path]


@pytest.fixture
def mocked_startrack(patch):

    startrack_catcher = StartrackCatcher()

    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _request(
            url,
            params=None,
            data=None,
            json=None,
            content_type=None,
            method=None,
            log_extra=None,
    ):
        startrack_catcher.add(STRequest(method=method, url=url, json=json))
        ticket_id = uuid.uuid4().hex
        key = f'RND-{ticket_id[:8]}'
        return {'self': f'{url}/{key}', 'key': key, 'id': ticket_id}

    return startrack_catcher


@pytest.fixture
def mocked_yql(patch):
    requests: typing.List[MockedRequest] = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        nonlocal requests
        return requests.pop(0)

    return requests


@pytest.fixture
def mocked_yt(patch) -> MockedDB:

    yt_base = MockedDB()

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.write_table')
    def write_table(
            path: str,
            data_iterator: typing.Iterable,
            column_names: typing.List[str],
            column_types: typing.List[str],
            append: bool = True,
            **kwargs,
    ):
        data = [x for x in data_iterator]
        print(f'mocked_yt write to {path} values: {data}')
        nonlocal yt_base
        yt_base.write_table(
            path, data, column_names, column_types, append, **kwargs,
        )

    return yt_base


@pytest.fixture
def mocked_yt_wrapper(patch):
    _CLIENT = (
        'taxi_billing_audit.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
    )

    @dataclasses.dataclass
    class Responses:
        read_table: list
        get: list
        exists: list

    responses = Responses([], [], [])

    @patch(_CLIENT + 'get')
    async def _get(*args, **kwargs):
        return responses.get.pop(0)

    @patch(_CLIENT + 'set')
    async def _set(*args, **kwargs):
        pass

    @patch(_CLIENT + 'exists')
    async def _exists(*args, **kwargs):
        return responses.exists.pop(0)

    @patch(_CLIENT + 'read_table')
    async def _read_table(*args, **kwargs):
        return responses.read_table.pop(0)

    return responses


@pytest.fixture
def check_result(mocked_yt):
    def fn(expected, expected_outcome='PASSED'):
        rows = mocked_yt.read_table(RESULTS_TABLE).rows
        if expected is None:
            assert not rows, 'results must be empty'
        else:
            print(rows)
            assert rows, 'results must be not empty'
            # 0:session_id, 1:check_id, 2:check_type, 3:outcome, 4:details
            assert rows[0][4] == expected
            assert rows[0][3] == expected_outcome

    return fn
