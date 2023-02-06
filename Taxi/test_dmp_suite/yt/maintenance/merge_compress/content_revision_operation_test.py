import pytest

import dmp_suite.yt.operation as op
from dmp_suite.yt.maintenance.merge_compress.content_revision_operation import DMP_MERGE_CONTENT_REVISION
from dmp_suite.yt.maintenance.merge_compress.content_revision_operation import (
    get_dmp_content_revision, get_content_revision
)
from dmp_suite.yt import YTTable, YTMeta, etl
from test_dmp_suite.yt import utils
from .helpers import is_merge_required_by_attrs


class TestTable(YTTable):
    pass


test_table = utils.fixture_random_yt_table(TestTable)


@pytest.mark.slow
def test_set_get_dmp_content_revision(test_table):
    meta = YTMeta(test_table)
    etl.init_target_table(meta)

    op.set_yt_attr(meta.target_path() + '/@' + DMP_MERGE_CONTENT_REVISION, 123456789)
    assert get_dmp_content_revision(meta) == 123456789


@pytest.mark.slow
def test_get_content_revision(test_table):
    meta = YTMeta(test_table)
    etl.init_target_table(meta)

    assert isinstance(get_content_revision(meta), int)


@pytest.mark.slow
def test_is_merge_required(test_table):
    meta = YTMeta(test_table)
    etl.init_target_table(meta)

    # Если нет атрибута, то нужен мерж
    assert is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))

    # Если ревизии не совпадают, то нужен мерж
    op.set_yt_attr(meta.target_path() + '/@' + DMP_MERGE_CONTENT_REVISION, get_content_revision(meta) - 1)
    assert is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))

    # Если ревизии совпадают, то мерж не нужен
    op.set_yt_attr(meta.target_path() + '/@' + DMP_MERGE_CONTENT_REVISION, get_content_revision(meta))
    assert not is_merge_required_by_attrs(get_dmp_content_revision(meta), get_content_revision(meta))
