from test_dmp_suite.greenplum import utils as gp_utils
from dmp_suite import greenplum as gp
from dmp_suite import yt as yt_suite
from test_dmp_suite.yt import utils as yt_test_utils


"""
Отдельный файл с табличками, чтобы nile не тянул всё подряд на кластер
"""


@yt_test_utils.random_yt_table
class YTSourceTable(yt_suite.NotLayeredYtTable):
    __layout__ = yt_suite.NotLayeredYtLayout('test', 'test', prefix_key='test')
    __unique_keys__ = True
    __partition_scale__ = yt_suite.ShortMonthPartitionScale(
        'a_utc_created_dttm'
    )
    __dynamic__ = True

    a_utc_created_dttm = yt_suite.Datetime(sort_key=True)
    id = yt_suite.Int(sort_key=True)
    doc = yt_suite.Any()


class GpStgTargetTable(gp.GPTable):
    __layout__ = gp_utils.TestLayout(name='test')

    a_utc_created_dttm = gp.Datetime(key=True)
    id = gp.Int(key=True)
    value = gp.String()


class GpOdsTargetTable(gp.GPTable):
    __layout__ = gp_utils.TestLayout(name='test')

    id = gp.Int(key=True)
    a_utc_created_dttm = gp.Datetime()
    value = gp.String()
