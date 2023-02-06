import pytest

from metrika.pylib import parse_url as pu


@pytest.mark.parametrize('url,keys,values', (
    ("asd=d\tfg&qw'e=,", b"['asd','qw\\'e']", b"['d\\tfg',',']"),
    ("asd=dfg&qwe=rty", b"['asd','qwe']", b"['dfg','rty']"),
    ("", b"[]", b"[]"),
    ("a=1", b"['a']", b"['1']"),
))
def test(url, keys, values):
    assert pu.parse_url(url) == (keys, values)
