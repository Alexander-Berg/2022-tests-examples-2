import pytest
from dmp_suite.yt.table import Date, Datetime, Int, MonthPartitionScale
import dmp_suite.yt.etl as etl
import dmp_suite.yt.operation as op
import dmp_suite.datetime_utils as dtu
from connection.yt import get_yt_client
from test_dmp_suite.yt import utils


class TestTable(etl.ETLTable):
    __unique_keys__ = True
    __partition_scale__ = MonthPartitionScale(partition_key='dt')

    dt = Date()
    dttm = Datetime(sort_key=True, sort_position=0)
    value = Int()


test_table = utils.fixture_random_yt_table(TestTable)


@pytest.mark.slow
def test_load_period_from_buffer(test_table):
    initial_data = [
        dict(dt='2017-03-04', dttm='2017-03-04 12:12:12', value=1),
        dict(dt='2017-03-07', dttm='2017-03-07 12:12:12', value=2),
    ]

    update_data = [
        dict(dt='2017-03-07', dttm='2017-03-07 02:02:02', value=3),
        dict(dt='2017-03-07', dttm='2017-03-07 00:00:00', value=4),
        dict(dt='2017-04-09', dttm='2017-04-09 16:16:16', value=5),
    ]

    meta = etl.YTMeta(test_table)

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=False
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        initial_data,
    )
    etl.load_period_from_buffer(
        test_table,
        period=dtu.Period('2017-03-04', '2017-03-07')
    )

    op.init_yt_table(
        meta.buffer_path(), meta.buffer_attributes(), replace=True
    )
    get_yt_client().write_table(
        meta.buffer_path(),
        update_data,
    )
    etl.load_period_from_buffer(
        meta,
        period=dtu.Period('2017-03-07', '2017-04-09')
    )

    first_partition = meta.with_partition('2017-03-01').target_path()
    second_partition = meta.with_partition('2017-04-01').target_path()
    result_data = (
        list(get_yt_client().read_table(first_partition)) +
        list(get_yt_client().read_table(second_partition))
    )

    assert len(result_data) == 4
    assert result_data[0]['dt'] == '2017-03-04'
    assert result_data[1]['dt'] == '2017-03-07'
    assert result_data[2]['dt'] == '2017-03-07'
    assert result_data[3]['dt'] == '2017-04-09'

    assert result_data[1]['dttm'] == '2017-03-07 00:00:00'
    assert result_data[1]['value'] == 4
    assert result_data[2]['dttm'] == '2017-03-07 02:02:02'
    assert result_data[2]['value'] == 3
    assert result_data[3]['dttm'] == '2017-04-09 16:16:16'
    assert result_data[3]['value'] == 5
