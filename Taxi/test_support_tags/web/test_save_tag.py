import datetime

import pytest


@pytest.mark.now('2021-01-01T00:00:00')
@pytest.mark.parametrize(
    'data, records_in_database',
    [
        (
            [],
            [
                (
                    'user_phone_id',
                    'old_user',
                    'one',
                    datetime.datetime(2020, 1, 1, 0, 0),
                    datetime.datetime(2020, 1, 1, 0, 0),
                    2000,
                ),
            ],
        ),
        (
            [
                {
                    'entity_type': 'user_phone_id',
                    'entity_id': 'new_user',
                    'tag': 'one',
                    'ttl': 123,
                },
            ],
            [
                (
                    'user_phone_id',
                    'old_user',
                    'one',
                    datetime.datetime(2020, 1, 1, 0, 0),
                    datetime.datetime(2020, 1, 1, 0, 0),
                    2000,
                ),
                (
                    'user_phone_id',
                    'new_user',
                    'one',
                    datetime.datetime(2021, 1, 1, 0, 0),
                    datetime.datetime(2021, 1, 1, 0, 0),
                    123,
                ),
            ],
        ),
        (
            [
                {
                    'entity_type': 'user_phone_id',
                    'entity_id': 'new_user',
                    'tag': 'one',
                },
            ],
            [
                (
                    'user_phone_id',
                    'old_user',
                    'one',
                    datetime.datetime(2020, 1, 1, 0, 0),
                    datetime.datetime(2020, 1, 1, 0, 0),
                    2000,
                ),
                (
                    'user_phone_id',
                    'new_user',
                    'one',
                    datetime.datetime(2021, 1, 1, 0, 0),
                    datetime.datetime(2021, 1, 1, 0, 0),
                    None,
                ),
            ],
        ),
        (
            [
                {
                    'entity_type': 'user_phone_id',
                    'entity_id': 'old_user',
                    'tag': 'one',
                    'ttl': 4000,
                },
                {
                    'entity_type': 'user_phone_id',
                    'entity_id': 'old_user',
                    'tag': 'one',
                    'ttl': 4000,
                },
            ],
            [
                (
                    'user_phone_id',
                    'old_user',
                    'one',
                    datetime.datetime(2020, 1, 1, 0, 0),
                    datetime.datetime(2021, 1, 1, 0, 0),
                    4000,
                ),
            ],
        ),
    ],
)
async def test_save_tag(web_app_client, pgsql, data, records_in_database):
    response = await web_app_client.post(
        '/v1/save_tags', json={'entities': data},
    )
    assert response.status == 200

    with pgsql['support_tags'].cursor() as cursor:
        cursor.execute('SELECT * FROM support_tags.tags')
        records = cursor.fetchall()
    assert records == records_in_database
