import pytest
from qb2.api.v1 import extractors as qe

import dmp_suite.yt.etl as etl
import dmp_suite.yt.operation as op
from connection.yt import get_yt_client
from dmp_suite.yt.table import String, YTTable
from test_dmp_suite.yt import utils


class TestTable(YTTable):
    column_one = String()
    column_two = String()


test_table = utils.fixture_random_yt_table(TestTable)



@pytest.mark.slow
def test_enrich(test_table):
    initial_data = [
        dict(column_one='1', column_two=None),
        dict(column_one='2', column_two=None),
    ]

    class MyEnricher(object):
        def transform(self, stream):
            return stream \
                .project('column_one',
                         qe.custom('column_two', lambda column_one: column_one * 2))

    meta = etl.YTMeta(test_table)

    op.init_yt_table(
        meta.buffer_path(), meta.attributes(), replace=False
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        initial_data
    )

    etl.enrich(test_table, [MyEnricher()])
    result_data = list(get_yt_client().read_table(meta.target_path()))

    expected_data = [
        dict(column_one='1', column_two='11'),
        dict(column_one='2', column_two='22'),
    ]
    assert result_data == expected_data
