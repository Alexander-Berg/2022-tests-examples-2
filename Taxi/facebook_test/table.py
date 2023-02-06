# coding: utf-8
from dmp_suite.yt import ETLTable, String, Int
from dmp_suite.table import OdsLayout
from media_etl.domain.source import mrkt


class Dst(ETLTable):

    __layout__ = OdsLayout('FB_test', domain=mrkt)
    campaign_name = String(comment='test1')
    cnt = Int(comment='test2')
