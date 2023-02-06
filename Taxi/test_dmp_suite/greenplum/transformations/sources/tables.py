from dmp_suite.greenplum import Int as GPInt, String as GPString, GPTable
from dmp_suite.yt import NotLayeredYtTable, NotLayeredYtLayout, Int as YTInt, String as YTString
from test_dmp_suite.greenplum.utils import TestLayout


class YTSourceTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test')

    id = YTInt()
    value = YTString()


class GPTargetTable(GPTable):
    __layout__ = TestLayout(name='test')

    id = GPInt()
    value = GPString()
    value_2 = GPString()
