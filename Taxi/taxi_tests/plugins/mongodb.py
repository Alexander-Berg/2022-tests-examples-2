import contextlib
import copy
import datetime
import multiprocessing.pool
import pprint
import random
import re
import warnings

import dateutil.parser
import pymongo
import pymongo.collection
import pymongo.errors
import pytest

from taxi_tests import ensure_db_indexes
from taxi_tests import utils
from taxi_tests.environment.services import mongo
# pylint: disable=too-many-statements

pytest_plugins = [
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.mocked_time',
]

DB_FILE_RE_PATTERN = re.compile(r'/db_(?P<mongo_db_alias>\w+)\.json$')


class BaseError(Exception):
    """Base testsuite error"""


class UnknownCollectionError(BaseError):
    pass


class DatabaseConfig:
    def __init__(self, collections):
        for alias, collection in collections.items():
            setattr(self, alias, collection)
        self._collections = collections.copy()
        self._aliases = tuple(collections.keys())

    def get_aliases(self):
        return self._aliases

    def get_local(self, collection_names):
        collections = {}
        for name in collection_names:
            if name not in self._collections:
                raise UnknownCollectionError(
                    'Collection %s is not known' % (name,))
            collections[name] = self._collections[name]
        return DatabaseConfig(collections)


@pytest.fixture
def mongodb(mongodb_init, mongodb_local):
    return mongodb_local


@pytest.fixture(scope='session')
def _mongodb(settings, mongo_collections_settings):
    """All available mongodb collections."""
    return _load_dbconfig(
        settings.MONGO_CONNECTIONS, mongo_collections_settings,
    )


@pytest.fixture(scope='session')
def _indexes_ensured():
    return set()


@pytest.fixture
def _mongo_service(pytestconfig, ensure_service_started, mongodb_local,
                   _mongos_port, _config_server_port, _shard_port):
    aliases = mongodb_local.get_aliases()
    if (aliases and not pytestconfig.getoption('--mongo') and
            not pytestconfig.getoption('--no-mongo')):
        ensure_service_started(
            'mongo',
            mongos_port=_mongos_port,
            config_server_port=_config_server_port,
            shard_port=_shard_port,
        )


@pytest.fixture
def _create_indexes(
        mongodb_local, mongodb_settings, pytestconfig,
        _indexes_ensured, _mongo_service):
    aliases = mongodb_local.get_aliases()
    if not pytestconfig.getoption('--no-indexes'):
        _ensure_indexes = {}
        for alias in aliases:
            if alias not in _indexes_ensured and alias in mongodb_settings:
                _ensure_indexes[alias] = mongodb_settings[alias]
        if _ensure_indexes:
            sharding_enabled = not pytestconfig.getoption('--no-sharding')
            ensure_db_indexes.ensure_db_indexes(
                mongodb_local, _ensure_indexes,
                sharding_enabled=sharding_enabled,
            )
            _indexes_ensured.update(_ensure_indexes)


@pytest.fixture(scope='session')
def _thread_pool():
    pool = multiprocessing.pool.ThreadPool(processes=20)
    with contextlib.closing(pool):
        yield pool


@pytest.fixture
def mongodb_init(request, mongodb_local, load_json, now, _thread_pool,
                 _create_indexes, verify_file_paths):
    """Populate mongodb with fixture data."""
    marker = request.node.get_marker('fixture_now')
    if marker:
        if isinstance(marker.args[0], datetime.datetime):
            now = marker.args[0]
        elif isinstance(marker.args[0], datetime.timedelta):
            now = now - marker.args[0]
        else:
            now = utils.to_utc(dateutil.parser.parse(marker.args[0]))

    if request.node.get_marker('nofilldb'):
        return

    # Disable shuffle to make some buggy test work
    shuffle_enabled = (
        not request.node.config.getoption('--no-shuffle-db')
        and not request.node.get_marker('noshuffledb')
    )
    aliases = {key: key for key in mongodb_local.get_aliases()}
    requested = set()

    marker = request.node.get_marker('filldb')
    if marker:
        for dbname, alias in marker.kwargs.items():
            if dbname not in aliases:
                raise UnknownCollectionError(
                    'Unknown collection %s requested' % (dbname,))
            if alias != 'default':
                aliases[dbname] = '%s_%s' % (dbname, alias)
            requested.add(dbname)

    def _verify_db_alias(file_path):
        match = DB_FILE_RE_PATTERN.search(file_path)
        if match:
            db_alias = match.group('mongo_db_alias')
            if db_alias not in aliases and not any(
                    db_alias.startswith(alias + '_') for alias in aliases):
                return False
        return True

    verify_file_paths(
        _verify_db_alias, check_name='mongo_db_aliases',
        text_at_fail='file has not valid mongo collection name alias '
                     '(probably should add to service.yaml)',
    )

    def load_collection(params):
        dbname, alias = params
        try:
            col = getattr(mongodb_local, dbname)
        except AttributeError:
            return
        try:
            docs = load_json('db_%s.json' % alias, now=now)
        except FileNotFoundError:
            if dbname in requested:
                raise
            docs = []
        if not docs and not col.count():
            return
        bulk = col.initialize_ordered_bulk_op()
        bulk.find({}).remove()

        if shuffle_enabled:
            # Make sure there is no tests that depend on order of
            # documents in fixture file.
            random.shuffle(docs)

        for doc in docs:
            bulk.insert(doc)
        try:
            bulk.execute()
        except pymongo.errors.BulkWriteError as bwe:
            pprint.pprint(bwe.details)
            raise

    pool_args = []
    for dbname, alias in aliases.items():
        pool_args.append((dbname, alias))

    _thread_pool.map(load_collection, pool_args)


@pytest.fixture(scope='session')
def mongo_collections_settings(mongodb_settings):
    collections = copy.deepcopy(_get_db_collections(mongodb_settings))
    return collections


@pytest.fixture(scope='session')
def mongodb_local(mongodb_local_create):
    """Service local mongodb collections.

    Override it in your local project conftest. Returns empty mongo
    configuration by default.
    """
    return mongodb_local_create([])


@pytest.fixture(scope='session')
def mongodb_local_create(_mongodb):
    """Creates local mongodb object."""
    def _mongodb_local_create(collection_names):
        return _mongodb.get_local(collection_names)
    return _mongodb_local_create


@pytest.fixture(scope='session')
def _mongos_port(worker_id, get_free_port):
    if worker_id == 'master':
        return mongo.DEFAULT_MONGOS_PORT
    return get_free_port()


@pytest.fixture(scope='session')
def _config_server_port(worker_id, get_free_port):
    if worker_id == 'master':
        return mongo.DEFAULT_CONFIG_SERVER_PORT
    return get_free_port()


@pytest.fixture(scope='session')
def _shard_port(worker_id, get_free_port):
    if worker_id == 'master':
        return mongo.DEFAULT_SHARD_PORT
    return get_free_port()


@pytest.fixture(scope='session')
def mongo_host(request, _mongos_port):
    host = request.config.getoption('--mongo')
    return host or mongo.get_connection_string(_mongos_port)


def pytest_addoption(parser):
    """
    :param parser: pytest's argument parser
    """
    group = parser.getgroup('mongo')
    group.addoption('--mongo', help='Mongo connection string.')
    group.addoption('--no-indexes', action='store_true',
                    help='Disable index creation.')
    group.addoption('--no-shuffle-db', action='store_true',
                    help='Disable fixture data shuffle.')
    group.addoption('--no-sharding', action='store_true',
                    help='Disable collections sharding.')
    group.addoption('--no-mongo', help='Disable mongo startup',
                    action='store_true')


def _load_dbconfig(mongo_connections, db_collections):
    connections = {}
    for dbalias, uri in mongo_connections.items():
        connections[dbalias] = pymongo.MongoClient(uri)

    collections = {}
    for name, (dbalias, dbname, colname) in db_collections.items():
        if dbalias not in connections:
            warnings.warn(
                'missing connection for dbalias %s' % dbalias)
            continue
        database = getattr(connections[dbalias], dbname)
        collections[name] = getattr(database, colname)

    return DatabaseConfig(collections)


def _get_db_collections(mongodb_settings):
    collections = {
        alias: (
            value['settings']['connection'],
            value['settings']['database'],
            value['settings']['collection'],
        ) for alias, value in mongodb_settings.items()
    }
    return collections
