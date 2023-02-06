from unittest import TestCase

from dmp_suite.cli.yt_custom.search_broken_string import find_broken_string


class TestFindBrokenString(TestCase):
    def test_find_broken_string(self):
        broken_fields = [
            b"b'foo'",
            "b'foo'",
            ["qwe", "rty", "b'foo'"],
            {"qwe": {"rty": "b'foo'"}},
            {"qwe": {"b'rty'": "foo"}},
            {"b'qwe'": {"rty": "foo"}}
        ]
        normal_fields = [
            123,
            54.65,
            True,
            [],
            b"foo",
            "foo",
            ["qwe", "rty", "foo"],
            {"qwe": {"rty": "foo"}}
        ]
        for field in broken_fields:
            self.assertTrue(find_broken_string(field))
        for field in normal_fields:
            self.assertFalse(find_broken_string(field))
