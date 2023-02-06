# coding=utf-8
from __future__ import unicode_literals

from sandbox.projects.metrika.core.metrika_core_dicts_upload import lib


def test_json_row_to_sql(json, sql):
    for json_row, sql_row in zip(json, sql):
        assert lib.json_row_to_sql(json_row, 'test') == sql_row
