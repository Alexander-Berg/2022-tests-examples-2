from dmp_suite.greenplum import Int as GPInt, String as GPString, ExternalGPTable, GPTable
from dmp_suite.yt import NotLayeredYtTable, NotLayeredYtLayout, Int as YTInt, String as YTString
from test_dmp_suite.greenplum.utils import TestLayout
from test_dmp_suite.greenplum.utils import GreenplumTestTable, external_gp_layout


class YTSourceTable(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('test', 'test')

    id = YTInt()
    value = YTString()


class GPTargetTable(GPTable):
    __layout__ = TestLayout(name="example")

    id = GPInt()
    value = GPString()
    value_2 = GPString()
