import pytest


@pytest.mark.yt(dyn_table_data=['yt_data.yaml'])
@pytest.mark.pgsql('basic_sample_db', files=['pg_data.sql'])
@pytest.mark.parametrize(
    'request_url,db_query_update',
    [
        ('/pg-yt/retrieve-one/composite-primary-key', {}),
        (
            '/pg-yt/retrieve-one/composite-primary-key',
            {'use_yt_select_rows': True},
        ),
        ('/pg-yt/retrieve-one/composite-primary-key-enum', {}),
    ],
)
@pytest.mark.parametrize(
    'db_query,expected_item',
    [
        (
            {'key_foo': 'key_pg', 'key_bar': 1},
            {
                'key_bar': 1,
                'key_foo': 'key_pg',
                'main_data': {
                    'updated_at': '2021-03-21T12:01:00+00:00',
                    'value': 'pg_value_1',
                },
                'second_data': {'second_value': 'pg_second_value_1'},
            },
        ),
        (
            {'key_foo': 'key_pg', 'key_bar': 2},
            {
                'key_bar': 2,
                'key_foo': 'key_pg',
                'main_data': {
                    'updated_at': '2021-03-21T12:02:00+00:00',
                    'value': 'pg_value_2',
                },
            },
        ),
        (
            {'key_foo': 'key_pg', 'key_bar': 2, 'skip_yt': True},
            {
                'key_bar': 2,
                'key_foo': 'key_pg',
                'main_data': {
                    'updated_at': '2021-03-21T12:02:00+00:00',
                    'value': 'pg_value_2',
                },
            },
        ),
        ({'key_foo': 'key_pg', 'key_bar': 2, 'skip_pg': True}, {}),
        (
            {'key_foo': 'key_yt', 'key_bar': 2},
            {
                'key_bar': 2,
                'key_foo': 'key_yt',
                'main_data': {
                    'updated_at': '2021-03-15T14:48:34.749324+00:00',
                    'value': 'value_2',
                },
                'second_data': {'second_value': 'second_value_2'},
            },
        ),
        (
            {'key_foo': 'key_yt', 'key_bar': 3},
            {
                'key_bar': 3,
                'key_foo': 'key_yt',
                'main_data': {
                    'updated_at': '2021-03-15T14:40:30+00:00',
                    'value': 'value_3',
                },
            },
        ),
        ({'key_foo': 'key_yt', 'key_bar': 3, 'skip_yt': True}, {}),
        (
            {
                'key_foo': 'key_yt',
                'key_bar': 3,
                'skip_yt': True,
                'dummy_yt': True,
            },
            {},
        ),
        (
            {
                'key_foo': 'key_pg',
                'key_bar': 2,
                'skip_pg': True,
                'yt_timeout': 1000,
                'use_yt_runtime': True,
            },
            {},
        ),
    ],
)
async def test_retrieve_one(
        taxi_userver_db_adapter_sample,
        yt_apply,
        request_url,
        db_query_update,
        db_query,
        expected_item,
):
    response = await taxi_userver_db_adapter_sample.post(
        request_url, json={**db_query, **db_query_update},
    )
    assert response.status_code == 200
    expected_response = {}
    if expected_item:
        expected_response = {'item': expected_item}
    assert response.json() == expected_response
