import json
import pytest

import yatest.common
import metrika.admin.python.mtapi.lib.api.cluster.lib as cl_lib
import metrika.admin.python.mtapi.lib.api.cluster.models as cl_models
import metrika.admin.python.mtapi.lib.app as lib_app

from time import sleep

from metrika.admin.python.mtapi.lib.peewee_utils import init_db, create_tables
import metrika.pylib.config as lib_config
from metrika.pylib.structures.dotdict import DotDict


def get_config():
    config_file = yatest.common.source_path('metrika/admin/python/mtapi/lib/api/cluster/tests/config.yaml')
    config = lib_config.get_yaml_config_from_file(config_file)
    return config


@pytest.fixture()
def args():
    return DotDict.from_dict(
        {
            "app": "cluster",
            "bishop_env": None,
            "config": yatest.common.source_path('metrika/admin/python/mtapi/lib/api/cluster/tests/config.yaml')
        }
    )


@pytest.fixture(scope="module")
def database():
    config = get_config()
    db = init_db(config.cluster.db_connection, config.cluster.db_type)
    create_tables(db, cl_models.TABLES, truncate=True)


@pytest.fixture(scope="module")
def hosts(database):
    cl_models.Hosts.create(fqdn='test', root_group='test', project='test')


@pytest.fixture()
def client(args, hosts):
    app, config = lib_app.create_app(args)

    with app.test_client() as client:
        yield client


@pytest.fixture
def prepare_refresh(monkeypatch):
    def mock_get_hosts(*args):
        sleep(1)
        with open(yatest.common.work_path('test_data/civil.txt')) as f_h:
            data = f_h.read()

        return data.strip()

    def mock_get_project(*args):
        sleep(1)
        with open(yatest.common.work_path('test_data/ablazh.json')) as f_h:
            data = f_h.read()

        data = json.loads(data)
        return data

    def mock_get_tags(*args):
        sleep(1)
        with open(yatest.common.work_path('test_data/ablazh.json')) as f_h:
            ablazh = f_h.read()

        with open(yatest.common.work_path('test_data/civil.txt')) as f_h:
            civil = f_h.read()

        a = [l.split(';') for l in civil.split('\n') if l]
        b = json.loads(ablazh)
        x = [(a[i][0], b[a[i][1]][a[i][0]]['tags']) for i in range(len(a))]

        return dict(x)

    monkeypatch.setattr(cl_lib, '_get_hosts_from_condutor', mock_get_hosts)
    monkeypatch.setattr(cl_lib, '_get_project_from_conductor', mock_get_project)
    monkeypatch.setattr(cl_lib, '_get_hosts_tags_from_conductor', mock_get_tags)

    yield


@pytest.fixture(
    params=('fqdn',
            'groups',
            'root_group',
            'project',
            'tags',
            'layer',
            'shard',
            'replica',
            'environment',
            'index',
            'dc_suff',
            'dc_name',
            'shard_id',
            )
)
def field(request):
    yield request.param
