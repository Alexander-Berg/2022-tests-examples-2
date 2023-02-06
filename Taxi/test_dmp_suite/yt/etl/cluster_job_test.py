import pytest

import dmp_suite.yt.etl as etl
import dmp_suite.yt.operation as op
from connection.yt import get_yt_client
from dmp_suite.yt import COMPRESSION_ATTRIBUTES
from dmp_suite.yt.table import Int, YTTable
from test_dmp_suite.yt import utils


class TestTable(YTTable):
    __compression_level__ = 'heaviest'

    column = Int()


test_table = utils.fixture_random_yt_table(TestTable)



@pytest.mark.slow
def test_cluster_job_performs_heaviest_compression(test_table):
    buffer_data = [
        dict(column=42)
    ]

    meta = etl.YTMeta(test_table)

    buffer_table = meta.buffer_path()
    rotation_table = meta.rotation_path()

    op.init_yt_table(
        buffer_table, meta.buffer_attributes(), replace=False
    )
    get_yt_client().write_table(
        buffer_table,
        buffer_data
    )
    job = etl.cluster_job(meta)
    job.table(buffer_table).put(rotation_table)
    job.run()

    attributes = get_yt_client().get(rotation_table + '/@')

    expected_attributes = COMPRESSION_ATTRIBUTES[meta.compression_level]
    for attribute, expected_value in expected_attributes.items():
        assert attributes[attribute] == expected_value
