import pytest
from metrika.admin.python.mtapi.lib.api.packages import lib as mtplib

from werkzeug.exceptions import BadRequest, NotFound

from metrika.pylib.log import base_logger, init_logger
import metrika.admin.python.mtapi.lib.api.packages.api as pkg_api


init_logger('mtapi', stdout=True)
init_logger('mtutils', stdout=True)
init_logger('cluster', stdout=True)
logger = base_logger.getChild(__name__)


def test_list_all_packages(populate_mock):
    bpvg = pkg_api.BulkPackageVersionGetter()
    resp = bpvg.get('mtlog')
    data = resp['data']
    assert 1 == len(data)
    pkg = data[0]
    assert 1 == len(pkg.keys())
    assert 'bummer-lib-metrika-yandex' == next(iter(pkg.keys()))
    assert '2.9.777' == pkg['bummer-lib-metrika-yandex']

    with pytest.raises(BadRequest):
        bpvg.get('not_existing_group')


def test_list_one_package(populate_mock):
    pvg = pkg_api.PackageVersionGetter()
    resp = pvg.get('mtlog', 'bummer-lib-metrika-yandex')
    assert '2.9.777' == resp['data']

    with pytest.raises(NotFound):
        pvg.get('mtlog', 'not_existing_package')


class TestPkgsPerEnv:
    def test_simple(self, populate_mock, deploy_pkg_version_getter):
        epg = pkg_api.EnvironmentPackagesGetter()
        resp = epg.get('testing', 'bummer-lib-metrika-yandex')
        assert '2.9.777' == resp['data'][0]['pkg_version']

    def test_unexisted(self, populate_mock, mock_deploy_bad, deploy_pkg_version_getter):
        epg = pkg_api.EnvironmentPackagesGetter()
        with pytest.raises(BadRequest):
            epg.get('testing', 'not_existing_package')

    def test_from_deploy(self, populate_mock, mock_deploy_good, deploy_pkg_version_getter):
        epg = pkg_api.EnvironmentPackagesGetter()
        resp = epg.get('production', 'asd')
        assert resp['data'][0]['pkg_version'] == '100500'


class TestVersionFromDeploy:
    def test_get_version(self, mock_deploy_good, deploy_pkg_version_getter, populate_mock):
        assert deploy_pkg_version_getter.get('asd')['data'] == '100500'
        assert deploy_pkg_version_getter.get('asd', 'production')['data'] == '100500'


class TestGetInfo:
    def test_stage_doesnt_exist(self, rr_doesnt_exist):
        api = pkg_api.YandexDeployPackageStageGetter()
        api.deploy_api = rr_doesnt_exist
        with pytest.raises(NotFound):
            assert api.get('test', 'testing')['data']

    def test_stage_exists(self, rr_exists_with_versions):
        api = pkg_api.YandexDeployPackageStageGetter()
        api.deploy_api = rr_exists_with_versions
        assert api.get('test', 'testing')['data'] == {
            'stage': 'stage', 'deploy_unit': 'du', 'box': 'box', 'layer': 'layer',
        }


class TestGetReleaseInfo:
    def test_with_release(self, getter_with_release, monkeypatch):
        api = pkg_api.YandexDeployReleaseGetter()
        monkeypatch.setattr(mtplib, 'DeployVersionGetter', lambda *args, **kwargs: getter_with_release)
        assert api.get('test', 'testing')['data'] == {'version': '1337', 'deploy_datetime': '1970-01-01 00:00:00', 'author': 'from_release', 'release_id': '1337'}

    def test_without_release(self, getter_without_release, monkeypatch):
        api = pkg_api.YandexDeployReleaseGetter()
        monkeypatch.setattr(mtplib, 'DeployVersionGetter', lambda *args, **kwargs: getter_without_release)
        assert api.get('test', 'testing')['data'] == {'version': '1337', 'deploy_datetime': '1970-01-01 00:00:00', 'author': 'from_revision', 'release_id': None}
