import pytest
import yatest.common
from mock import MagicMock
import metrika.pylib.config as lib_config
from metrika.pylib.log import init_logger, base_logger
from werkzeug.exceptions import NotFound, BadRequest
from werkzeug.local import LocalProxy

import metrika.admin.python.mtapi.lib.peewee_utils as mtpu
from metrika.admin.python.mtapi.lib.api.zookeeper.api import Handler, Explorer, ExplorerAllAsString, ExplorerAll
from metrika.admin.python.mtapi.lib.api.zookeeper.models import TABLES

config_file = yatest.common.source_path('metrika/admin/python/mtapi/lib/api/zookeeper/tests/config.yaml')
config = lib_config.get_yaml_config_from_file(config_file)

init_logger('mtapi', stdout=True)
init_logger('mtutils', stdout=True)
logger = base_logger.getChild(__name__)

base_url = config.zookeeper.api.base_url


@pytest.fixture(scope='session')
def database():
    db = mtpu.init_db(config.zookeeper.db_connection, config.zookeeper.db_type)
    mtpu.create_tables(db, TABLES, truncate=True)


def test_unique_insert(database, monkeypatch):
    mock_req_body(monkeypatch, {'hosts': [{'host': 'host1', 'port': 2327}, {'host': 'host2', 'port': 2327}, {'host': 'host3', 'port': 2327}]})

    zk_handler = Handler()
    zk_handler.post('env', 'group')

    db_content = mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall()
    assert len(db_content) == 3
    assert db_content[0][0] == "group" and db_content[1][0] == "group" and db_content[2][0] == "group"
    assert db_content[0][1] == "env" and db_content[1][1] == "env" and db_content[2][1] == "env"
    assert db_content[0][2] == "host1" and db_content[1][2] == "host2" and db_content[2][2] == "host3"
    assert db_content[0][3] == 2327 and db_content[1][3] == 2327 and db_content[2][3] == 2327


def test_duplicate_insert(database, monkeypatch):
    mock_req_body(monkeypatch, {'hosts': [{'host': 'host1', 'port': 2327}, {'host': 'host4', 'port': 2327}]})

    zk_handler = Handler()
    with pytest.raises(BadRequest):
        zk_handler.post('env', 'group')


def test_duplicate_insert_2(database, monkeypatch):
    mock_req_body(monkeypatch, {'hosts': [{'host': 'host4', 'port': 2327}, {'host': 'host1', 'port': 2327}]})

    zk_handler = Handler()
    with pytest.raises(BadRequest):
        zk_handler.post('env', 'group')

    db_content = mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall()

    assert len(db_content) == 3


def test_valid_get(database, monkeypatch):
    mock_req_body(monkeypatch, MagicMock())

    zk_handler = Handler()
    resp = zk_handler.get('env', 'group')

    hosts = sorted(resp['data']['hosts'], key=lambda x: x['host'])
    assert hosts[0]['host'] == 'host1' and hosts[0]['port'] == 2327
    assert hosts[1]['host'] == 'host2' and hosts[1]['port'] == 2327
    assert hosts[2]['host'] == 'host3' and hosts[2]['port'] == 2327


def test_invalid_get(database, monkeypatch):
    mock_req_body(monkeypatch, MagicMock())

    zk_handler = Handler()
    with pytest.raises(NotFound):
        zk_handler.get('not', 'exists')


def test_valid_put1(database, monkeypatch):
    mock_req_body(monkeypatch, {'update': 'environment', 'new_value': 'new_env', 'hosts': ['host1', 'host2']})

    zk_handler = Handler()
    zk_handler.put('env', 'group')

    db_content = sorted(mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall(), key=lambda x: x[2])
    assert 'new_env' == db_content[0][1]
    assert 'new_env' == db_content[1][1]
    assert 'env' == db_content[2][1]


def test_valid_put2(database, monkeypatch):
    mock_req_body(monkeypatch, {'update': 'port', 'new_value': 2326})

    zk_handler = Handler()
    zk_handler.put('new_env', 'group')

    db_content = sorted(mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall(), key=lambda x: x[2])
    assert 2326 == db_content[0][3]
    assert 2326 == db_content[1][3]
    assert 2327 == db_content[2][3]


def test_valid_put3(database, monkeypatch):
    mock_req_body(monkeypatch, {'hosts': ['host3']})

    zk_handler = Handler()
    zk_handler.put('env', 'group')

    db_content = mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall()
    assert 2 == len(db_content)
    assert 'host1' in list(zip(db_content[0], db_content[1]))[2]
    assert 'host2' in list(zip(db_content[0], db_content[1]))[2]
    assert 'host3' not in list(zip(db_content[0], db_content[1]))[2]


def test_valid_put4(database, monkeypatch):
    mock_req_body(monkeypatch, {'update': 'host', 'new_value': 'host22', 'hosts': ['host2']})

    zk_handler = Handler()
    zk_handler.put('new_env', 'group')

    db_content = mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall()
    assert 2 == len(db_content)
    assert 'host1' in list(zip(db_content[0], db_content[1]))[2]
    assert 'host22' in list(zip(db_content[0], db_content[1]))[2]


def test_invalid_put(database, monkeypatch):
    mock_req_body(monkeypatch, {'new_value': 'new_env', 'hosts': ['host1', 'host2']})

    zk_handler = Handler()
    with pytest.raises(BadRequest):
        zk_handler.put('env', 'group')


def test_explorer_with_data(database, monkeypatch):
    mock_req_body(monkeypatch, MagicMock())

    explorer = Explorer()
    resp = explorer.get()

    assert 1 == len(resp['data'])
    assert 'new_env' == resp['data'][0]['environment']
    assert 'group' == resp['data'][0]['group']


def test_explorer_all_as_string(database, monkeypatch):
    mock_req_body(monkeypatch, MagicMock())

    explorer = ExplorerAllAsString()
    resp = explorer.get()

    assert len(resp['data']) == 1
    cluster_name, cluster = next(iter(resp['data'].items()))
    assert isinstance(cluster_name, str)
    assert isinstance(cluster, str)

    assert cluster_name == 'new_env_group'

    hosts = cluster.split(',')
    assert len(hosts) == 2
    assert 'host22:2326' in hosts
    assert 'host1:2326' in hosts


def test_explorer_all(database, monkeypatch):
    mock_req_body(monkeypatch, MagicMock())

    explorer = ExplorerAll()
    resp = explorer.get()

    assert isinstance(resp['data']['new_env']['group'], list)
    assert isinstance(resp['data']['new_env']['group'][0], dict)
    assert 2 == len(resp['data']['new_env']['group'])


def test_delete(database, monkeypatch):
    mock_req_body(monkeypatch, MagicMock())

    zk_handler = Handler()
    zk_handler.delete('new_env', 'group')

    db_content = mtpu.proxy.execute_sql("select * from zookeeperhosts").fetchall()
    assert len(db_content) == 0


def mock_req_body(monkeypatch, body):
    monkeypatch.setattr(LocalProxy, '__getattr__', lambda *args: MagicMock(return_value=body))
