from operator import itemgetter

import pytest

import dmp_suite.yt.etl as etl
import dmp_suite.yt.operation as op
from connection.yt import get_yt_client
from dmp_suite.yt.table import Int, String, YTTable
from test_dmp_suite.yt import utils


class TestTable(YTTable):
    key_one = String(sort_key=True, sort_position=0)
    key_two = String(sort_key=True, sort_position=1)
    value = Int()


test_table = utils.fixture_random_yt_table(TestTable)


@pytest.mark.slow
def test_buffer_to_rotation(test_table):
    buffer_data = [
        dict(key_one='1', key_two='2', value=1),
        dict(key_one='1', key_two='1', value=2),
    ]

    meta = etl.YTMeta(test_table)

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=False
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        buffer_data,
    )
    etl.buffer_to_rotation(meta, merge=False)

    rotation_table = meta.rotation_path()
    result_data = list(get_yt_client().read_table(rotation_table))

    expected_data = sorted(buffer_data, key=itemgetter(*meta.sort_key_names()))
    assert result_data == expected_data
