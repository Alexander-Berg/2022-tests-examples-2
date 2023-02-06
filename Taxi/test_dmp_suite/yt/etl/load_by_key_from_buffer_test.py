import pytest
from dmp_suite.yt.table import Date, Int, String, MonthPartitionScale
import dmp_suite.yt.etl as etl
import dmp_suite.yt.operation as op
import dmp_suite.datetime_utils as dtu
from connection.yt import get_yt_client
from test_dmp_suite.yt import utils


class TestTable(etl.ETLTable):
    __unique_keys__ = True
    __partition_scale__ = MonthPartitionScale(partition_key='dt')

    dt = Date()
    key_one = String(sort_key=True, sort_position=0)
    key_two = String(sort_key=True, sort_position=1)
    value = Int()


test_table = utils.fixture_random_yt_table(TestTable)


@pytest.mark.slow
def test_load_by_key_from_buffer(test_table):
    initial_data = [
        dict(dt='2018-09-30', key_one='1', key_two='1', value=1),
        dict(dt='2018-10-02', key_one='1', key_two='2', value=2),
    ]

    update_data = [
        dict(dt='2018-10-02', key_one='1', key_two='2', value=3),
    ]

    meta = etl.YTMeta(test_table)

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=False
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        initial_data,
    )
    etl.load_by_key_from_buffer(
        test_table, partition_period=dtu.Period('2018-09-30', '2018-10-02')
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        update_data,
    )
    etl.load_by_key_from_buffer(
        meta, partition_period=dtu.Period('2018-10-02', '2018-10-02')
    )

    first_partition = meta.with_partition('2018-09-01').target_path()
    second_partition = meta.with_partition('2018-10-01').target_path()
    result_data = (
        list(get_yt_client().read_table(first_partition)) +
        list(get_yt_client().read_table(second_partition))
    )

    assert len(result_data) == 2
    result = {(rec['key_one'], rec['key_two']): rec['value'] for rec in result_data}

    assert result[('1', '1')] == 1
    assert result[('1', '2')] == 3
