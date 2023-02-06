import pytest

from dmp_suite.s3.client import get_endpoint_url


@pytest.mark.parametrize('host, expected', [
    # дефолтно используем https
    ('s3.mdst.yandex.net',  'https://s3.mdst.yandex.net'),
    # если схема была проставлена, должна остаться неизменной
    ('http://s3.mdst.yandex.net',  'http://s3.mdst.yandex.net'),
    ('https://s3.mdst.yandex.net',  'https://s3.mdst.yandex.net'),
])
def test_get_endpoint_url(host, expected):
    assert get_endpoint_url(host) == expected
