import metrika.pylib.zkconnect


class TestImport:
    def test_import(self):
        assert isinstance(metrika.pylib.zkconnect.KazooClientMetrika, type) == 1


def test_zapi_group():
    zk = metrika.pylib.zkconnect.get_zk(zapi_env='production', zapi_group='external')
    assert isinstance(zk.hosts, list)
    assert len(zk.hosts) >= 3
