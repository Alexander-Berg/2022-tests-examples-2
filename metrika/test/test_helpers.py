from metrika.admin.python.cms.judge.lib.helpers import host_is_supported
from metrika.pylib.mtapi.cluster import ClusterAPI


def test_host_is_supported_mtapi_exception():
    ClusterAPI.get = lambda *args, **kwargs: [][1]  # Exception
    assert host_is_supported('mtcalclog02kt.yandex.ru')
