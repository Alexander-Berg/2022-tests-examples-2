import datetime

import dateutil.parser
import pytest

from tests_plugins import utils

from . import utils as test_utils


CODEGEN_HANDLER_URL = 'driver/v1/loyalty/v1/registration'


# Generated via `tvmknife unittest service -s 111 -d 441`
UNIQUE_DRIVERS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxC5Aw:QetU'
    'JxaU35XR6YtwFZ_CVKMH-DptbFuT7mIzG-6zE_t'
    '8cY-Ek7FtPvNtoJfa88V4CDF3iVecam5VXcpBKu'
    'YbAmL6fi9rHWTDFYiJ0wxzyPBE3wAvDqZ5YjtaN'
    'iKOq8Jw0TiBPlQx_lzVcoH3I7nN5bSBfCz5Hhx-M_1rhuR_0HQ'
)


# pylint: disable=too-many-arguments, too-many-locals
@pytest.mark.parametrize(
    'position,unique_driver_id,time,expected_code,expected_status,'
    'expected_account,expected_log',
    [
        (
            [37.590533, 55.733863],
            '000000000000000000000001',
            '2019-04-01T06:35:00+0500',
            200,
            'silver',
            [
                (
                    '000000000000000000000001',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'silver',
                    '{}',
                    False,
                ),
            ],
            [
                ('silver', '000000000000000000000001', 'recount', 133),
                ('gold', '000000000000000000000001', 'recount', 233),
                ('newbie', '000000000000000000000001', 'registration', 0),
            ],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000002',
            '2019-04-01T06:35:00+0500',
            200,
            'newbie',
            [
                (
                    '000000000000000000000002',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'newbie',
                    '{}',
                    True,
                ),
            ],
            [('newbie', '000000000000000000000002', 'client_registration', 0)],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000002',
            '2019-04-01T06:35:00+0500',
            200,
            'newbie',
            [
                (
                    '000000000000000000000002',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'newbie',
                    '{}',
                    True,
                ),
            ],
            [('newbie', '000000000000000000000002', 'client_registration', 0)],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000002',
            '2019-04-01T01:35:00+0500',
            200,
            'newbie',
            [
                (
                    '000000000000000000000002',
                    datetime.datetime(2019, 3, 31, 21, 0),
                    'newbie',
                    '{}',
                    True,
                ),
            ],
            [('newbie', '000000000000000000000002', 'client_registration', 0)],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000002',
            '2019-04-01T02:35:00+0500',
            200,
            'newbie',
            [
                (
                    '000000000000000000000002',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'newbie',
                    '{}',
                    True,
                ),
            ],
            [('newbie', '000000000000000000000002', 'client_registration', 0)],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000002',
            '2019-03-28T16:35:00+0500',
            200,
            'newbie',
            [
                (
                    '000000000000000000000002',
                    datetime.datetime(2019, 3, 31, 21, 0),
                    'newbie',
                    '{}',
                    True,
                ),
            ],
            [('newbie', '000000000000000000000002', 'client_registration', 0)],
        ),
        (
            [39.590533, 55.733863],
            '000000000000000000000001',
            '2019-04-01T06:35:00+0500',
            200,
            'silver',
            [
                (
                    '000000000000000000000001',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'silver',
                    '{}',
                    False,
                ),
            ],
            [
                ('silver', '000000000000000000000001', 'recount', 133),
                ('gold', '000000000000000000000001', 'recount', 233),
                ('newbie', '000000000000000000000001', 'registration', 0),
            ],
        ),
        (
            [39.590533, 55.733863],
            '000000000000000000000002',
            '2019-04-01T06:35:00+0500',
            200,
            'none',
            [],
            [],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000003',
            '2019-03-28T16:35:00+0500',
            200,
            'returnee',
            [
                (
                    '000000000000000000000003',
                    datetime.datetime(2019, 3, 31, 21, 0),
                    'returnee',
                    '{}',
                    True,
                ),
            ],
            [
                (
                    'returnee',
                    '000000000000000000000003',
                    'client_registration',
                    0,
                ),
                ('undefined', '000000000000000000000003', 'recount', 1),
            ],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000005',
            '2019-03-28T16:35:00+0500',
            200,
            'undefined',
            [
                (
                    '000000000000000000000005',
                    datetime.datetime(2019, 4, 30, 21, 0),
                    'undefined',
                    '{}',
                    False,
                ),
            ],
            [('undefined', '000000000000000000000005', 'recount', 1)],
        ),
        (
            [37.590533, 55.733863],
            '000000000000000000000006',
            '2019-03-28T16:35:00+0500',
            200,
            'undefined',
            [
                (
                    '000000000000000000000006',
                    datetime.datetime(2019, 3, 31, 21, 0),
                    'undefined',
                    '{}',
                    True,
                ),
            ],
            [
                (
                    'undefined',
                    '000000000000000000000006',
                    'client_registration_experiment',
                    0,
                ),
            ],
        ),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='driver_db_id1', uuid='driver_uuid1', tags=['good_driver'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({441: UNIQUE_DRIVERS_SERVICE_TICKET})
@pytest.mark.now('2019-04-01T06:35:00+0500')
@pytest.mark.experiments3(filename='loyalty_registration_settings.json')
@pytest.mark.pgsql(
    'loyalty',
    files=['loyalty_accounts.sql', 'status_logs.sql', 'statistics.sql'],
)
async def test_driver_loyalty_registration(
        taxi_loyalty,
        unique_drivers,
        pgsql,
        position,
        unique_driver_id,
        mock_fleet_parks_list,
        time,
        expected_code,
        expected_status,
        expected_account,
        expected_log,
        mocked_time,
):
    unique_drivers.set_unique_driver(
        'driver_db_id1', 'driver_uuid1', unique_driver_id,
    )
    mocked_time.set(utils.to_utc(dateutil.parser.parse(time)))
    await taxi_loyalty.invalidate_caches()

    def select_account(unique_driver_id):
        cursor = pgsql['loyalty'].cursor()
        cursor.execute(
            'SELECT unique_driver_id, next_recount, status, '
            'block, send_notification '
            'FROM loyalty.loyalty_accounts '
            'WHERE unique_driver_id = \'{}\''.format(unique_driver_id),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    def select_log(unique_driver_id):
        cursor = pgsql['loyalty'].cursor()
        cursor.execute(
            'SELECT status, unique_driver_id, reason, points '
            'FROM loyalty.status_logs '
            'WHERE unique_driver_id = \'{}\' '
            'ORDER BY created DESC'.format(unique_driver_id),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', 'Taximeter 8.80 (562)',
        ),
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == {'loyalty': {'status': expected_status}}

        account = select_account(unique_driver_id)
        assert account == expected_account
        log = select_log(unique_driver_id)
        assert log == expected_log


@pytest.mark.parametrize(
    'expected_code,park_id, expected_status',
    [
        # Registration allowed by zone and country ('rus')
        (200, 'driver_db_id1', 'newbie'),
        # Country not found, country sent as empty kwargs ('')
        # and forbidden by country in config.
        (200, 'park_country_unknown', 'none'),
        # Registration forbidden by country 'aze' in config.
        (200, 'park_aze', 'none'),
    ],
)
@pytest.mark.driver_tags_match(
    dbid='driver_db_id1', uuid='driver_uuid1', tags=['good_driver'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({441: UNIQUE_DRIVERS_SERVICE_TICKET})
@pytest.mark.experiments3(filename='loyalty_registration_settings.json')
async def test_driver_loyalty_registration_country(
        taxi_loyalty,
        unique_drivers,
        mock_fleet_parks_list,
        park_id,
        expected_code,
        expected_status,
):
    unique_driver_id = '000000000000000000000001'
    position = [37.590533, 55.733863]  # zone "moscow"
    unique_drivers.set_unique_driver(park_id, 'driver_uuid1', unique_driver_id)

    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            park_id, 'driver_uuid1', 'Taximeter 8.80 (562)',
        ),
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == {'loyalty': {'status': expected_status}}
