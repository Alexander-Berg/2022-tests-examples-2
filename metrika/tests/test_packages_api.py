import pytest
from metrika.pylib.http import request
from metrika.pylib.mtapi import mtapi_logger

from metrika.pylib.mtapi.packages import PackagesAPI

BASE_URL = 'https://mtapi-test.mtrs.yandex-team.ru/v1/packages/'
logger = mtapi_logger.getChild('test_packages_api')


@pytest.fixture(scope='session')
def packages_api():
    pkg = request('http://c.yandex-team.ru/api/packages_on_host/mtlog01-01-1.yandex.ru?format=json').json()[0]
    yield pkg, PackagesAPI(BASE_URL)


def test_packages_per_group(packages_api):
    resp = packages_api[1].pkgs_version_per_group('mtlog')
    assert packages_api[0]['name'] in resp[0]
    assert resp[0][packages_api[0]['name']] == packages_api[0]['version']


def test_package_per_group(packages_api):
    resp = packages_api[1].pkg_version_per_group('mtlog', packages_api[0]['name'])
    assert packages_api[0]['version'] == resp


def test_package_per_environment(packages_api):
    resp = packages_api[1].pkg_version_per_environment('production', packages_api[0]['name'])
    assert 0 < len(resp)
    version = None
    for e in resp:
        if e['root_group'] == 'mtlog':
            version = e['pkg_version']
            break
    assert version == packages_api[0]['version']
