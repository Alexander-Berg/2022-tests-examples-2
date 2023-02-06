import datetime
import typing as tp

import pytest

from replication.sources.postgres import core
from replication.sources.postgres.core import query_util

_TEST_LEFT_BOUND = datetime.datetime(2019, 1, 1)

_MIN_REPLICATE_BY = (
    'SELECT id FROM sequence.table {extra_condition} '
    'ORDER BY id ASC LIMIT 1'
)
_MAX_REPLICATE_BY = (
    'SELECT id FROM sequence.table {extra_condition} '
    'ORDER BY id DESC LIMIT 1'
)


@pytest.mark.parametrize(
    'use_aiopg,min_replicate_by_query,expected',
    (
        [
            True,
            None,
            r'SELECT MIN({field}) as {field} FROM {table} '
            r'WHERE {field} > %s',
        ],
        [
            False,
            None,
            r'SELECT MIN({field}) as {field} FROM {table} '
            r'WHERE {field} > $1',
        ],
        [
            True,
            _MIN_REPLICATE_BY,
            _MIN_REPLICATE_BY.format(extra_condition='WHERE {field} > %s'),
        ],
        [
            False,
            _MIN_REPLICATE_BY,
            _MIN_REPLICATE_BY.format(extra_condition='WHERE {field} > $1'),
        ],
    ),
)
def test_next_value_query_builder(use_aiopg, min_replicate_by_query, expected):
    assert expected == query_util.get_next_replicate_by_template(
        use_aiopg=use_aiopg,
        min_replicate_by_query=min_replicate_by_query,
        replicate_by_has_conditions=False,
    )


@pytest.mark.parametrize(
    'ascending, min_replicate_by_query, max_replicate_by_query, expected',
    (
        [False, None, None, core.templates.MAX_VALUE],
        [True, None, None, core.templates.MIN_VALUE],
        [
            False,
            _MIN_REPLICATE_BY,
            _MAX_REPLICATE_BY,
            _MAX_REPLICATE_BY.format(extra_condition=''),
        ],
        [
            True,
            _MIN_REPLICATE_BY,
            _MAX_REPLICATE_BY,
            _MIN_REPLICATE_BY.format(extra_condition=''),
        ],
    ),
)
def test_replicate_by_builder(
        ascending, min_replicate_by_query, max_replicate_by_query, expected,
):
    assert expected == query_util.get_replicate_by_template(
        ascending=ascending,
        min_replicate_by_query=min_replicate_by_query,
        max_replicate_by_query=max_replicate_by_query,
    )


# pylint: disable=protected-access
raw_select_cls: tp.Type[core.RawSelect] = core.RawSelect


# noinspection SqlDialectInspection
@pytest.mark.parametrize(
    'use_aiopg, raw_select, exclude_left, left_bound, expected',
    (
        [
            True,
            None,
            False,
            _TEST_LEFT_BOUND,
            'SELECT * FROM {table} WHERE {field} >= %s AND {field} <= %s',
        ],
        [
            False,
            None,
            False,
            None,
            'SELECT * FROM {table} WHERE {field} <= $1',
        ],
        [
            False,
            raw_select_cls(
                data=r'SELECT *, (subqery) FROM test_table',
                data_query_has_conditions=False,
            ),
            True,
            _TEST_LEFT_BOUND,
            'SELECT *, (subqery) FROM test_table '
            'WHERE {field} > $1 AND {field} <= $2',
        ],
        [
            False,
            raw_select_cls(
                data=r'SELECT *, (subqery) FROM test_table WHERE condition',
                data_query_has_conditions=True,
            ),
            True,
            _TEST_LEFT_BOUND,
            'SELECT *, (subqery) FROM test_table '
            'WHERE condition AND {field} > $1 AND {field} <= $2',
        ],
        [
            False,
            raw_select_cls(
                data=r'SELECT *, (subqery) FROM test_table',
                data_query_has_conditions=False,
            ),
            False,
            None,
            'SELECT *, (subqery) FROM test_table WHERE {field} <= $1',
        ],
        [
            False,
            raw_select_cls(
                data=r'SELECT *, (subqery) FROM test_table WHERE condition',
                data_query_has_conditions=True,
            ),
            False,
            None,
            'SELECT *, (subqery) FROM test_table '
            'WHERE condition AND {field} <= $1',
        ],
    ),
)
def test_bounds_query_builder(
        use_aiopg, raw_select, exclude_left, left_bound, expected,
):
    assert expected == query_util.get_bounds_template(
        use_aiopg=use_aiopg,
        raw_select=raw_select,
        exclude_left=exclude_left,
        left_bound=left_bound,
    )
