import pytest
from unittest import TestCase

from dmp_suite.datetime_utils import Period
from dmp_suite.yt import (
    NotLayeredYtTable, NotLayeredYtLayout, Datetime, YearPartitionScale, MonthPartitionScale, ShortMonthPartitionScale,
    DayPartitionScale, YTMeta
)

import dmp_suite.yql as yql_utils


class Table(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test_path')
    partition_key = Datetime()


class YearPartitionTable(Table):
    __partition_scale__ = YearPartitionScale('partition_key')


class MonthPartitionTable(Table):
    __partition_scale__ = MonthPartitionScale('partition_key')


class ShortMonthPartitionTable(Table):
    __partition_scale__ = ShortMonthPartitionScale('partition_key')


class DayPartitionTable(Table):
    __partition_scale__ = DayPartitionScale('partition_key')


class PrepareYqlRangeArgsTest(TestCase):

    big_period = Period('2017-02-12 10:20:30', '2018-02-12 10:20:45')
    small_period = Period('2017-01-23 16:20:18', '2017-03-25 08:10:15')
    test_folder_path = '//dummy/test/test_path'

    def test_no_partition_table(self):
        meta = YTMeta(Table)

        self.assertRaises(
            ValueError,
            yql_utils.range_path_by_meta,
            meta=meta,
            period=self.small_period
        )
        self.assertRaises(
            ValueError,
            yql_utils.range_path_by_meta,
            meta=meta,
            period=self.big_period
        )

    def test_year_partition_table(self):
        meta = YTMeta(YearPartitionTable)

        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.small_period
            ),
            '`{}`, `2017-01-01`, `2017-01-01`'.format(self.test_folder_path)
        )
        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.big_period
            ),
            '`{}`, `2017-01-01`, `2018-01-01`'.format(self.test_folder_path)
        )

    def test_month_partition_table(self):
        meta = YTMeta(MonthPartitionTable)
        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.small_period
            ),
            '`{}`, `2017-01-01`, `2017-03-01`'.format(self.test_folder_path)
        )
        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.big_period
            ),
            '`{}`, `2017-02-01`, `2018-02-01`'.format(self.test_folder_path)
        )

    def test_short_month_partition_table(self):
        meta = YTMeta(ShortMonthPartitionTable)

        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.small_period
            ),
            '`{}`, `2017-01`, `2017-03`'.format(self.test_folder_path)
        )
        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.big_period
            ),
            '`{}`, `2017-02`, `2018-02`'.format(self.test_folder_path)
        )

    def test_day_partition_table(self):
        meta = YTMeta(DayPartitionTable)

        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.small_period
            ),
            '`{}`, `2017-01-23`, `2017-03-25`'.format(self.test_folder_path)
        )
        self.assertEqual(
            yql_utils.range_path_by_meta(
                meta=meta,
                period=self.big_period
            ),
            '`{}`, `2017-02-12`, `2018-02-12`'.format(self.test_folder_path)
        )


class QueryWithAttachmentsTest(TestCase):
    @pytest.mark.slow
    def test_python_script_attachment(self):
        from test_dmp_suite.yql import yql_udf_attachment_test_script
        from textwrap import dedent
        script_alias = 'yql_udf_attachment_test_script.py'

        first = 165
        second = 39
        test_query = (
            yql_utils.YqlSelect
            .from_string(
                dedent(
                    """\
                    $first = {first_argument};
                    $second = {second_argument};
                    
                    $script = FileContent('{script_alias}');
                    
                    $add = Python::add_function(
                        Callable<(Int64, Int64)->Int64>,
                        $script
                    );
                    
                    $subtract = Python::subtract_function(
                        Callable<(Int64, Int64)->Int64>,
                        $script
                    );
                    
                    select 
                        $add($first, $second) as sum_value,
                        $subtract($first, $second) as diff_value;
                    """
                )
            )
            .add_params(
                first_argument=first,
                second_argument=second,
                script_alias=script_alias
            )
            .attach_file(
                yql_utils.PythonScriptAttachment.from_module(
                    yql_udf_attachment_test_script,
                    alias=script_alias
                )
            )
        )
        result_record = test_query.get_one_data_dict()
        self.assertEqual(int(result_record['sum_value']), first + second)
        self.assertEqual(int(result_record['diff_value']), first - second)
