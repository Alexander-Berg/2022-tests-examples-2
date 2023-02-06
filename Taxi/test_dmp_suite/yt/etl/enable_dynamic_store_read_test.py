import pytest
from dmp_suite.yt import YTTable, String, YTMeta, operation as op
from test_dmp_suite.yt import utils


class TestTableWithEnabled(YTTable):
    __dynamic__ = True
    __enable_dynamic_store_read__ = True
    dummy = String()


class TestTableWithDefault(YTTable):
    __dynamic__ = True
    dummy = String()


table_with_enabled = utils.fixture_random_yt_table(TestTableWithEnabled)
table_with_default = utils.fixture_random_yt_table(TestTableWithDefault)


def _test_enable_dynamic_store_read(table, value):
    meta = YTMeta(table)
    op.init_yt_table(meta.target_path(), meta.attributes(), replace=True)
    assert op.get_yt_attr(meta, 'enable_dynamic_store_read') == value
    op.init_yt_table(meta.rotation_path(), meta.rotation_attributes(), replace=True)
    assert op.get_yt_attr(meta, 'enable_dynamic_store_read') == value


@pytest.mark.slow
def test_table_with_enabled(table_with_enabled):
    _test_enable_dynamic_store_read(table_with_enabled, True)


@pytest.mark.slow
def test_table_with_default(table_with_default):
    _test_enable_dynamic_store_read(table_with_default, False)
