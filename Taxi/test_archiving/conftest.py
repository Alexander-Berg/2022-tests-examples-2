# pylint: disable=redefined-outer-name, function-redefined
# pylint: disable=protected-access
import archiving.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

import contextlib  # noqa: I100
import datetime
import logging
import operator
import os
import uuid

from motor import motor_asyncio
import pymongo
import pytest

from taxi import db as taxi_db
from taxi.pytest_plugins import service
from taxi.util import yaml_util
from taxi.util.archiving import base_classes
from taxi.util.archiving import mongo_classes

# pylint: disable=ungrouped-imports
# import of archiving.generated.service.pytest_plugins must be first
from archiving import consts
from archiving import cron_run
from archiving import settings
from archiving.cron_tasks import register_rules
from archiving.generated.cron import cron_context as cron_context_mod
from archiving.sources import managing as sources_managing
from archiving.sources.postgres import archiver as postgres_archiver

pytest_plugins = ['archiving.generated.service.pytest_plugins']

logger = logging.getLogger(__name__)

_TEST_PG_DATABASES = {'pg_test', 'pg_test_conditioned'}
_TEST_MONGO_COLLECTIONS = {
    'real_rules',
    'test_collection',
    'test_collection_filter',
}
_REAL_RULES_REQUESTED = {'order_proc', 'orders', 'holded_subventions'}
_TEST_RULES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'static', 'rules'),
)


# redefine of cron_context because of depends
@pytest.fixture  # type: ignore
async def cron_context(
        _cached_load_yaml_file,
        patch_collection_getter,
        monkeypatch,
        mock_archiving_admin,
        patch_sleep_delay,
):
    ctx = cron_context_mod.Context()
    await ctx.on_startup()
    yield ctx
    await ctx.on_shutdown()


@pytest.fixture
async def requests_handlers(
        cron_context, mockserver, mock_archiving_admin, monkeypatch,
):
    config = cron_context.config
    monkeypatch.setattr(
        config.__class__, 'TEST_FILTER_RULE_TTL', 3600, raising=False,
    )
    # pylint: disable=unused-variable

    @mock_archiving_admin('/archiving/v1/rule/sync_status/', prefix=True)
    async def mock_sync_status(request):
        request_data = request.json
        logger.info('Got data %s', request_data)
        return mockserver.make_response(None)

    @mock_archiving_admin('/admin/v1/rules/retrieve')
    async def rules_retrieve(request):  # pylint: disable=unused-variable
        # pylint: disable=protected-access
        rule_items = register_rules._load_rules_yaml(
            config, rules_dir=settings.RULES_DIR, rules_to_load=None,
        )
        yaml_rules = {'rules': []}
        for rule_item in rule_items:
            ttl_duration_default = rule_item.ttl_info.duration_default
            # TODO: refactor orders tests
            if rule_item.rule_name == 'orders_daily':
                ttl_duration_default = 950400
            yaml_rules['rules'].append(
                {
                    'group_name': rule_item.group_name,
                    'rule_name': rule_item.rule_name,
                    'source_type': rule_item.source_type,
                    'period': rule_item.period,
                    'sleep_delay': rule_item.sleep_delay,
                    'enabled': True,
                    'last_run': [],
                    'ttl_duration': ttl_duration_default,
                },
            )
        return mockserver.make_response(json=yaml_rules)


# TODO: Get rid of this autouse fixture
@pytest.fixture(autouse=True)
def use_pgsql(pgsql):
    pass


# TODO: Get rid of this autouse fixture
@pytest.fixture(autouse=True)
def use_mongo(mongodb):
    pass


@pytest.fixture(scope='session')
def mongodb_collections():
    return [
        'test_collection',
        'test_collection_filter',
        'holded_subventions',
        'order_proc',
        'orders',
    ]


@pytest.fixture(scope='session')
def mongo_schema_extra_directories(tests_dir):
    extra_dir = os.path.join(tests_dir, 'schemas', 'mongo')
    return (extra_dir,)


@pytest.fixture
def simple_secdist(simple_secdist, mongo_connection_info):
    _patch_mongo_connections(mongo_connection_info, simple_secdist)
    return simple_secdist


def _patch_mongo_connections(mongo_connection_info, simple_secdist):
    mongo_settings = simple_secdist.setdefault('mongo_settings', {})
    for collection in _TEST_MONGO_COLLECTIONS:
        mongo_settings[collection] = {'uri': mongo_connection_info.get_uri()}
    mongo_settings['test_collection'] = {
        'uri': mongo_connection_info.get_uri(),
    }


@pytest.fixture(scope='session')
def pgsql_local(pgsql_local_create, tests_dir):
    databases = service.pgsql_discover(
        tests_dir, 'archiving', _TEST_PG_DATABASES,
    )
    return pgsql_local_create(databases)


@pytest.fixture
def patch_collection_getter(monkeypatch, simple_secdist):
    old_getter = taxi_db.get_collections

    def patched_get_collections():
        all_collections = {}
        real_collections = old_getter()
        for real_collection in _REAL_RULES_REQUESTED:
            # pylint: disable=protected-access
            all_collections[real_collection] = real_collections[
                real_collection
            ]._replace(connection='real_rules')
        all_collections.update(_get_service_test_collections())
        return all_collections

    monkeypatch.setattr(taxi_db, 'get_collections', patched_get_collections)


@pytest.fixture
def rules_directories():
    def wrapped_directories(real_rules=True, test_rules=False):
        rules_dirs = []
        if real_rules:
            rules_dirs.append(settings.RULES_DIR)
        if test_rules:
            rules_dirs.append(_TEST_RULES_DIR)
        return rules_dirs

    return wrapped_directories


@pytest.fixture
async def patch_sleep_delay(monkeypatch):
    @contextlib.asynccontextmanager
    async def fake_sleep_between(self, delay):
        yield 0

    async def fake_sleep(self, delay):
        return 0

    monkeypatch.setattr(
        base_classes.SleepLimiter, 'sleep_between', fake_sleep_between,
    )
    monkeypatch.setattr(base_classes.SleepLimiter, 'sleep', fake_sleep)
    monkeypatch.setattr(
        mongo_classes.base_classes.SleepLimiter,
        'sleep_between',
        fake_sleep_between,
    )


@pytest.fixture
@pytest.mark.config(
    TVM_RULES=[{'dst': 'replication', 'src': 'replication-tasks'}],
)
async def patch_test_env(cron_context, monkeypatch):
    monkeypatch.setattr(settings, 'RULES_DIR', _TEST_RULES_DIR)
    monkeypatch.setattr(
        settings,
        'ROOT_DIR_OBJ',
        settings.ROOT_DIR_OBJ.parent.joinpath('test_archiving'),
    )


def _get_service_test_collections():
    extra_collections = {}
    test_collections_path = os.path.join(
        os.path.dirname(__file__), 'schemas', 'mongo',
    )
    for collection_path in os.listdir(test_collections_path):
        full_path = os.path.join(test_collections_path, collection_path)
        collection_settings = yaml_util.load_file(full_path)
        collection_name = os.path.splitext(collection_path)[0]
        extra_collections[collection_name] = taxi_db.CollectionData(
            **collection_settings['settings'],
        )
    return extra_collections


@pytest.fixture(scope='session')
def postgresql_local_settings(tests_dir, pgsql_local):
    dbconfig = service.find_pgsql_databases(
        tests_dir, 'archiving', _TEST_PG_DATABASES,
    )
    return {
        'composite_tables_count': 1,
        'databases': {
            dbname: [
                {
                    'shard_number': shard.shard_id,
                    # pylint: disable=unsubscriptable-object
                    'hosts': [pgsql_local[shard.pretty_name].get_dsn()],
                }
                for shard in sharded_database.shards
            ]
            for dbname, sharded_database in dbconfig.items()
        },
    }


@pytest.fixture(scope='session')
def postgresql_settings_substitute(postgresql_local_settings):
    return {'postgresql_settings': lambda _: postgresql_local_settings}


@pytest.fixture(scope='session')
def _yaml_cache():
    return {}


@pytest.fixture
def _cached_load_yaml_file(monkeypatch, _yaml_cache):
    original = yaml_util.load_file

    def _load_file(path, **kwargs):
        if path not in _yaml_cache:
            _yaml_cache[path] = original(path, **kwargs)
        return _yaml_cache[path]

    monkeypatch.setattr(yaml_util, 'load_file', _load_file)


@pytest.fixture(scope='session')
def fake_task_id():
    return uuid.uuid4().hex


@pytest.fixture
def load_all_mongo_docs(cron_context, fake_task_id):
    async def _load(rule_name):
        archivers = await cron_run.prepare_archivers(
            cron_context, rule_name, fake_task_id,
        )
        # TODO: move it to source implementation?
        docs = {}
        for archiver in archivers.values():
            source = await archiver.get_source()
            source_docs = await source.find().to_list(None)
            docs.update({doc['_id']: doc for doc in source_docs})
        return docs

    return _load


async def load_pg_source_docs(
        archiver,
        primary_key,
        table_name=None,
        get_all_columns=False,
        get_ordered=False,
):
    table = archiver._table if table_name is None else table_name
    if get_all_columns:
        query = f'SELECT * from {table}'
    else:
        select_columns_str = ', '.join(primary_key)
        query = f'SELECT ({select_columns_str}) from {table}'
    if get_ordered:
        primary_key_str = ', '.join(primary_key)
        query += f'\n ORDER BY ({primary_key_str})'
    source = await archiver.get_source(slave=True)
    pk_getter = operator.itemgetter(*primary_key) if primary_key else None
    async with source.acquire() as conn:
        docs = await conn.fetch(query)
        docs = [pk_getter(x) if pk_getter else x for x in docs]
    return docs


@pytest.fixture
def pg_secdist_patch(monkeypatch):
    def _get_pg_dsn(*, secdist, source_settings):
        assert 'connection' in source_settings
        source_settings = {
            **source_settings,
            'connection': 'pg_test_conditioned',
        }
        return postgres_archiver.get_connection_dsn_settings(
            secdist=secdist, source_settings=source_settings,
        )

    monkeypatch.setitem(
        sources_managing._ARCHIVING_SHARDS_GETTERS,
        consts.POSTGRES_SOURCE_TYPE,
        _get_pg_dsn,
    )


@pytest.fixture
def replication_state_min_ts(mockserver):
    url = '/replication/state/min_ts'

    state = {}

    @mockserver.handler(url, prefix=True)
    def get_min_ts(request):
        replication_rule_name = _get_rule_name(request)
        mocked_result = state.get(replication_rule_name)
        if mocked_result is None:
            raise RuntimeError(f'{replication_rule_name} not found')
        return mockserver.make_response(json=mocked_result)

    # pylint: disable=unused-variable
    @mockserver.handler(
        '/replication/v3/state/targets_info/retrieve', prefix=True,
    )
    def targets_info_retrieve(request):
        target_names = request.json['target_names']
        return mockserver.make_response(
            json={
                'target_info': [
                    {
                        'replication_settings': {
                            'replication_type': 'queue',
                            'iteration_field': {
                                'field': state[target_name]['replicate_by'],
                                'type': 'datetime',
                            },
                        },
                        'replication_state': {
                            'overall_status': 'mixed',
                            'last_replicated_datetime': state[target_name][
                                'targets_timestamp'
                            ],
                        },
                        'target_name': target_name,
                        'target_type': 'yt',
                    }
                    for target_name in target_names
                ],
            },
        )

    class Applier:
        @staticmethod
        def apply(data):
            for (
                    replication_rule_name,
                    (replicate_by, timestamp),
            ) in data.items():
                if isinstance(timestamp, datetime.datetime):
                    timestamp = timestamp.isoformat()
                state[replication_rule_name] = {
                    'replicate_by': replicate_by,
                    'targets_timestamp': timestamp,
                    'queue_timestamp': timestamp,
                }

        @classmethod
        def apply_simple(cls, rule_names, *, field, replication_min_ts):
            cls.apply(
                {
                    rule_name: (field, replication_min_ts)
                    for rule_name in rule_names
                },
            )

        handler = get_min_ts

    return Applier()


@pytest.fixture
def replication_sync_api(mockserver, cron_context):
    url = '/replication/sync_data'
    state = {}
    default_status = None

    @mockserver.json_handler(url, prefix=True)
    async def sync_data(request):
        replication_rule_name = _get_rule_name(request)
        items = []
        for requested_doc in request.json['items']:
            doc_id = requested_doc['id']
            status = state.get(replication_rule_name, {}).get(
                doc_id, default_status,
            )
            assert status is not None
            items.append({'id': doc_id, 'status': status})
        return {'items': items}

    class Applier:
        # Response statuses
        STATUS_INSERTED = 'inserted'
        STATUS_NOT_FOUND = 'not_found'
        STATUS_MISMATCH = 'mismatch'
        STATUS_FILTERED = 'filtered'
        STATUS_MATCH = 'match'

        @staticmethod
        def set_default_status(status):
            nonlocal default_status
            assert default_status is None
            default_status = status

        @staticmethod
        def apply(data):
            for replication_rule_name, statuses_by_ids in data.items():
                assert replication_rule_name not in state
                state[replication_rule_name] = statuses_by_ids

        handler = sync_data

    return Applier()


def _get_rule_name(request):
    return request.path.split('/')[-1]


@pytest.fixture
def patch_current_date(monkeypatch):
    def patch_update(update):
        if '$currentDate' in update:
            update.setdefault('$set', {})
            now = datetime.datetime.utcnow()
            for key, value in update['$currentDate'].items():
                assert value is True
                update['$set'][key] = now
            update.pop('$currentDate')

    class PatchedUpdateOne(pymongo.UpdateOne):
        # pylint: disable=redefined-builtin
        def __init__(self, filter, update, *args, **kwargs):
            patch_update(update)
            super().__init__(filter, update, *args, **kwargs)

    monkeypatch.setattr(pymongo, 'UpdateOne', PatchedUpdateOne)

    old_update = motor_asyncio.AsyncIOMotorCollection.update

    async def update(
            self, filter, update, *args, **kwargs,  # pylint: disable=W0622
    ):
        patch_update(update)
        return await old_update(self, filter, update, *args, **kwargs)

    monkeypatch.setattr(motor_asyncio.AsyncIOMotorCollection, 'update', update)
