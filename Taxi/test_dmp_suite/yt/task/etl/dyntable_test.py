from datetime import timedelta

import pytest

from connection.ctl import get_ctl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.datetime_utils import utcnow
from dmp_suite.task.execution import run_task
from dmp_suite.yt import YTTable, Int, Datetime, LayeredLayout, resolve_meta
from dmp_suite.yt.dyntable_operation.dynamic_table_loaders import GenericDataIncrement
from dmp_suite.yt.dyntable_operation.operations import select_rows
from dmp_suite.yt.task.dyntable import insert_unordered_increment


class Table(YTTable):
    __dynamic__ = True
    __layout__ = LayeredLayout(name='test', layer='test')
    __updated_dttm_field__ = 'etl_updated'

    a = Int(sort_key=True)
    b = Int()
    d = Datetime()
    etl_updated = Datetime()


@pytest.fixture
def rows():
    return [
        {
            'a': 1,
            'b': 2,
            'd': '2020-05-25 06:48:11'
        },
        {
            'a': 2,
            'b': 3,
            'd': '2020-05-25 06:48:11'
        },
        {
            'a': 4,
            'b': 5,
            'd': '2020-05-25 06:48:11'
        },
    ]


@pytest.mark.slow
def test_insert_unordered_increment(rows):

    now = utcnow()

    get_ctl().yt.set_param(Table, CTL_LAST_LOAD_DATE, now - timedelta(days=2, hours=2))

    task = insert_unordered_increment(
        'test_insert_unordered_increment',
        GenericDataIncrement(rows, now),
        Table,
    )

    run_task(task)

    saved_rows = list(map(lambda x: {'a': x['a'], 'b': x['b'], 'd': x['d']}, select_rows(resolve_meta(Table))))

    assert saved_rows == rows

    ctl_date = get_ctl().yt.get_param(Table, CTL_LAST_LOAD_DATE)

    assert ctl_date == now.replace(microsecond=0)
