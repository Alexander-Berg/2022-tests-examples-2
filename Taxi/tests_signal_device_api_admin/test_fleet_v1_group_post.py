import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/group'


def get_amount_of_groups(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT COUNT(*) FROM signal_device_api.device_groups')
    return list(db)[0][0]


IDEMPOTENCY_TOKEN = '1e45203f-812c-4f25-995e-270fcf15de44'
DUPLICATE_IDEMPOTENCY_TOKEN = 'cc888693-c2c4-4f78-976f-12fc7dc32c0b'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, group_name, parent_group_id, idempotency_token,'
    'is_new_row_created, expected_code, err_response',
    [
        ('p1', 'West', None, IDEMPOTENCY_TOKEN, True, 200, None),
        ('p2', 'East', None, IDEMPOTENCY_TOKEN, True, 200, None),
        (
            'p2',
            'East',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            IDEMPOTENCY_TOKEN,
            True,
            200,
            None,
        ),
        ('p2', 'East', None, DUPLICATE_IDEMPOTENCY_TOKEN, False, 200, None),
        (
            'p2',
            'WrongGroup',
            None,
            DUPLICATE_IDEMPOTENCY_TOKEN,
            False,
            400,
            None,
        ),
        ('p228', 'East', None, DUPLICATE_IDEMPOTENCY_TOKEN, False, 400, None),
        (
            'p2',
            'East',
            'SomeMaybeExistingID',
            DUPLICATE_IDEMPOTENCY_TOKEN,
            False,
            400,
            None,
        ),
        (
            'p2',
            'East',
            '12bb68a6-aae3-421d-9119-ca1c14fd486',
            IDEMPOTENCY_TOKEN,
            False,
            400,
            None,
        ),
        (
            'p2',
            'East',
            'aaa168a6-2aa3-4bbd-9119-ba1114fd4862',
            IDEMPOTENCY_TOKEN,
            False,
            400,
            None,
        ),
        (
            'p3',
            'East',
            'a4cc6cc6-abe3-311d-9109-a23c14fd4862',
            IDEMPOTENCY_TOKEN,
            True,
            400,
            {'code': 'bad_group', 'message': 'Incorrect group provided'},
        ),
    ],
)
async def test_group_post(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        group_name,
        parent_group_id,
        idempotency_token,
        is_new_row_created,
        expected_code,
        err_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    rows_amount_before = get_amount_of_groups(pgsql)
    assert rows_amount_before == 4
    headers = {
        **web_common.PARTNER_HEADERS_1,
        'X-Park-Id': park_id,
        'X-Idempotency-Token': idempotency_token,
    }

    body = {'group_name': group_name}
    if parent_group_id is not None:
        body['parent_group_id'] = parent_group_id

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 400:
        if err_response is not None:
            assert response.json() == err_response
        return

    response_json = response.json()
    group_id = response_json.pop('group_id')
    assert response_json == body
    expected_rows_amount = rows_amount_before + (
        1 if is_new_row_created else 0
    )
    assert get_amount_of_groups(pgsql) == expected_rows_amount

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT group_id, parent_group_id '
        'FROM signal_device_api.device_groups '
        f'WHERE park_id = \'{park_id}\' AND group_name = \'{group_name}\' '
        f'AND idempotency_token = \'{idempotency_token}\'',
    )
    db_result = list(db)
    assert db_result
    assert db_result[0] == (group_id, parent_group_id)
