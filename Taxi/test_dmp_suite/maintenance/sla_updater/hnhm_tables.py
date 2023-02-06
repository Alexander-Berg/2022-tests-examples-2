from datetime import timedelta

from dmp_suite import yt, greenplum as gp
from dmp_suite.ctl import CTL_LAST_SYNC_DATE, CTL_LAST_LOAD_DATE
from dmp_suite.greenplum import YearPartitionScale
from dmp_suite.greenplum.hnhm import sla, HnhmEntity, HnhmLink, HnhmLinkElement
from dmp_suite.table import Sla
from test_dmp_suite.greenplum.utils import TestLayout


class TestGPTable(gp.GPTable):
    __layout__ = TestLayout('test_layout')
    __sla__ = Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=1), crit_lag=timedelta(seconds=2))


class TestYTTable(yt.YTTable):
    __layout__ = TestLayout('test_layout')
    __sla__ = [
        Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=1), crit_lag=timedelta(seconds=2)),
        Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=1), crit_lag=timedelta(seconds=2)),
    ]


class TestHnhmEntityTableTop(HnhmEntity):
    __layout__ = TestLayout('test_layout')
    __sla__ = [
        sla.attribute(
            'a', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=123), crit_lag=timedelta(seconds=321))
        ),
        sla.attributes(
            'b', 'c',
            sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=123), crit_lag=timedelta(seconds=321))
        ),
        sla.default(
            Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=12), crit_lag=timedelta(seconds=21)),
        ),
        sla.default(
            Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=666), crit_lag=timedelta(seconds=999)),
        )
    ]
    a = gp.String()
    b = gp.Int()
    c = gp.Datetime()

    __keys__ = [a]


class TestHnhmEntityTableBottom(HnhmEntity):
    __layout__ = TestLayout('test_layout')
    a = gp.String()
    b = gp.Int()
    c = gp.Datetime()

    __keys__ = [a]
    __sla__ = [
        sla.attribute(
            a, Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=123), crit_lag=timedelta(seconds=321))
        ),
        sla.attributes(
            b, c,
            sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=123), crit_lag=timedelta(seconds=321))
        ),
        sla.default(
            Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=12), crit_lag=timedelta(seconds=21)),
        ),
        sla.default(
            Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=666), crit_lag=timedelta(seconds=999)),
        )
    ]


class TestHnhmEntityTableAlias(HnhmEntity):
    # Table with aliases (ensure that we just ignore them)
    __layout__ = TestLayout('test_layout')
    a = gp.String(alias='b')
    b = gp.Int(alias='c')
    c = gp.Datetime(alias='aaaaaa!!!')

    __keys__ = [a]
    __sla__ = [
        sla.default(
            Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=666), crit_lag=timedelta(seconds=999)),
        ),
        sla.default(
            Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=12), crit_lag=timedelta(seconds=21)),
        ),
        sla.attributes(
            'b', 'c',
            sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=123), crit_lag=timedelta(seconds=321))
        ),
        sla.attribute(
            'a', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(seconds=123), crit_lag=timedelta(seconds=321))
        ),
    ]


class TestHnhmEntityWithPartitionKey(HnhmEntity):
    __layout__ = TestLayout('test_layout')
    __partition_scale__ = YearPartitionScale('c')
    a = gp.String()
    b = gp.Int()
    c = gp.Datetime()  # Для этого поля не существует таблицы в GP
    __keys__ = [a]
    __sla__ = [
        sla.default(Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1), crit_lag=timedelta(2))),
    ]


class TestHnhmLink(HnhmLink):
    # Используем обычный Sla для линков
    __sla__ = Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=1), crit_lag=timedelta(seconds=2))
    __layout__ = TestLayout('test_link_layout')

    a = HnhmLinkElement(entity=TestHnhmEntityTableTop())
    b = HnhmLinkElement(entity=TestHnhmEntityTableBottom())

    __keys__ = [a]
