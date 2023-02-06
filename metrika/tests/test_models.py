import uuid
import pytest
import yatest.common
import metrika.admin.python.mtapi.lib.api.cluster.lib as cl_lib
import metrika.pylib.config as lib_config
from metrika.pylib.log import init_logger

from metrika.admin.python.mtapi.lib.api.cluster import models

config_file = yatest.common.source_path('metrika/admin/python/mtapi/lib/api/cluster/tests/config.yaml')
config = lib_config.get_yaml_config_from_file(config_file)

TEST_FQDNS = config.tests.test_fqdns
init_logger('peewee', stdout=True)


@pytest.fixture(params=TEST_FQDNS.keys())
def host_model(request):
    info = models.Hosts(fqdn=request.param)
    info.initialise()
    yield info


@pytest.fixture()
def tag_model():
    tag = models.ConductorTags(name='wr', hostname='haha')
    yield tag


class TestHostModelValues:

    def test_fqdn(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.fqdn == origin_dict['fqdn']

    def test_type(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.type == origin_dict['type']

    def test_layer(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.layer == origin_dict['layer']

    def test_shard(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.shard == origin_dict['shard']

    def test_index(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.index == origin_dict['index']

    def test_replica(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.replica == origin_dict['replica']

    def test_environment(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.environment == origin_dict['environment']

    def test_dc_suff(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.dc_suff == origin_dict['dc_suff']

    def test_shard_id(self, host_model):
        origin_dict = TEST_FQDNS.get(host_model.fqdn)
        assert host_model.shard_id == origin_dict['shard_id']


def test_export_as_dict(host_model):
    origin_dict = TEST_FQDNS.get(host_model.fqdn)
    generated_dict = host_model.export_as_dict()

    for key in origin_dict:
        assert origin_dict[key] == generated_dict[key]

    for key in generated_dict:
        if key in ('group', 'root_group', 'project'):
            continue
        assert origin_dict[key] == generated_dict[key]


def test_compare_host_models(host_model):
    origin_dict = TEST_FQDNS.get(host_model.fqdn)
    new_model = models.Hosts(fqdn=origin_dict.get('fqdn'))
    new_model.initialise()
    assert host_model.compare(new_model)
    new_model.layer = 999999
    assert not host_model.compare(new_model)

# def test_tags(tag_model):
#     assert tag_model.name == 'wr'
#     assert tag_model.hostname is None


def test_unexisted_version(database):
    version = cl_lib.GetLastVersion.get_version()
    assert str(version) == '00000000-0000-0000-0000-000000000000'


def test_versions(database):
    version = models.Versions().create_new_version()
    uid = uuid.UUID(version)

    assert uid.version == 4
