# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pymongo
import pytest
from stq_agent_plugins import *  # noqa: F403 F401

from testsuite.utils import yaml_util


@pytest.fixture(name='db_extra')
def _db_extra(mongodb, db_extra_impl):
    _clean_db_extra(mongodb, db_extra_impl)
    return db_extra_impl


@pytest.fixture(name='db_extra_impl', scope='session')
def _db_extra_impl(mongo_connection_info, service_source_dir):
    service_yaml = yaml_util.load_file(service_source_dir / 'service.yaml')
    extra_connections = (
        service_yaml.get('mongo', {})
        .get('testsuite', {})
        .get('extra-connections', [])
    )

    connections = {}
    for connection in extra_connections:
        connections[connection] = pymongo.MongoClient(
            mongo_connection_info.get_uri(),
        )

    return MongoDbExtra(connections)


@pytest.fixture(name='stqs')
def _stqs(mongodb, db_extra):
    return Stqs(mongodb, db_extra)


class MongoDbExtra:
    def __init__(self, connections):
        self._connections = connections

    def connection(self, name):
        class Connection:
            def __init__(self, database):
                self._database = database

            def collection(self, collection_name):
                return getattr(self._database, collection_name)

        return Connection(
            getattr(self._connections[name], 'db{}'.format(name)),
        )

    def shard_collection(self, shard):
        return self.connection(shard['connection']).collection(
            shard['collection'],
        )


class Stqs:
    # pylint: disable=redefined-outer-name
    def __init__(self, db, db_extra):
        self._db = db
        self._db_extra = db_extra

    def get_shard(self, queue_name, shard_id):
        stq_config = self._db.stq_config.find_one({'_id': queue_name})
        shards = stq_config['shards']
        collection = self._db_extra.shard_collection(shards[shard_id])
        return StqShard(collection)


class StqShard:
    def __init__(self, collection):
        self._collection = collection

    @property
    def collection(self):
        return self._collection

    # pylint: disable=invalid-name
    def add_task(
            self,
            task_id,
            a=None,
            k=None,
            x=None,
            e=0.0,
            e_dup=None,
            t=0.0,
            f=0,
            rc=None,
            eu=0.0,
            m=None,
            tag=None,
    ):
        if a is None:
            a = []
        if k is None:
            k = {}
        if e_dup is None:
            e_dup = e
        doc = {
            '_id': task_id,
            'a': a,
            'k': k,
            'x': x,
            'e': e,
            'e_dup': e_dup,
            't': t,
            'f': f,
            'eu': eu,
            'tag': tag,
        }
        if m is not None:
            doc['m'] = m
        if rc is not None:
            doc['rc'] = rc
        self._collection.insert(doc)

    def get_task(self, task_id):
        return self._collection.find_one({'_id': task_id})


def _clean_db_extra(db, db_extra):
    for stq_config in db.stq_config.find():
        for shard in stq_config['shards']:
            collection = db_extra.shard_collection(shard)
            collection.delete_many({})


@pytest.fixture(name='get_stq_config_old')
def _get_stq_config_old(taxi_stq_agent, testpoint):
    @testpoint('queues_configs_get::save_host_queue_seen')
    def save_host_queue_seen(data):
        pass

    async def _get_stq_config(host, queues):
        response = await taxi_stq_agent.post(
            'queues/configs', json={'host': host, 'queues': queues},
        )
        assert response.status_code == 200
        await save_host_queue_seen.wait_call()
        return response.json()

    return _get_stq_config


@pytest.fixture(name='get_stq_config')
def _get_stq_config(taxi_stq_agent, testpoint):
    @testpoint('queues_config::save_host_queue_seen')
    def save_host_queue_seen(data):
        pass

    async def _get_stq_config(host, queues):
        response = await taxi_stq_agent.post(
            'queues/config', json={'host': host, 'queues': queues},
        )
        assert response.status_code == 200
        await save_host_queue_seen.wait_call()
        return response.json()

    return _get_stq_config
