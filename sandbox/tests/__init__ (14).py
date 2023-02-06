# coding: utf-8
from __future__ import absolute_import, print_function, unicode_literals

import datetime as dt
import collections

from sandbox.common import hash as common_hash


class TestJSONHash(object):

    def test__nested(self):
        # Also make sure all possible types are covered, including custom ones like enums
        obj = {
            "foo": {
                "bar": [4.5, [{"bar": "buz"}, {"buz": "bar"}], None, True, ]
            },
            "bar": (7, 6, 5, 3),
            "dt": dt.datetime(year=2019, month=4, day=20, hour=23, minute=59, second=59),
            "date": dt.date(year=2019, month=4, day=20),
        }
        assert common_hash.json_hash(obj) == "ecbc4e18dbae169e92e6a63831272160"

    def test__key_order(self):
        a = collections.OrderedDict([("foo", "bar"), ("bar", "buz")])
        b = collections.OrderedDict([("bar", "buz"), ("foo", "bar")])
        assert common_hash.json_hash(a) == common_hash.json_hash(b)

    def test__sort_lists(self):
        a = {"foo": [1, 2, 3, 4, 5]}
        b = {"foo": [5, 4, 3, 2, 1]}
        assert common_hash.json_hash(a) != common_hash.json_hash(b)
        assert common_hash.json_hash(a, sort_lists=True) == common_hash.json_hash(b, sort_lists=True)
