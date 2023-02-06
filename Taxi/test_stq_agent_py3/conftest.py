# pylint: disable=wildcard-import, unused-wildcard-import,
# pylint: disable=redefined-outer-name, unused-variable
import aiohttp.web
import pytest

from stq_agent_py3.clients import conductor
import stq_agent_py3.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from stq_agent_py3.common import stq_config  # noqa: I100
from stq_agent_py3.common import stq_maintenance
from stq_agent_py3.common import stq_shards  # noqa: I100

pytest_plugins = ['stq_agent_py3.generated.service.pytest_plugins']


CONDUCTOR_MOCK_URL = '/conductor'

HOSTS2GROUPS_URL = '/api/hosts2groups/'
GROUPS2HOSTS_URL = '/api/groups2hosts/'
HOSTS_URL = '/api/hosts/'

HANDLERS = [GROUPS2HOSTS_URL, HOSTS_URL, HOSTS2GROUPS_URL]


def pytest_configure(config):
    config.addinivalue_line('markers', 'fillstqdb: fill stq database')


@pytest.fixture
def mock_conductor_url(monkeypatch):
    monkeypatch.setattr(
        conductor.ConductorClient,
        'BASE_URL',
        '$mockserver{}'.format(CONDUCTOR_MOCK_URL),
    )


@pytest.fixture
def fake_grafana_url(monkeypatch):
    monkeypatch.setattr(
        stq_config,
        'GRAFANA_URL_TEMPLATE_BY_ENV',
        {'unittests': 'grafana/{}', 'production': 'grafana/{}'},
    )


@pytest.fixture
def fake_check_stq_tasks(patch, stq_db, cron_context):
    @patch('stq_agent_py3.common.queue_tasks_helpers.read_queue_tasks_file')
    def load():
        return {'processing': 3}


@pytest.fixture
def mock_clownductor_empty(mock_clownductor):
    @mock_clownductor('/v1/hosts/')
    def handler(request):
        return []


@pytest.fixture
def mock_conductor(mockserver):
    def _build_mockserver(hosts_info=None):
        @mockserver.json_handler(CONDUCTOR_MOCK_URL, prefix=True)
        def handler(request, hosts=hosts_info):
            existing_hosts = hosts or {}
            path = request.path_qs[len(CONDUCTOR_MOCK_URL) :]
            assert request.method == 'GET'
            for handler_path in HANDLERS:
                if path.startswith(handler_path):
                    item_name = path[len(handler_path) :].split('?')[0]
                    break
            else:
                raise RuntimeError(f'Unknown conductor url: {request.path_qs}')

            if handler_path == GROUPS2HOSTS_URL:
                result = [
                    {
                        conductor.DATACENTER_NAME: host['datacenter'],
                        conductor.HOSTNAME: host['hostname'],
                    }
                    for host in existing_hosts
                    if host['group'] == item_name
                ]
                if result:
                    return aiohttp.web.json_response(result)
                return aiohttp.web.Response(
                    text='No group {}'.format(item_name), status=404,
                )

            if handler_path == HOSTS_URL:
                request_hosts = item_name.split(',')
                result = [
                    {
                        conductor.GROUP: host['group'],
                        conductor.DATACENTER: host['datacenter'],
                        conductor.HOSTNAME: host['hostname'],
                    }
                    for host in existing_hosts
                    if host['hostname'] in request_hosts
                ]
                if result:
                    return aiohttp.web.json_response(result)
                return aiohttp.web.Response(
                    text='No hosts {}'.format(item_name), status=404,
                )

            if handler_path == HOSTS2GROUPS_URL:
                result = [
                    {'name': host['group']}
                    for host in existing_hosts
                    if host['hostname'] == item_name
                ]
                if result:
                    return aiohttp.web.json_response(result)
                return aiohttp.web.Response(
                    text='No host {}'.format(item_name), status=404,
                )

        return handler

    return _build_mockserver


@pytest.fixture(autouse=True)
def simple_secdist(simple_secdist, mongo_connection_info):
    simple_secdist['mongo_settings'].update(
        {
            'stq': {'uri': mongo_connection_info.get_uri(dbname='dbstq')},
            'stq_2': {'uri': mongo_connection_info.get_uri(dbname='dbstq_2')},
            'stq1': {'uri': mongo_connection_info.get_uri(dbname='dbstq')},
        },
    )
    return simple_secdist


class Secdist:
    def __init__(self, mongo_connection_info, connections):
        mongo_settings = {}
        for connection, database in connections.items():
            mongo_settings[connection] = {
                'uri': mongo_connection_info.get_uri(dbname=database),
            }
        self._settings = {'mongo_settings': mongo_settings}
        # pylint: disable=invalid-name
        self.ro = self._settings

    def __getitem__(self, item):
        return self._settings.__getitem__(item)


@pytest.fixture(autouse=True)
async def stq_db(request, load_json, mongo_connection_info):
    marker = request.node.get_closest_marker('fillstqdb')
    if not marker:
        return
    shards = []
    connections = {}
    for connection, database, collection in marker.kwargs.get(
            'collections', (),
    ):
        shards.append(
            {
                'connection': connection,
                'database': database,
                'collection': collection,
            },
        )
        if connection in connections and connections[connection] != database:
            raise RuntimeError(
                'Different databases specified for one '
                'connection {}'.format(connection),
            )
        connections[connection] = database

    stq_mongo = stq_shards.StqMongoWrapper(
        shards, Secdist(mongo_connection_info, connections),
    )
    for shard in shards:
        collection = stq_mongo.get_shard_collection(shard)
        await stq_maintenance.create_indexes([collection])
        bulk = collection.initialize_ordered_bulk_op()
        bulk.find({}).remove()
        # pylint: disable=protected-access
        try:
            docs = load_json('%s.json' % (stq_shards._get_alias(shard),))
            for doc in docs:
                bulk.insert(doc)
        except FileNotFoundError:
            pass

        await bulk.execute()
    return stq_mongo
