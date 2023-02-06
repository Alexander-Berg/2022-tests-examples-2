import os

import psycopg2
import psycopg2.extras as extras

import metrika.admin.python.zooface.recursive_deleter.lib as lib
import metrika.admin.python.zooface.recursive_deleter.tests.utils as utils
import metrika.pylib.structures.dotdict as dotdict
import metrika.pylib.zkconnect as zkconnect
import pytest


@pytest.fixture(scope='module')
def cfg():
    cfg = {
        'delete_chunk': 100,
        'update_chunk': 1000,
        'max_child_count': 1000,
        'zooface_root': '/zooface-testing',
        'workers': 1,
        'zk': {
            'env': 'testing',
            'group': 'recipe'
        }
    }
    return dotdict.DotDict.from_dict(cfg)


@pytest.fixture(scope='module')
def zk_client():
    zk_client = zkconnect.get_zk(zk_string=f"{os.environ['RECIPE_ZOOKEEPER_HOST']}:{os.environ['RECIPE_ZOOKEEPER_PORT']}")
    zk_client.start()
    yield zk_client
    zk_client.stop()


@pytest.fixture(scope='module')
def pg_client():
    db = {
        'dbname': os.environ['POSTGRES_RECIPE_DBNAME'],
        'user': os.environ['POSTGRES_RECIPE_USER'],
        'password': None,
        'host': os.environ['POSTGRES_RECIPE_HOST'],
        'port': os.environ['POSTGRES_RECIPE_PORT']
    }
    conn = psycopg2.connect(**db, cursor_factory=extras.RealDictCursor)
    yield conn
    conn.close()


@pytest.fixture(scope='module')
def helper(cfg, zk_client, pg_client):
    class EventMock:
        def is_set(self):
            return False

    class WorkerMock:
        ident = '1337'
        config = cfg
        shutdown = EventMock()
        stopping_tasks = set()
        logger = None

    helper = lib.DeleteHelper(WorkerMock())
    helper.get_zk_client = lambda *args, **kwargs: zk_client
    helper.api_client = utils.ApiMock(pg_client)
    return helper


@pytest.fixture(scope='module')
def db(pg_client):
    utils.execute_query(
        pg_client,
        """
        CREATE TABLE "tasks" (
            "id" serial NOT NULL PRIMARY KEY,
            "created" timestamp with time zone NOT NULL,
            "started" timestamp with time zone NULL,
            "finished" timestamp with time zone NULL,
            "group" varchar(64) NOT NULL,
            "environment" varchar(64) NOT NULL,
            "node" varchar(64) NOT NULL,
            "deleted" integer NOT NULL CHECK ("deleted" >= 0) DEFAULT 0,
            "total" integer NULL CHECK ("total" >= 0),
            "approximately" boolean NOT NULL DEFAULT false,
            "counted" boolean NOT NULL DEFAULT false,
            "status" varchar(64) NOT NULL DEFAULT 'ENQUEUED'
        );
        CREATE UNIQUE INDEX "unique not done node" ON "tasks" ("node") WHERE (status NOT IN ('FINISHED', 'STOPPED'));
        """
    )


@pytest.fixture
def patch_delete(helper, monkeypatch):
    orig_delete = helper.zk_client.delete
    call_count = 0

    def flaky_delete(path, **kwargs):
        nonlocal call_count
        if path.startswith('/test'):
            call_count += 1
            if call_count % 2 == 0:
                helper.logger.debug('Flaky he-he')
                raise Exception('Flaky he-he')

        return orig_delete(path, **kwargs)

    with monkeypatch.context() as m:
        yield m.setattr(helper.zk_client, 'delete', flaky_delete)


@pytest.fixture
def patch_execute(helper, monkeypatch):
    orig_update = helper.api_client.update_task

    def log_update(*args, **kwargs):
        deleted = kwargs.get('deleted')
        if deleted:
            log_update.values.append(deleted)
        return orig_update(*args, **kwargs)

    log_update.values = []

    with monkeypatch.context() as m:
        yield m.setattr(helper.api_client, 'update_task', log_update)


@pytest.fixture
def patch_delete_cancel(helper, pg_client, monkeypatch):
    orig_delete = helper.delete
    MAX_DELETED = 2
    helper.config.delete_chunk = MAX_DELETED + 1

    def delete(zk_client, path, task, deleted):
        if deleted == MAX_DELETED:
            utils.cancel_task(pg_client, task['id'])

        return orig_delete(zk_client, path, task, deleted)

    with monkeypatch.context() as m:
        yield m.setattr(helper, 'delete', delete)


@pytest.fixture
def patch_api(helper, monkeypatch):
    with monkeypatch.context() as m:
        yield m.setattr(helper.api_client, 'get_task', lambda *args, **kwargs: {'status': 'ENQUEUED'})
