import os

import mock
import json

import utils.common as common
import connections.clickhouse.client as clickhouse


test_secdist_config = os.path.dirname(__file__) + '/test_secdist.yaml'
test_config = common.read_yaml(test_secdist_config)
test_config_with_cluster = common.path_extractor(test_config, 'clickhouse.connections.test_cluster')
test_config_without_cluster = common.path_extractor(test_config, 'clickhouse.connections.test_without_cluster')


class TestClickHouseConfigPreparation(object):
    def test_config_preparation(self):
        assert clickhouse.ClusterSettings._secdist_search_path('test') == 'clickhouse.connections.test'
        assert clickhouse.ClusterSettings._secdist_search_path() is None


@mock.patch.object(clickhouse.ClusterSettings, '_get_secdist_params', return_value=test_config_with_cluster)
class TestClickHouseConfig(object):

    def test_clickhouse_cluster_settings(self, mock_object):
        clickhouse_cluster = clickhouse.ClusterSettings('test_cluster')
        assert clickhouse_cluster.cluster_name == 'testcluster'
        assert clickhouse_cluster.host == 'clickhouse-test.taxi.yandex.net'
        assert clickhouse_cluster.port_client == 9000
        assert clickhouse_cluster.port_http == 8123
        assert clickhouse_cluster.user == 'test_user'
        assert clickhouse_cluster.password == 'test_password'

    def test_clickhouse_config(self, mock_object):
        config = clickhouse.Config()
        clickhouse_cluster = config['test_cluster']
        assert clickhouse_cluster.cluster_name == 'testcluster'
        assert clickhouse_cluster.host == 'clickhouse-test.taxi.yandex.net'
        assert clickhouse_cluster.port_client == 9000
        assert clickhouse_cluster.port_http == 8123
        assert clickhouse_cluster.user == 'test_user'
        assert clickhouse_cluster.password == 'test_password'


@mock.patch.object(clickhouse.ClusterSettings, '_get_secdist_params', return_value=test_config_with_cluster)
class TestClickHouseConfigWithCluster(object):

    def test_clickhouse_with_cluster(self, mock_object):
        clickhouse_cluster = clickhouse.ClusterSettings('test_cluster')
        assert clickhouse_cluster.cluster_name == 'testcluster'
        assert clickhouse_cluster.host == 'clickhouse-test.taxi.yandex.net'
        assert clickhouse_cluster.port_client == 9000
        assert clickhouse_cluster.port_http == 8123
        assert clickhouse_cluster.user == 'test_user'
        assert clickhouse_cluster.password == 'test_password'


@mock.patch.object(clickhouse.ClusterSettings, '_get_secdist_params', return_value=test_config_without_cluster)
class TestClickHouseConfigWithoutCluster(object):

    def test_clickhouse_without_cluster(self, mock_object):
        clickhouse_cluster = clickhouse.ClusterSettings('test_without_cluster')
        assert clickhouse_cluster.cluster_name is None
        assert clickhouse_cluster.host == 'clickhouse-test.taxi.yandex.net'
        assert clickhouse_cluster.port_client == 9000
        assert clickhouse_cluster.port_http == 8123
        assert clickhouse_cluster.user == 'test_user'
        assert clickhouse_cluster.password == 'test_password'


class TestClickHouseResponse(object):
    def test_response(self):
        data = {'field_1': 1, 'field_2': 'abc'}
        data_dump = json.dumps(data)
        data_text = u'1\tabc\n'

        response = clickhouse.Response(data_text)
        assert response.text == data_text

        response = clickhouse.Response(data_dump)
        assert response.json == data


class TestClickHouseClient(object):
    def test_client(self):
        assert clickhouse.Client._connection_string('host', 1111) == 'http://host:1111/'
        assert clickhouse.Client._connection_string() == 'http://None:None/'
