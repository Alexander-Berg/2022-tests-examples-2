# coding: utf-8
from dmp_suite.yt import HistTable, Int
from dmp_suite.table import ChangeType
from test_dmp_suite.yt.utils import random_yt_table


@random_yt_table
class BaseTestTable(HistTable):
    a = Int(sort_key=True, sort_position=1)
    b = Int(change_type=ChangeType.NEW)
    c = Int(change_type=ChangeType.UPDATE)
    d = Int(change_type=ChangeType.IGNORE)