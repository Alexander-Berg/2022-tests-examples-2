import re
import six

import pytest
import requests
from metrika.pylib.mtapi.zookeeper import ZookeeperAPI, ZookeeperAPIException

BASE_URL = 'https://mtapi-test.mtrs.yandex-team.ru/v1/zookeeper/'


@pytest.fixture(scope='session')
def zookeeper_api():
    requests.delete(BASE_URL + 'testing/common')
    requests.post(BASE_URL + 'testing/common',
                  json={'hosts': [{'host': 'host1', 'port': 2327}, {'host': 'host2', 'port': 2328}]})
    yield ZookeeperAPI(BASE_URL)
    requests.delete(BASE_URL + 'new_env/common')


def test_getting_resources(zookeeper_api):
    clusters = zookeeper_api.clusters()
    assert {'environment': 'testing', 'group': 'common'} in clusters

    hosts = zookeeper_api.get(environment='testing', group='common')
    assert 2 == len(hosts)
    assert 'host1' == hosts[0]['host']
    assert 'host2' == hosts[1]['host']
    assert 2327 == hosts[0]['port']
    assert 2328 == hosts[1]['port']

    with pytest.raises(ZookeeperAPIException) as exinfo:
        zookeeper_api.get(environment='not_existing_env', group='common')
    assert 'not_existing_env/common' in str(exinfo.value)


def test_get_zk_string(zookeeper_api):
    zk_str = zookeeper_api.get_zk_string(environment='testing', group='common')
    assert isinstance(zk_str, six.string_types)
    assert zk_str.count(',') == 1
    assert zk_str.count(':') == 2


def test_all(zookeeper_api):
    data = zookeeper_api.all()
    assert isinstance(data, dict)
    assert isinstance(data['testing'], dict)
    assert isinstance(data['testing']['common'], list)


def test_all_as_string(zookeeper_api):
    data = zookeeper_api.all_as_string()
    assert isinstance(data, dict)
    assert data['testing_common'].count(',') == 1
    assert data['testing_common'].count(':') == 2


def test_setting_resources(zookeeper_api):
    # using __setattr__
    zookeeper_api.rows = {'environment': 'testing', 'group': 'common', 'host': 'host3', 'port': 2328}

    data = requests.get(BASE_URL + 'testing/common').json().get('data').get('hosts')
    assert 3 == len(data)
    assert 'host3' == data[2]['host']
    assert 2328 == data[2]['port']

    zookeeper_api.rows = {'environment': 'testing', 'group': 'common', 'host': ['host4', 'host5'], 'port': [2328, 2338]}

    data = requests.get(BASE_URL + 'testing/common').json().get('data').get('hosts')
    assert 5 == len(data)
    assert 'host4' == data[3]['host']
    assert 'host5' == data[4]['host']
    assert 2328 == data[3]['port']
    assert 2338 == data[4]['port']

    zookeeper_api.rows = {'environment': 'testing', 'group': 'common', 'host': ['host6', 'host7'], 'port': 2399}

    data = requests.get(BASE_URL + 'testing/common').json().get('data').get('hosts')
    assert 7 == len(data)
    assert 'host6' == data[5]['host']
    assert 'host7' == data[6]['host']
    assert 2399 == data[5]['port']
    assert 2399 == data[6]['port']

    with pytest.raises(ZookeeperAPIException) as exinfo:
        zookeeper_api.rows = {'environment': 'testing', 'group': 'common', 'host': ['host8', 'host9'], 'port': [2328, 2338, 3456]}
    assert 'lengths of "host" and "port" must be the same' in str(exinfo.value)

    with pytest.raises(ZookeeperAPIException) as exinfo:
        zookeeper_api.rows = {'environment': 'testing', 'group': 'common', 'port': 2328}
    assert 'host is a required parameter' in str(exinfo.value)

    # using __getattribute__
    zookeeper_api.add(environment='testing', group='common', host='host8', port=3228)

    data = requests.get(BASE_URL + 'testing/common').json().get('data').get('hosts')
    assert 8 == len(data)
    assert 'host8' == data[7]['host']
    assert 3228 == data[7]['port']

    zookeeper_api.add(environment='testing', group='common', host=['host9', 'host10'], port=[4528, 4538])

    data = requests.get(BASE_URL + 'testing/common').json().get('data').get('hosts')
    data = sorted(data, key=lambda el: int(re.findall(r'\d+$', el['host'])[0]))
    assert 10 == len(data)
    assert 'host9' == data[8]['host']
    assert 'host10' == data[9]['host']
    assert 4528 == data[8]['port']
    assert 4538 == data[9]['port']


def test_updating_resources(zookeeper_api):
    zookeeper_api.update(environment='testing', group='common', update='environment', new_value='new_env',
                         hosts=['host1', 'host2'])

    data = requests.get(BASE_URL + 'testing/common').json().get('data').get('hosts')
    data = sorted(data, key=lambda el: int(re.findall(r'\d+$', el['host'])[0]))
    assert 8 == len(data)
    assert 'host3' == data[0]['host']
    assert 2328 == data[0]['port']

    data = requests.get(BASE_URL + 'new_env/common').json().get('data').get('hosts')
    assert 2 == len(data)
    assert 'host1' == data[0]['host']
    assert 'host2' == data[1]['host']
    assert 2327 == data[0]['port']
    assert 2328 == data[1]['port']

    zookeeper_api.update(environment='new_env', group='common')
    with pytest.raises(ZookeeperAPIException) as exinfo:
        zookeeper_api.get(environment='new_env', group='common')
    assert 'new_env/common' in str(exinfo.value)


def test_delete_resource(zookeeper_api):
    zookeeper_api.delete(environment='testing', group='common')

    resp = requests.get(BASE_URL + 'testing/common')
    assert 404 == resp.status_code
    assert 'testing/common' in resp.json().get('reason')
