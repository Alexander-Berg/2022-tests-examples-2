import pytest
from metrika.pylib.mtapi import mtapi_logger
from metrika.pylib.mtapi.cluster import ClusterAPI


logger = mtapi_logger.getChild('test_mtapi')


@pytest.fixture(scope='session')
def api(mtapi_url, mtapi):
    yield ClusterAPI(mtapi_url)


class TestGet:
    def test_common(self, api):
        data = api.get(fqdn='mtlog01-01-1.yandex.ru')
        assert len(data) == 1
        assert data[0].dc_name == 'sas'
        assert data[0].layer == 1
        assert data[0].shard == 1
        assert data[0].replica == 1
        assert data[0].root_group == 'mtlog'

    def test_multiple_choice(self, api):
        data = api.get(field=['root_group', 'dc_name'], fqdn=['mtlog01-01-1.yandex.ru', 'mtlog01-01-2.yandex.ru'])
        assert len(data) == 2
        assert len(data[1]) == 2
        assert data[1].dc_name == 'iva'
        assert data[1].root_group == 'mtlog'
