import pytest

from sandbox.projects.yabs.qa.hamster.http_request import update_url_query


@pytest.mark.parametrize(("url", "query", "append", "expected_url"), [
    ("http://example.com", [], False, "http://example.com"),
    ("http://example.com", [], True, "http://example.com"),
    ("http://example.com?a=1", [("b", 1)], False, "http://example.com?a=1&b=1"),
    ("http://example.com?a=1", [("b", 1)], True, "http://example.com?a=1&b=1"),
    ("http://example.com?a=1&a=2", [("a", 3)], False, "http://example.com?a=3"),
    ("http://example.com?a=1&a=2", [("a", 3)], True, "http://example.com?a=1&a=2&a=3"),
    ("http://example.com?a=1&a=2", [("a", 3), ("a", 4)], False, "http://example.com?a=3&a=4"),
    ("http://example.com?a=1&a=2", [("a", 3), ("a", 4)], True, "http://example.com?a=1&a=2&a=3&a=4"),
    ("http://example.com?a=1&b=2", [("b", 3), ("c", 4)], True, "http://example.com?a=1&b=2&b=3&c=4"),
    ("http://example.com?a=1&b=2", [("b", 3), ("c", 4)], False, "http://example.com?a=1&b=3&c=4"),
    ("http://example.com?a=&b=2", [("b", 3)], True, "http://example.com?a=&b=2&b=3"),
    ("http://example.com?a=&b=2", [("a", 3)], False, "http://example.com?b=2&a=3"),
    ("http://example.com?a=&b=2", [("a", 3)], True, "http://example.com?a=&b=2&a=3"),
])
def test_update_url_query(url, query, append, expected_url):
    assert update_url_query(url, query, append) == expected_url
