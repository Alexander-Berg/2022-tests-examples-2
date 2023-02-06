import typing

import pytest

_DOC_PG_1 = {
    'key_bar': 1,
    'key_foo': 'key_pg_1',
    'main_data': {
        'updated_at': '2021-03-21T12:01:00+00:00',
        'value': 'pg_value_1',
    },
    'second_data': {'second_value': 'pg_second_value_1'},
}
_DOC_PG_2 = {
    'key_bar': 2,
    'key_foo': 'key_pg_2',
    'main_data': {
        'updated_at': '2021-03-21T12:02:00+00:00',
        'value': 'pg_value_2',
    },
}
_DOC_YT_1 = {
    'key_bar': 2,
    'key_foo': 'key_yt_1',
    'main_data': {
        'updated_at': '2021-03-15T14:48:34.749324+00:00',
        'value': 'value_2',
    },
    'second_data': {'second_value': 'second_value_2'},
}
_DOC_YT_2 = {
    'key_bar': 3,
    'key_foo': 'key_yt_2',
    'main_data': {
        'updated_at': '2021-03-15T14:40:30+00:00',
        'value': 'value_3',
    },
}
_DOC_YT_3_IF_SKIP_PG = {
    'key_bar': 1000,
    'key_foo': 'key_pg_1',
    'main_data': {
        'updated_at': '2021-03-10T12:00:00+00:00',
        'value': 'outdated',
    },
}


class Options(typing.NamedTuple):
    skip_pg: bool = False
    skip_yt: bool = False
    dummy_yt: bool = False


def _make_expected_log_stats(stats=None, *, dummy_stats=None, skipped=None):
    return {
        'stats': stats or {},
        'skipped': skipped or [],
        'dummy_stats': dummy_stats or {},
    }


@pytest.mark.yt(dyn_table_data=['yt_data.yaml'])
@pytest.mark.pgsql('basic_sample_db', files=['pg_data.sql'])
@pytest.mark.parametrize(
    'db_query,options,expected_items,expected_log_stats',
    [
        (
            [{'key_foo': 'key_pg_1'}],
            Options(),
            [_DOC_PG_1],
            _make_expected_log_stats({'pg': 1}),
        ),
        (
            [{'key_foo': 'key_pg_1'}, {'key_foo': 'key_pg_2'}],
            Options(),
            [_DOC_PG_1, _DOC_PG_2],
            _make_expected_log_stats({'pg': 2}),
        ),
        (
            [{'key_foo': 'key_pg_1'}, {'key_foo': 'key_yt_1'}],
            Options(),
            [_DOC_PG_1, _DOC_YT_1],
            _make_expected_log_stats({'pg': 1, 'yt': 1}),
        ),
        (
            [{'key_foo': 'key_pg_1'}, {'key_foo': 'key_yt_1'}],
            Options(skip_pg=True),
            [_DOC_YT_3_IF_SKIP_PG, _DOC_YT_1],
            _make_expected_log_stats({'yt': 2}, skipped=['pg']),
        ),
        (
            [{'key_foo': 'key_yt_1'}, {'key_foo': 'key_yt_2'}],
            Options(),
            [_DOC_YT_1, _DOC_YT_2],
            _make_expected_log_stats({'pg': 0, 'yt': 2}),
        ),
        (
            [
                {'key_foo': 'key_pg_1'},
                {'key_foo': 'key_pg_2'},
                {'key_foo': 'key_yt_1'},
                {'key_foo': 'key_yt_2'},
                {'key_foo': 'key_not_found'},
            ],
            Options(),
            [_DOC_PG_1, _DOC_PG_2, _DOC_YT_1, _DOC_YT_2],
            _make_expected_log_stats({'pg': 2, 'yt': 2}),
        ),
        (
            [{'key_foo': 'key_not_found'}],
            Options(),
            [],
            _make_expected_log_stats({'pg': 0, 'yt': 0}),
        ),
        (
            [{'key_foo': 'key_pg_1'}, {'key_foo': 'key_yt_1'}],
            Options(skip_yt=True),
            [_DOC_PG_1],
            _make_expected_log_stats({'pg': 1}, skipped=['yt']),
        ),
        (
            [{'key_foo': 'key_pg_1'}, {'key_foo': 'key_yt_1'}],
            Options(skip_yt=True, dummy_yt=True),
            [_DOC_PG_1],
            _make_expected_log_stats(
                {'pg': 1}, skipped=['yt'], dummy_stats={'yt': 1},
            ),
        ),
        (
            [{'key_foo': 'key_yt_1'}],
            Options(skip_yt=True, dummy_yt=True),
            [],
            _make_expected_log_stats(
                {'pg': 0}, skipped=['yt'], dummy_stats={'yt': 1},
            ),
        ),
    ],
)
async def test_retrieve_many(
        taxi_userver_db_adapter_sample,
        testpoint,
        yt_apply,
        db_query,
        options,
        expected_items,
        expected_log_stats,
):
    @testpoint('db-adapter_log-stats')
    def log_stats(data):
        pass

    response = await taxi_userver_db_adapter_sample.post(
        '/pg-yt/retrieve-many/primary-key',
        json={'items': db_query, **options._asdict()},
    )
    assert response.status_code == 200
    assert response.json() == {'items': expected_items}

    assert log_stats.times_called == 1
    assert log_stats.next_call()['data'] == expected_log_stats
