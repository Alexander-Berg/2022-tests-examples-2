import copy
import datetime as dt
import typing as tp

import pytest

from taxi import secdist
from taxi.billing import pgstorage
from taxi.clients import replication
from taxi.pytest_plugins import fixtures_content as conftest
from taxi.pytest_plugins import service

from taxi_billing_accounts import app as accounts_app
from taxi_billing_accounts import config
from taxi_billing_accounts import db as accounts_db
from taxi_billing_accounts.audit import app as audit_app
from taxi_billing_accounts.monrun import app as monrun_app
from taxi_billing_accounts.replication import app as replication_app
from taxi_billing_accounts.replication.handlers import _base
from taxi_billing_accounts.replication.handlers import balance

pytest_plugins = ['taxi.pytest_plugins.stq_agent']

YT_DIR = '//home/taxi/unittests/services/taxi-billing-accounts/'
TVM_TICKET = 'good_ticket'
YT_STATUS_COMPLETED = 'COMPLETED'
YT_STATUS_CANCELLED = 'CANCELLED'
YT_STATUS_ERROR = 'ERROR'


@pytest.fixture
def request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing_accounts')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture(autouse=True)
def _patch_pgaas_qos(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_ACCOUNTS_PGAAS_QOS',
        {'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    )


@pytest.fixture(name='billing_accounts_secdist')
def ba_secdist_fixture(
        loop,
        monkeypatch,
        mongo_settings,
        postgresql_local_settings,
        yt_local_config,
):
    def split_pg_string(pg_string):
        return dict(x.split('=') for x in pg_string.split(' '))

    def _build_asyncpg_string(parts: dict) -> str:
        host = parts['host']
        dbname = parts['dbname']
        user = parts['user']
        asyncpg_string = f'postgresql:///{dbname}?user={user}&host={host}'
        return asyncpg_string

    ba_pg = postgresql_local_settings['databases']['billing_accounts']
    ba_settings = {
        'meta': 'ba_testsuite_meta',
        'pg_shards': [
            {
                'id': shard['shard_number'],
                'cluster_id': 'stub-',
                'dsn': _build_asyncpg_string(parts),
                'ro_sync_suffix': '',
                'database': parts['dbname'],
                'host': parts['host'],
                'port': parts.get('port'),
                'ssl': None,
            }
            for shard, parts in (
                [shard, split_pg_string(shard['master'])] for shard in ba_pg
            )
        ],
        'arc_user': {
            'login': split_pg_string(ba_pg[0]['master'])['user'],
            'password': None,
        },
        'ro_user': {
            'login': split_pg_string(ba_pg[0]['master'])['user'],
            'password': None,
        },
    }

    for shard in ba_pg:
        if 'hosts' not in shard:
            shard['hosts'] = [shard['master']]

    settings_override = copy.deepcopy(conftest.SETTINGS_OVERRIDE)
    settings_override_ro = copy.deepcopy(conftest.SETTINGS_OVERRIDE)
    settings_override.update({'YT_CONFIG': yt_local_config.copy()})
    settings_override_ro.update({'YT_CONFIG': yt_local_config.copy()})

    def load_secdist():
        return {
            'postgresql_settings': postgresql_local_settings,
            'billing_accounts': ba_settings,
            'mongo_settings': mongo_settings,
            'settings_override': settings_override,
        }

    def load_secdist_ro():
        return {
            'postgresql_settings': postgresql_local_settings,
            'billing_accounts': ba_settings,
            'mongo_settings': mongo_settings,
            'settings_override': settings_override_ro,
        }

    monkeypatch.setattr(secdist, 'load_secdist', load_secdist)
    monkeypatch.setattr(secdist, 'load_secdist_ro', load_secdist_ro)


@pytest.fixture(name='billing_accounts_app')
def billing_accounts_app_fixture(loop, billing_accounts_secdist):
    # pylint: disable=protected-access
    return accounts_app._create_app()


@pytest.fixture(name='accounts_cron_app')
async def accounts_cron_app_fixture(loop, billing_accounts_secdist):
    cron_app = replication_app.App(loop=loop)
    await cron_app.startup()
    yield cron_app
    await cron_app.cleanup()


@pytest.fixture(name='accounts_monrun_app')
async def accounts_cron_monrun_fixture(loop, billing_accounts_secdist):
    cron_app = monrun_app.App(loop=loop)
    await cron_app.startup()
    yield cron_app
    await cron_app.cleanup()


@pytest.fixture(name='accounts_audit_cron_app')
async def accounts_cron_audit_app_fixture(loop, billing_accounts_secdist):
    cron_app = audit_app.App(loop=loop)
    await cron_app.startup()
    yield cron_app
    await cron_app.cleanup()


@pytest.fixture
def billing_accounts_client(aiohttp_client, billing_accounts_app, loop):
    return loop.run_until_complete(aiohttp_client(billing_accounts_app))


@pytest.fixture
def billing_accounts_storage(billing_accounts_secdist, loop):
    payload = secdist.load_secdist()
    billing_accounts = payload['billing_accounts']
    pg_section = payload['postgresql_settings']['databases'][
        'billing_accounts'
    ]

    storage = loop.run_until_complete(
        pgstorage.create_storage(
            svc_secdist_section=billing_accounts,
            pg_secdist_section=pg_section,
            min_size=1,
        ),
    )

    yield storage

    loop.run_until_complete(storage.close())


@pytest.fixture
def mock_put_data_into_queue(monkeypatch, mock):
    def _wrap():
        @mock
        async def put_data_into_queue(
                rule: str,
                data: tp.List[replication.ReplicationItem],
                *,
                log_extra: dict,
        ) -> dict:
            return {'items': [{'id': x.id} for x in data]}

        monkeypatch.setattr(
            replication.ReplicationClient,
            'put_data_into_queue',
            put_data_into_queue,
        )
        return put_data_into_queue

    return _wrap


# pylint: disable=invalid-name
@pytest.fixture
def mock_delete_replicated_entries_from_store(monkeypatch, mock):
    def _wrap():
        @mock
        async def delete_replicated_entries(
                vid: int,
                *,
                threshold: dt.datetime,
                chunk_size: int,
                sleep_time: float,
                dry_run: bool,
                log_extra: dict,
        ) -> None:
            return None

        monkeypatch.setattr(
            accounts_db.BalanceReplicationChunksStore,
            'delete_replicated_entries',
            delete_replicated_entries,
        )
        return delete_replicated_entries

    return _wrap


# pylint: disable=invalid-name
@pytest.fixture
def mock_delete_old_chunks_from_store(monkeypatch, mock):
    def _wrap():
        @mock
        async def delete_old_chunks(vid: int, *, log_extra: dict) -> None:
            return None

        monkeypatch.setattr(
            accounts_db.BalanceReplicationChunksStore,
            'delete_old_chunks',
            delete_old_chunks,
        )
        return delete_old_chunks

    return _wrap


@pytest.fixture
def mock_iter_chunks_to_replicate(monkeypatch, mock):
    def _wrap():
        @mock
        async def iter_chunks_to_replicate(
                an_app, vid: int, chunk_size: int, *, log_extra: dict,
        ) -> tp.AsyncIterable[_base.ReplicationDataChunk]:
            # pylint: disable=using-constant-test
            if False:
                yield []

        monkeypatch.setattr(
            balance.BalanceRuleHandler,
            'iter_chunks_to_replicate',
            iter_chunks_to_replicate,
        )
        return iter_chunks_to_replicate

    return _wrap


@pytest.fixture
def mock_iter_chunks_to_reconcile(monkeypatch, mock):
    def _wrap():
        @mock
        async def iter_chunks_to_reconcile(
                an_app, vid: int, recheck_interval: int, *, log_extra: dict,
        ) -> tp.AsyncIterable[_base.ReplicationDataChunk]:
            # pylint: disable=using-constant-test
            if False:
                yield []

        monkeypatch.setattr(
            balance.BalanceRuleHandler,
            'iter_chunks_to_reconcile',
            iter_chunks_to_reconcile,
        )
        return iter_chunks_to_reconcile

    return _wrap


@pytest.fixture
def mock_delete_old_chunks(monkeypatch, mock):
    def _wrap():
        @mock
        async def delete_old_chunks(
                an_app, vid: int, threshold: dt.datetime, *, log_extra: dict,
        ) -> None:
            return None

        monkeypatch.setattr(
            balance.BalanceRuleHandler, 'delete_old_chunks', delete_old_chunks,
        )
        return delete_old_chunks

    return _wrap


class MockedTable:
    def __init__(
            self,
            data: tp.List[tp.List[tp.Any]],
            names: tp.Optional[tp.List[str]] = None,
            types: tp.Optional[tp.List[str]] = None,
    ):
        self._data: tp.List[tp.List[tp.Any]] = data
        self._names: tp.List[str] = names or []
        self._types: tp.List[str] = types or []

    def fetch_full_data(self):
        pass

    @property
    def rows(self) -> tp.List[tp.List[tp.Any]]:
        return self._data

    @property
    def column_names(self) -> tp.List[str]:
        return self._names

    @property
    def column_types(self) -> tp.List[str]:
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
    def __init__(self, status: str, data: tp.List[MockedTable]):
        self._status = status
        self._data = data

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_success(self) -> bool:
        return self._status == YT_STATUS_COMPLETED

    @property
    def errors(self) -> tp.List[Exception]:
        return (
            [Exception('The nastiest error')]
            if self.status == YT_STATUS_ERROR
            else []
        )

    def __iter__(self) -> tp.Iterator:
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
        self._db: tp.Dict[str, MockedTable] = {
            YT_DIR
            + 'journal_chunks_pg': MockedTable(
                data=[],
                names=[
                    'created',
                    'shard_id',
                    'min_id',
                    'max_id',
                    'amount',
                    'total',
                    'currency',
                ],
                types=[
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'String',
                    'Uint64',
                    'String',
                ],
            ),
            YT_DIR
            + 'balance_chunks_pg': MockedTable(
                data=[],
                names=[
                    'created',
                    'shard_id',
                    'journal_id',
                    'amount',
                    'total',
                    'max_accrued_at',
                ],
                types=[
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'String',
                    'Uint64',
                    'Uint64',
                ],
            ),
            YT_DIR
            + 'accounts_chunks_pg': MockedTable(
                data=[],
                names=[
                    'shard_id',
                    'chunk_id',
                    'hash',
                    'total',
                    'created',
                    'last_update',
                ],
                types=[
                    'Int64',
                    'Int64',
                    'Uint64',
                    'Uint64',
                    'Uint64',
                    'Int64',
                ],
            ),
        }

    def write_table(
            self,
            path: str,
            data_iterator: tp.Iterable,
            column_names: tp.List[str],
            column_types: tp.List[str],
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
def mocked_yql(patch):
    requests: tp.List[MockedRequest] = []

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
            data_iterator: tp.Iterable,
            column_names: tp.List[str],
            column_types: tp.List[str],
            append: bool = True,
            **kwargs,
    ):
        nonlocal yt_base
        yt_base.write_table(
            path, data_iterator, column_names, column_types, append, **kwargs,
        )

    return yt_base


service.install_service_local_fixtures(__name__)
