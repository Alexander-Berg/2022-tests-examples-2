import uuid

from dmp_suite import greenplum as gp
from dmp_suite.greenplum import GPTable
from dmp_suite.greenplum import hnhm
from dmp_suite.greenplum.table import \
    MonthPartitionScale as GPMonthPartitionScale, \
    PartitionList as GPPartitionList, Datetime as GPDatetime, Int as GPInt, \
    String as GPString, \
    ListPartitionItem as GPPartition
from dmp_suite.table import LayeredLayout
from dmp_suite.table import SummaryLayout, ChangeType, DdsLayout
from dmp_suite.yt import YTTable, MonthPartitionScale, Datetime, \
    DayPartitionScale

TEST_SERVICE_ETL = 'test'


class FooTable(YTTable):
    __layout__ = LayeredLayout(layer='bar', group='group', name='foo')


class MonthFooTable(YTTable):
    __layout__ = LayeredLayout(layer='bar', name='month_foo')
    __partition_scale__ = MonthPartitionScale('dttm')
    dttm = Datetime()


class DayFooTable(YTTable):
    __layout__ = LayeredLayout(layer='bar', name='day_foo')
    __partition_scale__ = DayPartitionScale('dttm')
    dttm = Datetime()


class GPMonthPartitionTable(GPTable):
    __layout__ = SummaryLayout('summary', 'test_' + uuid.uuid4().hex)
    __partition_scale__ = GPMonthPartitionScale('utc_dt', start='2012-03-01', end='2020-01-01')

    id = GPInt(key=True)
    utc_dt = GPDatetime()

    @classmethod
    def get_layout_prefix(cls):
        return 'test'


class GPListPartitionTable(GPTable):
    __layout__ = SummaryLayout('summary', 'test_' + uuid.uuid4().hex)
    __partition_scale__ = GPPartitionList(
        'scale',
        [
            GPPartition(
                name='daily',
                value='daily'
            ),
            GPPartition(
                name='weekly',
                value='weekly'
            )
        ]
    )

    id = GPInt(key=True)
    scale = GPString()

    @classmethod
    def get_layout_prefix(cls):
        return 'test'


class GPListAndMonthPartitionTable(GPTable):
    __layout__ = SummaryLayout('summary', 'test_' + uuid.uuid4().hex)
    __partition_scale__ = GPPartitionList(
        'scale',
        [
            GPPartition(
                name='daily',
                value='daily'
            ),
            GPPartition(
                name='weekly',
                value='weekly'
            )
        ],
        subpartition=GPMonthPartitionScale(
            'utc_dt',
            start='2012-03-01',
            end='2020-01-01',
            is_subpartition=True
        ),
    )

    id = GPInt(key=True)
    scale = GPString()
    utc_dt = GPDatetime()

    @classmethod
    def get_layout_prefix(cls):
        return 'test'


class GPHeapTable(GPTable):
    __layout__ = SummaryLayout('summary', 'test_' + uuid.uuid4().hex)
    id = GPInt(key=True)
    utc_dt = GPDatetime()

    @classmethod
    def get_layout_prefix(cls):
        return 'test'


class HnhmEntityTable(hnhm.HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='hnhm_group', prefix_key=TEST_SERVICE_ETL)

    eid = gp.Int(change_type=ChangeType.IGNORE)
    evalue = gp.String(change_type=ChangeType.NEW)
    edt = gp.Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class HnhmEntityTablePartition(hnhm.HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='hnhm_group_part', prefix_key=TEST_SERVICE_ETL)

    __partition_scale__ = gp.YearPartitionScale('edt', start='2018-01-01')

    eid = gp.Int()
    evalue = gp.String(change_type=ChangeType.UPDATE)
    edt = gp.Datetime()

    __keys__ = [eid]
