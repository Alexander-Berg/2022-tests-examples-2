import unittest
from enum import Enum

import pytest

from dmp_suite.yt.table import (
    Date, Datetime, Int, String, MonthPartitionScale, NotLayeredYtLayout
)
import dmp_suite.yt.etl as etl
import dmp_suite.yt.operation as op
from dmp_suite.yt import COMPRESSION_ATTRIBUTES
import dmp_suite.datetime_utils as dtu
from connection.yt import get_yt_client
from test_dmp_suite.yt.utils import random_yt_table


class IncrementType(Enum):
    PERIOD = 'period'
    PERIOD_FROM_PATH = 'period_from_path'
    KEY = 'key'


@pytest.mark.slow
class TestLoadIncrement(unittest.TestCase):
    partition = None
    initial_period = None
    update_period = None
    meta = None
    increment_type = None
    unique_buffer = False

    def setUp(self):
        if self.meta:
            return
        self.meta = etl.YTMeta(self.Table, self.partition)

        buffer_path = self.meta.buffer_path(unique=self.unique_buffer)

        op.init_yt_table(
            buffer_path, self.meta.buffer_attributes(), replace=False
        )
        get_yt_client().write_table(
            buffer_path,
            self.initial_data
        )

        if self.increment_type == IncrementType.PERIOD:
            etl.load_period_from_buffer(
                self.meta,
                period=self.initial_period,
            )
        elif self.increment_type == IncrementType.PERIOD_FROM_PATH:
            etl.load_period_from_path(
                buffer_path,
                self.meta,
                period=self.initial_period,
            )
        elif self.increment_type == IncrementType.KEY:
            etl.load_by_key_from_buffer(
                self.meta,
                partition_period=self.initial_period,
            )

        op.init_yt_table(
            buffer_path, self.meta.buffer_attributes(), replace=True
        )
        get_yt_client().write_table(
            buffer_path,
            self.update_data
        )

        if self.increment_type == IncrementType.PERIOD:
            etl.load_period_from_buffer(
                self.meta,
                period=self.update_period,
            )
        elif self.increment_type == IncrementType.PERIOD_FROM_PATH:
            etl.load_period_from_path(
                buffer_path,
                self.meta,
                period=self.update_period,
            )
        elif self.increment_type == IncrementType.KEY:
            etl.load_by_key_from_buffer(
                self.meta,
                partition_period=self.update_period,
            )

        self.table_data = list(get_yt_client().read_table(self.meta.target_path()))
        self.table_attributes = get_yt_client().get(self.meta.target_path() + '/@')

        op.remove_yt_table(buffer_path)

    def assertCorrectCompressionAttributes(self):
        expected_attributes = COMPRESSION_ATTRIBUTES[self.meta.compression_level]
        for attribute, expected_value in expected_attributes.items():
            self.assertEqual(self.table_attributes[attribute], expected_value)


class TestByUniqueKeys(TestLoadIncrement):

    @random_yt_table
    class Table(etl.ETLTable):
        __unique_keys__ = True
        __compression_level__ = 'heaviest'

        key_one = String(sort_key=True, sort_position=0)
        key_two = String(sort_key=True, sort_position=1)
        value = Int()

    initial_data = [
        dict(key_one='1', key_two='1', value=1),
        dict(key_one='1', key_two='2', value=2),
    ]
    update_data = [
        dict(key_one='1', key_two='2', value=3),
    ]
    increment_type = IncrementType.KEY

    def test_correct_data(self):
        assert len(self.table_data) == 2
        result = {(rec['key_one'], rec['key_two']): rec['value']
                  for rec in self.table_data}

        assert result[('1', '1')] == 1
        assert result[('1', '2')] == 3

        self.assertCorrectCompressionAttributes()


class TestByUniqueKeysIntoPartition(TestLoadIncrement):

    @random_yt_table
    class Table(etl.ETLTable):
        __unique_keys__ = True
        __partition_scale__ = MonthPartitionScale(partition_key='dt')

        dt = Date()
        key_one = String(sort_key=True, sort_position=0)
        key_two = String(sort_key=True, sort_position=1)
        value = Int()

    partition = '2018-09-01'
    initial_data = [
        dict(dt='2018-09-02', key_one='1', key_two='1', value=1),
        dict(dt='2018-09-03', key_one='1', key_two='2', value=2),
    ]
    update_data = [
        dict(dt='2018-09-03', key_one='1', key_two='2', value=3),
    ]
    increment_type = IncrementType.KEY
    initial_period = dtu.date_period('2018-09-01', '2018-09-30')
    update_period = dtu.date_period('2018-09-01', '2018-09-30')

    def test_correct_data(self):
        assert len(self.table_data) == 2
        result = {(rec['key_one'], rec['key_two']): rec['value']
                  for rec in self.table_data}

        assert result[('1', '1')] == 1
        assert result[('1', '2')] == 3


class TestByUniqueKeysIntoNamelessEntity(TestLoadIncrement):

    @random_yt_table
    class Table(etl.ETLTable):
        __unique_keys__ = True

        key_one = String(sort_key=True, sort_position=0)
        key_two = String(sort_key=True, sort_position=1)
        value = Int()

    initial_data = [
        dict(key_one='1', key_two='1', value=1),
        dict(key_one='1', key_two='2', value=2),
    ]
    update_data = [
        dict(key_one='1', key_two='2', value=3),
    ]
    increment_type = IncrementType.KEY

    def test_correct_data(self):
        assert len(self.table_data) == 2
        result = {(rec['key_one'], rec['key_two']): rec['value']
                  for rec in self.table_data}

        assert result[('1', '1')] == 1
        assert result[('1', '2')] == 3


class TestByPartitionKey(TestLoadIncrement):

    @random_yt_table
    class Table(etl.ETLTable):
        __unique_keys__ = True
        __layout__ = NotLayeredYtLayout(folder='tests', name='load_increment_by_partition_key', prefix_key='test')
        __partition_scale__ = MonthPartitionScale(partition_key='dt')

        dt = Date()
        dttm = Datetime(sort_key=True, sort_position=0)
        value = Int()

    partition = '2017-03-01'
    initial_data = [
        dict(dt='2017-03-04', dttm='2017-03-04 12:12:12', value=1),
        dict(dt='2017-03-07', dttm='2017-03-07 12:12:12', value=2),
    ]
    update_data = [
        dict(dt='2017-03-07', dttm='2017-03-07 02:02:02', value=3),
        dict(dt='2017-03-07', dttm='2017-03-07 00:00:00', value=4),
    ]
    increment_type = IncrementType.PERIOD
    initial_period = dtu.Period('2017-03-04', '2017-03-07')
    update_period = dtu.Period('2017-03-07', '2017-03-07')

    def test_correct_data(self):
        assert len(self.table_data) == 3
        assert self.table_data[0]['dt'] == '2017-03-04'
        assert self.table_data[1]['dt'] == '2017-03-07'
        assert self.table_data[2]['dt'] == '2017-03-07'

        assert self.table_data[1]['dttm'] == '2017-03-07 00:00:00'
        assert self.table_data[1]['value'] == 4
        assert self.table_data[2]['dttm'] == '2017-03-07 02:02:02'
        assert self.table_data[2]['value'] == 3

    def test_correct_metadata(self):
        self.assertCorrectCompressionAttributes()


class TestByPartitionKeyFromPath(TestByPartitionKey):
    increment_type = IncrementType.PERIOD_FROM_PATH
    unique_buffer = True


class TestByPartitionKeyWholePartition(TestLoadIncrement):

    @random_yt_table
    class Table(etl.ETLTable):
        __unique_keys__ = True
        __partition_scale__ = MonthPartitionScale(partition_key='dt')

        dt = Date()
        dttm = Datetime(sort_key=True, sort_position=0)
        value = Int()

    partition = '2017-03-01'
    initial_data = [
        dict(dt='2017-03-04', dttm='2017-03-04 12:12:12', value=1),
    ]
    update_data = [
        dict(dt='2017-03-05', dttm='2017-03-04 12:12:12', value=2),
    ]
    increment_type = IncrementType.PERIOD
    initial_period = update_period = dtu.Period(
        dtu.get_start_of_month('2017-03-01'),
        dtu.get_end_of_month('2017-03-01')
    )

    def test_correct_data(self):
        assert len(self.table_data) == 1
        assert self.table_data[0]['dt'] == '2017-03-05'
        assert self.table_data[0]['value'] == 2


class TestByPartitionKeyWholePartitionFromPath(
    TestByPartitionKeyWholePartition,
):
    increment_type = IncrementType.PERIOD_FROM_PATH
    unique_buffer = True


class TestByPartitionKeyIntoNamelessEntity(TestLoadIncrement):

    @random_yt_table
    class Table(etl.ETLTable):
        __unique_keys__ = True
        __partition_scale__ = MonthPartitionScale(partition_key='dt')

        dt = Date()
        dttm = Datetime(sort_key=True, sort_position=0)
        value = Int()

    partition = '2017-03-01'
    initial_data = [
        dict(dt='2017-03-04', dttm='2017-03-04 12:12:12', value=1),
        dict(dt='2017-03-07', dttm='2017-03-07 12:12:12', value=2),
    ]
    update_data = [
        dict(dt='2017-03-07', dttm='2017-03-07 02:02:02', value=3),
        dict(dt='2017-03-07', dttm='2017-03-07 00:00:00', value=4),
    ]
    increment_type = IncrementType.PERIOD
    initial_period = dtu.Period('2017-03-04', '2017-03-07')
    update_period = dtu.Period('2017-03-07', '2017-03-07')

    def test_correct_data(self):
        assert len(self.table_data) == 3
        assert self.table_data[0]['dt'] == '2017-03-04'
        assert self.table_data[1]['dt'] == '2017-03-07'
        assert self.table_data[2]['dt'] == '2017-03-07'

        assert self.table_data[1]['dttm'] == '2017-03-07 00:00:00'
        assert self.table_data[1]['value'] == 4
        assert self.table_data[2]['dttm'] == '2017-03-07 02:02:02'
        assert self.table_data[2]['value'] == 3


class TestByPartitionKeyIntoNamelessEntityByPath(
    TestByPartitionKeyIntoNamelessEntity,
):
    increment_type = IncrementType.PERIOD_FROM_PATH
    unique_buffer = True
