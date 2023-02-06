# pylint: disable=protected-access

import datetime

import pytest

from mia.crontasks import filters
from mia.crontasks import mia_searcher
from mia.crontasks import period
from test_mia.cron import yt_dummy


@pytest.mark.parametrize(
    'queries, month_tables, expected',
    [
        (
            {
                'id_1': filters.ExactMatchFilter('a', 'value_1'),
                'id_2': filters.ExactMatchFilter('b', 'value_2'),
            },
            ['2019-07', '2019-08', '2019-09', '2019-10'],
            {
                'found': {
                    'id_1': [
                        {
                            'id': '1',
                            'a': 'value_1',
                            'b': 'value_2',
                            'requests_matched': ['id_1', 'id_2'],
                        },
                        {
                            'id': '5',
                            'a': 'value_1',
                            'b': 'value_2',
                            'requests_matched': ['id_1', 'id_2'],
                        },
                        {
                            'id': '7',
                            'a': 'value_1',
                            'b': 'value_1',
                            'requests_matched': ['id_1'],
                        },
                    ],
                    'id_2': [
                        {
                            'id': '1',
                            'a': 'value_1',
                            'b': 'value_2',
                            'requests_matched': ['id_1', 'id_2'],
                        },
                        {
                            'id': '4',
                            'a': 'value_3',
                            'b': 'value_2',
                            'requests_matched': ['id_2'],
                        },
                        {
                            'id': '5',
                            'a': 'value_1',
                            'b': 'value_2',
                            'requests_matched': ['id_1', 'id_2'],
                        },
                    ],
                },
                'too_much': {},
                'not_found': [],
            },
        ),
        (
            {'id_1': filters.ExactMatchFilter('field', 'test_value_4')},
            ['2019-07', '2019-08', '2019-09', '2019-10'],
            {'found': {}, 'too_much': {}, 'not_found': ['id_1']},
        ),
    ],
)
async def test_search(load_json, queries, month_tables, expected):
    max_records_count = 1000
    searcher = mia_searcher.MiaSearcher(
        yt_dummy.YtWrapperDummy(load_json('yt_tables.json')),
        'private/mongo/struct/order_proc_mia/orders_monthly/{}',
        max_records_count,
    )
    search_operation = await searcher.run_search_operation(
        queries, month_tables,
    )
    result = await searcher.await_search_operation(
        search_operation, queries.keys(),
    )
    assert result == mia_searcher.MiaSearchResult(**expected)


@pytest.mark.config(MIA_TAXI_MAX_RESULTS_COUNT=3)
async def test_search_too_much():
    count_of_records = 3 + 1
    expected = {
        'found': {},
        'too_much': {'id_1': count_of_records},
        'not_found': [],
    }
    queries = {'id_1': filters.ExactMatchFilter('a', 'value_1')}
    month_tables = ['2019-10']

    table_name = 'private/mongo/struct/order_proc_mia/orders_monthly/2019-10'
    tables = {table_name: []}

    searcher = mia_searcher.MiaSearcher(
        yt_dummy.YtWrapperDummy(tables),
        'private/mongo/struct/order_proc_mia/orders_monthly/{}',
        count_of_records - 1,
    )
    searcher.yt_.yt_tables[table_name].extend(
        [{'a': 'value_1'}] * count_of_records,
    )

    search_operation = await searcher.run_search_operation(
        queries, month_tables,
    )
    result = await searcher.await_search_operation(
        search_operation, queries.keys(),
    )
    assert result == mia_searcher.MiaSearchResult(**expected)


@pytest.mark.parametrize(
    'period_, expected',
    [
        (
            period.Period(
                datetime.datetime(2019, 8, 2, 12, 56, 32, 391),
                datetime.datetime(2019, 9, 1, 9, 0, 0, 0),
            ),
            ['2019-08', '2019-09'],
        ),
        (
            period.Period(
                datetime.datetime(2019, 6, 5, 12, 56, 32, 391),
                datetime.datetime(2019, 9, 15, 9, 0, 0, 0),
            ),
            ['2019-06', '2019-07', '2019-08', '2019-09'],
        ),
        (
            period.Period(
                datetime.datetime(2019, 10, 2, 12, 56, 32, 391),
                datetime.datetime(2020, 1, 1, 1, 0, 0, 1),
            ),
            ['2019-10', '2019-11', '2019-12', '2020-01'],
        ),
        (
            period.Period(
                datetime.datetime(2019, 11, 2, 12, 56, 32, 391),
                datetime.datetime(2020, 2, 12, 9, 0, 0, 0),
            ),
            ['2019-11', '2019-12', '2020-01', '2020-02'],
        ),
    ],
)
async def test_month_tables(period_, expected):
    assert mia_searcher.MiaSearcher.month_tables(period_) == expected
