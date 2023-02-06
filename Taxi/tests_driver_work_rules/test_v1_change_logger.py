import pytest

from tests_driver_work_rules import defaults


ENDPOINT = 'service/v1/change-logger'


def check_changes(pgsql, request_body, pg_values):
    cursor = pgsql['misc'].conn.cursor()
    cursor.execute('SELECT * FROM changes_0')
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]

    if not res and not pg_values:
        return
    assert len(res) == 1
    pg_entry = res[0]
    assert pg_entry['park_id'] == request_body['park_id']
    assert pg_entry['id'] == request_body['entity_id']
    assert pg_entry['object_id'] == request_body['change_info']['object_id']
    assert pg_entry['object_type'] == (
        request_body['change_info']['object_type']
    )
    assert pg_entry['counts'] == 1
    assert pg_entry['values'] == pg_values
    assert pg_entry['user_id'] == request_body['author']['dispatch_user_id']
    assert pg_entry['user_name'] == request_body['author']['display_name']
    assert pg_entry['ip'] == request_body['author']['user_ip']


@pytest.mark.parametrize(
    'diff, pg_values, expected_code',
    [
        (
            [
                {
                    'field': 'category',
                    'old': 'sticker',
                    'new': 'sticker, lightbox',
                },
            ],
            '{"category":{"old":"sticker","current":"sticker, lightbox"}}',
            200,
        ),
        (
            [{'field': 'category', 'old': 'sticker', 'new': 'sticker'}],
            None,
            200,
        ),
        (
            [
                {
                    'field': 'category',
                    'old': 'sticker',
                    'new': 'sticker, lightbox',
                },
                {
                    'field': 'category',
                    'old': 'sticker',
                    'new': 'sticker, lightbox',
                },
            ],
            None,
            400,
        ),
    ],
)
async def test_change_logger(
        taxi_driver_work_rules,
        fleet_parks_shard,
        pgsql,
        diff,
        pg_values,
        expected_code,
):
    request_body = {
        'park_id': 'park_id',
        'entity_id': 'entity_id',
        'change_info': {
            'object_id': 'object_id',
            'object_type': 'MongoDB.Docs.Car.CarDoc',
            'diff': diff,
        },
        'author': {
            'dispatch_user_id': '',
            'display_name': 'driver',
            'user_ip': '',
        },
    }

    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers={'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET},
        json=request_body,
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        check_changes(pgsql, request_body, pg_values)
