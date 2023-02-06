import dateutil.parser
from dateutil.relativedelta import relativedelta
import pytest

from tests_plugins import utils as utc

from . import utils


@pytest.mark.parametrize(
    'unique_driver_id, expected_code, expected_response',
    [
        ('100000000000000000000001', 200, 'manual_status_info.json'),
        ('100000000000000000000002', 200, 'manual_status_in_progress.json'),
        ('100000000000000000000003', 404, 'manual_status_not_found.json'),
        ('100000000000000000000004', 200, 'manual_status_attempts_ended.json'),
        ('100000000000000000000005', 200, 'manual_status_current_year.json'),
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
async def test_driver_manual_status(
        taxi_loyalty,
        unique_drivers,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        unique_driver_id,
        expected_code,
        expected_response,
):
    unique_drivers.set_unique_driver('db1', 'uuid1', unique_driver_id)
    experiments3.add_experiments_json(
        load_json('loyalty_manual_status_settings.json'),
    )

    response = await taxi_loyalty.post(
        'driver/v1/loyalty/v1/manual/status',
        headers=utils.get_auth_headers(),
        json={
            'position': {'lat': 55.744094, 'lon': 37.627920},
            'timezone': 'Europe/Moscow',
        },
    )

    assert response.status_code == expected_code
    assert response.json() == load_json(expected_response)


def get_borders_and_statuses(number):
    return [
        (
            (0, number // 3),
            (number // 3, 2 * (number // 3)),
            (2 * (number // 3), number - 2),
            (number - 2, number),
        ),
        ('bronze', 'silver', 'gold', 'platinum'),
    ]


def make_array(date_object, number_of_lines):
    start_date = date_object - relativedelta(months=number_of_lines - 1)
    borders, statuses = get_borders_and_statuses(number_of_lines)
    result = [[], [], []]
    for border, status in zip(borders, statuses):
        for line_num in range(*border):
            result[0].append(line_num)
            result[1].append(
                (start_date + relativedelta(months=line_num)).strftime(
                    '%Y-%m-%d %H:%M:%S.%f',
                ),
            )
            result[2].append(status)
    return result


@pytest.mark.driver_tags_match(
    dbid='db1', uuid='uuid1', tags=['200_days_with_trips'],
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'manual_statuses.sql'],
)
@pytest.mark.now('2019-06-15T06:35:00+0300')
async def test_driver_loyalty_big_driver_details(
        taxi_loyalty,
        unique_drivers,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        pgsql,
):
    cursor = pgsql['loyalty'].cursor()
    cursor.execute(
        """INSERT INTO loyalty.status_logs
          (log_id, created, status, unique_driver_id, reason, points)
              SELECT UNNEST(%s), UNNEST(%s::TIMESTAMP[]), UNNEST(%s::TEXT[]),
              '100000000000000000000001', 'recount', 0;
        """,
        (
            make_array(
                utc.to_utc(dateutil.parser.parse('2019-05-01T06:35:00+0300')),
                1000,
            )
        ),
    )
    unique_drivers.set_unique_driver(
        'db1', 'uuid1', '100000000000000000000001',
    )
    experiments3.add_experiments_json(
        load_json('loyalty_manual_status_settings.json'),
    )
    await taxi_loyalty.invalidate_caches()

    response = await taxi_loyalty.post(
        'driver/v1/loyalty/v1/manual/status',
        headers=utils.get_auth_headers(),
        json={
            'position': {'lat': 55.744094, 'lon': 37.627920},
            'timezone': 'Europe/Moscow',
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json('manual_status_big.json')


@pytest.mark.parametrize(
    'time, timezone, result',
    [
        ('2019-04-01T00:00:00+0300', 'Europe/Moscow', 'Серебро'),
        ('2019-04-01T00:00:00+0300', 'Asia/Yekaterinburg', 'Серебро'),
        ('2019-04-01T00:00:00+0300', 'Europe/Kaliningrad', 'Серебро'),
        ('2019-05-01T00:00:00+0300', 'Europe/Moscow', 'Бронза'),
        ('2019-05-01T00:00:00+0300', 'Asia/Yekaterinburg', 'Бронза'),
        ('2019-05-01T00:00:00+0300', 'Europe/Kaliningrad', 'Бронза'),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='db1', uuid='uuid1', tags=['200_days_with_trips'],
)
@pytest.mark.pgsql(
    'loyalty',
    files=['loyalty_accounts.sql', 'status_logs.sql', 'manual_statuses.sql'],
)
async def test_driver_manual_status_in_msk(
        taxi_loyalty,
        unique_drivers,
        mock_fleet_parks_list,
        experiments3,
        load_json,
        mocked_time,
        time,
        timezone,
        result,
):
    mocked_time.set(utc.to_utc(dateutil.parser.parse(time)))
    unique_drivers.set_unique_driver(
        'db1', 'uuid1', '000000000000000000000007',
    )
    experiments3.add_experiments_json(
        load_json('loyalty_manual_status_settings.json'),
    )

    await taxi_loyalty.invalidate_caches()
    response = await taxi_loyalty.post(
        'driver/v1/loyalty/v1/manual/status',
        headers=utils.get_auth_headers(),
        json={
            'position': {'lat': 55.744094, 'lon': 37.627920},
            'timezone': timezone,
        },
    )

    # import pdb; pdb.set_trace()
    assert response.status_code == 200
    assert response.json()['ui']['items'][0]['title'] == result
