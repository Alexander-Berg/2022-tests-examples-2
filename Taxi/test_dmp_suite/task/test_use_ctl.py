from argparse import Namespace
from datetime import datetime

from connection import ctl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.greenplum import GPTable
from dmp_suite.table import LayeredLayout
from dmp_suite.task.args import use_ctl, use_ctl_datetime, DatetimeArgPipe
from dmp_suite.yt import YTTable


class GPFooTable(GPTable):
    __layout__ = LayeredLayout(name='test', layer='test')


def test_use_ctl_gp_table():
    accessor = use_ctl(entity=GPFooTable, ctl_parameter=CTL_LAST_LOAD_DATE)
    assert accessor.get_value(Namespace(), None) is None

    accessor = use_ctl(entity=GPFooTable, ctl_parameter=CTL_LAST_LOAD_DATE, default=datetime(2020, 12, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 12, 1)

    ctl.get_ctl().gp.set_param(entity=GPFooTable, parameter=CTL_LAST_LOAD_DATE, value=datetime(2020, 11, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 11, 1)


def test_use_ctl_datetime_gp_table():
    accessor = use_ctl_datetime(entity=GPFooTable, ctl_parameter=CTL_LAST_LOAD_DATE)
    assert accessor.get_value(Namespace(), None) is None

    accessor = use_ctl_datetime(entity=GPFooTable, ctl_parameter=CTL_LAST_LOAD_DATE, default=datetime(2020, 12, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 12, 1)

    ctl.get_ctl().gp.set_param(entity=GPFooTable, parameter=CTL_LAST_LOAD_DATE, value=datetime(2020, 11, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 11, 1)


class YTFooTable(YTTable):
    __layout__ = LayeredLayout(name='test', layer='test')


def test_use_ctl_yt_table():
    accessor = use_ctl(entity=YTFooTable, ctl_parameter=CTL_LAST_LOAD_DATE)
    assert accessor.get_value(Namespace(), None) is None

    accessor = use_ctl(entity=YTFooTable, ctl_parameter=CTL_LAST_LOAD_DATE, default=datetime(2020, 12, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 12, 1)

    ctl.get_ctl().yt.set_param(entity=YTFooTable, parameter=CTL_LAST_LOAD_DATE, value=datetime(2020, 11, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 11, 1)


def test_use_ctl_datetime_yt_table():
    accessor = use_ctl_datetime(entity=YTFooTable, ctl_parameter=CTL_LAST_LOAD_DATE)
    assert accessor.get_value(Namespace(), None) is None

    accessor = use_ctl_datetime(entity=YTFooTable, ctl_parameter=CTL_LAST_LOAD_DATE, default=datetime(2020, 12, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 12, 1)

    ctl.get_ctl().yt.set_param(entity=YTFooTable, parameter=CTL_LAST_LOAD_DATE, value=datetime(2020, 11, 1))
    assert accessor.get_value(Namespace(), None) == datetime(2020, 11, 1)


def test_value_accessor_as_default():
    accessor = use_ctl_datetime(
        entity=YTFooTable,
        ctl_parameter=CTL_LAST_LOAD_DATE,
    )
    assert accessor.get_value(Namespace(), None) is None

    accessor = use_ctl_datetime(
        entity=YTFooTable,
        ctl_parameter=CTL_LAST_LOAD_DATE,
        default=DatetimeArgPipe(
            value_extractor=lambda *args, **kwargs: datetime(2021, 1, 1, 1, 1),
        ),
    )
    assert accessor.get_value(Namespace(), None) == datetime(2021, 1, 1, 1, 1)

    ctl.get_ctl().yt.set_param(
        entity=YTFooTable,
        parameter=CTL_LAST_LOAD_DATE,
        value=datetime(2021, 2, 2, 2, 2),
    )
    assert accessor.get_value(Namespace(), None) == datetime(2021, 2, 2, 2, 2)
