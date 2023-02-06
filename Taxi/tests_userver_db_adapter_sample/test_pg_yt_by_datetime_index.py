import typing

import pytest


class AdapterRequest(typing.NamedTuple):
    key_foo: str
    right_threshold: typing.Optional[str] = None
    limit: typing.Optional[int] = None


@pytest.mark.now('2021-03-21T12:01:00')
@pytest.mark.yt(dyn_table_data=['yt_data.yaml'])
@pytest.mark.pgsql('basic_sample_db', files=['pg_data.sql'])
@pytest.mark.parametrize(
    'db_query,expected_items',
    [
        (
            AdapterRequest(
                key_foo='key_common',
                right_threshold='2021-03-21T18:01:00+00:00',
                limit=5,
            ),
            [
                {
                    'key_bar': 0,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-21T12:01:00+00:00',
                        'value': 'pg_value_1',
                    },
                    'second_data': {'second_value': 'pg_second_value_1'},
                },
                {
                    'key_bar': 1,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-21T12:02:00+00:00',
                        'value': 'pg_value_2',
                    },
                },
                {
                    'key_bar': 2,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:48:34.749324+00:00',
                        'value': 'value_2',
                    },
                    'second_data': {'second_value': 'second_value_2'},
                },
                {
                    'key_bar': 3,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'value_3',
                    },
                },
            ],
        ),
        (
            AdapterRequest(
                key_foo='key_common',
                right_threshold='2021-03-21T15:01:30+00:00',
                limit=5,
            ),
            [
                {
                    'key_bar': 0,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-21T12:01:00+00:00',
                        'value': 'pg_value_1',
                    },
                    'second_data': {'second_value': 'pg_second_value_1'},
                },
                {
                    'key_bar': 1,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'cold_yt_value',
                    },
                },
                {
                    'key_bar': 2,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:48:34.749324+00:00',
                        'value': 'value_2',
                    },
                    'second_data': {'second_value': 'second_value_2'},
                },
                {
                    'key_bar': 3,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'value_3',
                    },
                },
            ],
        ),
        (
            AdapterRequest(
                key_foo='key_common',
                right_threshold='2021-03-15T14:40:50+00:00',
                limit=5,
            ),
            [
                {
                    'key_bar': 1,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'cold_yt_value',
                    },
                },
                {
                    'key_bar': 3,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'value_3',
                    },
                },
            ],
        ),
        (
            AdapterRequest(
                key_foo='key_common',
                right_threshold='2021-03-21T15:01:30+00:00',
                limit=1,
            ),
            [
                {
                    'key_bar': 0,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-21T12:01:00+00:00',
                        'value': 'pg_value_1',
                    },
                    'second_data': {'second_value': 'pg_second_value_1'},
                },
            ],
        ),
        (
            AdapterRequest(key_foo='key_common'),
            [
                # other filtered by NOW
                {
                    'key_bar': 1,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'cold_yt_value',
                    },
                },
                {
                    'key_bar': 2,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:48:34.749324+00:00',
                        'value': 'value_2',
                    },
                    'second_data': {'second_value': 'second_value_2'},
                },
                {
                    'key_bar': 3,
                    'key_foo': 'key_common',
                    'main_data': {
                        'updated_at': '2021-03-15T14:40:30+00:00',
                        'value': 'value_3',
                    },
                },
            ],
        ),
    ],
)
async def test_retrieve_many(
        taxi_userver_db_adapter_sample, yt_apply, db_query, expected_items,
):
    response = await taxi_userver_db_adapter_sample.post(
        '/pg-yt/retrieve-many/by-datetime-index', json=db_query._asdict(),
    )
    assert response.status_code == 200
    assert response.json() == {'items': expected_items}
