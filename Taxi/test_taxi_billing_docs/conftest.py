# pylint: disable=redefined-outer-name
import typing as tp

import pytest

from taxi import secdist
from taxi.billing import pgstorage
from taxi.pytest_plugins import service

from taxi_billing_docs import app
from taxi_billing_docs import config
from taxi_billing_docs.cron import app as cron_app
from taxi_billing_docs.monrun import app as monrun_app
from taxi_billing_docs.stq import context as stq_context

pytest_plugins = ['taxi.pytest_plugins.stq_agent']

TVM_TICKET = 'good_ticket'
YT_STATUS_COMPLETED = 'COMPLETED'
YT_STATUS_ERROR = 'ERROR'


def get_request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture(autouse=True)
def _patch_pgaas_qos(monkeypatch):
    monkeypatch.setattr(
        config.Config,
        'BILLING_DOCS_PGAAS_QOS',
        {'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    )


@pytest.fixture
def request_headers():
    return get_request_headers()


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing-docs')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def bd_secdist(simple_secdist, postgresql_local_settings):
    def _build_asyngpg_string(host, dbname, user):
        return f'postgresql:///{dbname}?user={user}&host={host}'

    def get_shard_info(shard):
        pg_string = shard['master']
        info = dict(item.split('=') for item in pg_string.split(' '))
        info['shard_number'] = shard['shard_number']
        return info

    bd_pg = postgresql_local_settings['databases']['billing_docs']
    shard_info = [get_shard_info(shard) for shard in bd_pg]

    pg_shard_settings = [
        {
            'id': info['shard_number'],
            'cluster_id': 'pg-local-{0}'.format(info['shard_number']),
            'dsn': _build_asyngpg_string(
                info['host'], info['dbname'], info['user'],
            ),
            'host': info['host'],
            'port': None,
            'database': info['dbname'],
            'ro_sync_suffix': '',
            'ssl': None,
        }
        for info in shard_info
    ]
    bd_settings = {
        'meta': 'bd_testsuite_meta',
        'arc_user': {'login': shard_info[0]['user'], 'password': None},
        'ro_user': {'login': shard_info[0]['user'], 'password': None},
        'pg_shards': pg_shard_settings,
    }
    for shard in bd_pg:
        if 'hosts' not in shard:
            shard['hosts'] = [shard['master']]

    simple_secdist['billing_docs'] = bd_settings
    simple_secdist['postgresql_settings'] = postgresql_local_settings
    simple_secdist['postgresql_settings']['databases'][
        'taxi-billing-docs'
    ] = simple_secdist['postgresql_settings']['databases']['billing_docs']


@pytest.fixture
async def docs_app(loop, bd_secdist):
    return app.create_app(loop=loop)


@pytest.fixture
async def docs_stq_app(loop, bd_secdist):
    app = stq_context.Context(loop=loop)
    await app.startup()
    yield app
    await app.cleanup()


@pytest.fixture
async def docs_cron_app(loop, bd_secdist):
    app = cron_app.App(loop)
    await app.startup()

    yield app

    await app.cleanup()


@pytest.fixture
async def docs_monrun_app(loop, bd_secdist):
    app = monrun_app.App(loop)
    await app.startup()

    yield app

    await app.cleanup()


@pytest.fixture
def taxi_billing_docs_client(aiohttp_client, docs_app, loop):
    return loop.run_until_complete(aiohttp_client(docs_app))


@pytest.fixture
def billing_docs_storage(bd_secdist, loop):
    secdist_payload = secdist.load_secdist()
    billing_docs = secdist_payload['billing_docs']
    pg_section = secdist_payload['postgresql_settings']['databases'][
        'billing_docs'
    ]

    storage = loop.run_until_complete(
        pgstorage.create_storage(
            svc_secdist_section=billing_docs,
            pg_secdist_section=pg_section,
            min_size=1,
        ),
    )

    yield storage

    loop.run_until_complete(storage.close())


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


@pytest.fixture
def mocked_yql(patch):
    requests: tp.List[MockedRequest] = []

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def query(query_str, **kwargs):
        nonlocal requests
        return requests.pop(0)

    return requests


service.install_service_local_fixtures(__name__)
