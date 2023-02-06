import datetime


import pytest


from . import utils


@pytest.mark.parametrize(
    'unique_driver_id, token, expected_status, expected_code, '
    'expected_account, expected_log, expected_manual_status',
    [
        (
            '100000000000000000000001',
            'token',
            'bronze',
            200,
            [
                (
                    '100000000000000000000001',
                    datetime.datetime(2019, 6, 30, 21, 0),
                    'bronze',
                    '{}',
                    True,
                ),
            ],
            [
                ('bronze', '100000000000000000000001', 'manual', 0),
                ('silver', '100000000000000000000001', 'recount', 1),
                ('silver', '100000000000000000000001', 'recount', 1),
                ('bronze', '100000000000000000000001', 'recount', 1),
            ],
            [
                ('100000000000000000000001', 'bronze'),
                ('100000000000000000000001', 'gold'),
                ('100000000000000000000001', 'silver'),
            ],
        ),
        (
            '100000000000000000000001',
            '342fdsfdgsdg',
            'bronze',
            200,
            [
                (
                    '100000000000000000000001',
                    datetime.datetime(2019, 6, 30, 21, 0),
                    'silver',
                    '{}',
                    False,
                ),
            ],
            [
                ('silver', '100000000000000000000001', 'recount', 1),
                ('silver', '100000000000000000000001', 'recount', 1),
                ('bronze', '100000000000000000000001', 'recount', 1),
            ],
            [
                ('100000000000000000000001', 'gold'),
                ('100000000000000000000001', 'silver'),
            ],
        ),
        (
            '100000000000000000000002',
            'token',
            'in_progress',
            409,
            None,
            None,
            None,
        ),
        (
            '100000000000000000000003',
            'token',
            'no_statuses',
            404,
            None,
            None,
            None,
        ),
        (
            '100000000000000000000004',
            'token',
            'no_attempts_left',
            409,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='db1', uuid='uuid1', tags=['200_days_with_trips'],
)
@pytest.mark.pgsql(
    'loyalty',
    files=['loyalty_accounts.sql', 'status_logs.sql', 'manual_statuses.sql'],
)
@pytest.mark.now('2019-06-01T06:35:00+0300')
async def test_driver_manual_status_set(
        taxi_loyalty,
        tags,
        unique_drivers,
        mock_fleet_parks_list,
        experiments3,
        pgsql,
        load_json,
        unique_driver_id,
        token,
        expected_status,
        expected_code,
        expected_account,
        expected_log,
        expected_manual_status,
):
    tags.set_append_tag(expected_status)

    unique_drivers.set_unique_driver('db1', 'uuid1', unique_driver_id)
    experiments3.add_experiments_json(
        load_json('loyalty_manual_status_settings.json'),
    )

    headers = utils.get_auth_headers()
    headers['X-Idempotency-Token'] = token

    response = await taxi_loyalty.put(
        'driver/v1/loyalty/v1/manual/status/set',
        headers=headers,
        json={
            'position': {'lat': 55.744094, 'lon': 37.627920},
            'timezone': 'Europe/Moscow',
        },
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        account = utils.select_account(pgsql, unique_driver_id)
        assert account == expected_account
        log = utils.select_log(pgsql, unique_driver_id)
        assert log == expected_log
        manual_status = utils.select_manual_status(pgsql, unique_driver_id)
        assert manual_status == expected_manual_status
