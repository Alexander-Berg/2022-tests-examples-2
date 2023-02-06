# pylint: disable=import-only-modules
import pytest

from tests_contractor_status_history.consts import OrderStatus
from tests_contractor_status_history.consts import Status
import tests_contractor_status_history.utils as utils


NOW = utils.parse_date_str('2020-11-26 23:59:59.0+00')

DEFAULT_CONTRACTOR = {'park_id': 'park1', 'profile_id': 'profile1'}

# corresponds to 2020-11-10, 2020-11-26 ('today'), 2020-12-12
FILL_EVENTS_000 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(\'2020-11-26 15:00:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:01:00.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-26 15:02:00.0+03\', \'busy\', '
    '\'{transporting,waiting}\')::event_tuple,'
    '(\'2020-11-26 15:03:00.0+03\', \'offline\', \'{}\')::event_tuple'
    ']), (\'park2\', \'profile2\',  ARRAY['
    '(\'2020-11-26 15:00:00.0+03\', \'online\', \'{}\')::event_tuple'
    # cannot be in prod, for time ranges testing
    ']), (\'park3\', \'profile3\',  ARRAY['
    '(\'2020-11-10 15:00:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:00:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-12-12 15:00:00.0+03\', \'online\', \'{}\')::event_tuple'
    ']), (\'park4\', \'profile4\',  ARRAY['
    '(\'2020-11-26 15:00:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:05:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:05:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:10:00.0+03\', \'busy\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:15:00.0+03\', \'busy\', \'{waiting}\')::event_tuple,'
    '(\'2020-11-26 15:20:00.0+03\', \'busy\', \'{waiting}\')::event_tuple,'
    '(\'2020-11-26 15:25:00.0+03\', \'busy\', \'{waiting,driving}\')'
    '::event_tuple'
    ']); '
    'COMMIT;'
)

# corresponds to 2020-11-11, 2020-11-27 ('tomorrow'), 2020-12-13
FILL_EVENTS_001 = (
    # cannot be in prod, for time ranges testing
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_001 VALUES '
    # cannot be in prod, for time ranges testing
    '(\'park3\', \'profile3\', ARRAY['
    '(\'2020-11-11 15:00:00.0+03\', \'offline\', \'{}\')::event_tuple,'
    '(\'2020-11-27 15:00:00.0+03\', \'offline\', \'{}\')::event_tuple,'
    '(\'2020-12-13 15:00:00.0+03\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'COMMIT;'
)

# corresponds to 2020-11-17
FILL_EVENTS_007 = (
    # cannot be in prod, for time ranges testing
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_007 VALUES '
    # cannot be in prod, for time ranges testing
    '(\'park7\', \'profile7\', ARRAY['
    '(\'2020-11-17 15:00:00.0+03\', \'offline\', \'{}\')::event_tuple,'
    '(\'2020-11-17 15:00:01.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-17 15:00:02.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-17 15:00:03.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-17 15:00:04.0+03\', \'online\', '
    '\'{driving,waiting}\')::event_tuple,'
    '(\'2020-11-17 15:00:05.0+03\', \'online\', '
    '\'{waiting,driving}\')::event_tuple,'
    '(\'2020-11-17 15:00:06.0+03\', \'online\', '
    '\'{transporting}\')::event_tuple,'
    '(\'2020-11-17 15:00:07.0+03\', \'online\', '
    '\'{transporting,complete}\')::event_tuple,'
    '(\'2020-11-17 15:00:08.0+03\', \'online\', \'{complete}\')::event_tuple,'
    '(\'2020-11-17 15:00:09.0+03\', \'busy\', \'{complete}\')::event_tuple,'
    '(\'2020-11-17 15:00:10.0+03\', \'busy\', \'{}\')::event_tuple,'
    # not in order by time
    '(\'2020-11-17 14:59:00.0+03\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'COMMIT;'
)

# corresponds to 2020-11-09, 2020-11-25 ('yesterday'), 2020-12-11
FILL_EVENTS_015 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_015 VALUES '
    '(\'park2\', \'profile2\', ARRAY['
    '(\'2020-11-25 15:00:00.0+03\', \'busy\', \'{}\')::event_tuple'
    # cannot be in prod, for time ranges testing
    ']), (\'park3\', \'profile3\',  ARRAY['
    '(\'2020-11-09 15:00:00.0+03\', \'busy\', \'{}\')::event_tuple,'
    '(\'2020-11-25 15:00:00.0+03\', \'busy\', \'{}\')::event_tuple,'
    '(\'2020-12-11 15:00:00.0+03\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'COMMIT;'
)


async def test_non_existent_contractor(
        taxi_contractor_status_history, pgsql, mocked_time, testpoint,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )

    mocked_time.set(NOW)

    park_id = 'somepark'
    profile_id = 'someprofile'
    req = {
        'interval': {'duration': 43200},
        'contractors': [{'park_id': park_id, 'profile_id': profile_id}],
    }
    resp = await taxi_contractor_status_history.post(
        'extended-events', json=req,
    )
    assert resp.status_code == 200

    contractors = resp.json()['contractors']
    assert len(contractors) == 1
    contractor = contractors[0]
    assert contractor['park_id'] == park_id
    assert contractor['profile_id'] == profile_id
    events = contractor.get('events')
    assert events is None or not events

    # test that request for history for non-existent contractor
    # do not modify history.events_XXX table
    for i in range(16):
        cursor = pgsql['contractor_status_history'].cursor()
        cursor.execute(
            f'SELECT count(*) FROM history.events_{i:03d} '
            f'WHERE park_id = \'{park_id}\' '
            f'AND profile_id = \'{profile_id}\';',
        )
        assert cursor.fetchone()[0] == 0


@pytest.mark.pgsql(
    'contractor_status_history',
    queries=[FILL_EVENTS_000, FILL_EVENTS_001, FILL_EVENTS_015],
)
@pytest.mark.parametrize(
    'park_id,profile_id,from_ts,to_ts,expected',
    [
        pytest.param(
            'park1',
            'profile1',
            '2020-11-26 11:00:00+00',
            '2020-11-26 13:00:00+00',
            {
                'park_id': 'park1',
                'profile_id': 'profile1',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 11:00:00+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:01:00.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [OrderStatus.kDriving],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:02:00.0+00',
                        ),
                        'status': Status.Busy,
                        'order_statuses': [
                            OrderStatus.kTransporting,
                            OrderStatus.kWaiting,
                        ],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:03:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                ],
            },
            id='from-to within today',
        ),
        pytest.param(
            'park2',
            'profile2',
            '2020-11-25 11:00:00+00',
            '2020-11-26 13:00:00+00',
            {
                'park_id': 'park2',
                'profile_id': 'profile2',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-25 11:00:00+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-25 12:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='from is in yesterday, to is in today',
        ),
        pytest.param(
            'park3',
            'profile3',
            '2020-11-26 11:00:00+00',
            '2020-12-13 13:00:00+00',
            {
                'park_id': 'park3',
                'profile_id': 'profile3',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 11:00:00+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='from is in today, to is in the future',
        ),
        pytest.param(
            'park3',
            'profile3',
            # NOTE: actual 'from' will be NOW - REQUEST_DURATION_MAX_DAYS
            '2020-11-09 11:00:00+00',
            '2020-11-26 13:00:00+00',
            {
                'park_id': 'park3',
                'profile_id': 'profile3',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-24 23:59:59+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-25 12:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='from is far in the past, to is in today',
        ),
    ],
)
async def test_from_to(
        taxi_contractor_status_history,
        mocked_time,
        park_id,
        profile_id,
        from_ts,
        to_ts,
        expected,
        testpoint,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )
    mocked_time.set(NOW)

    req = {
        'interval': {
            'from': utils.date_str_to_sec(from_ts),
            'to': utils.date_str_to_sec(to_ts),
        },
        'contractors': [{'park_id': park_id, 'profile_id': profile_id}],
    }
    response = await taxi_contractor_status_history.post(
        'extended-events', json=req,
    )
    assert response.status_code == 200

    expected_resp = {'contractors': [expected]}
    assert expected_resp == response.json()


@pytest.mark.pgsql(
    'contractor_status_history',
    queries=[FILL_EVENTS_000, FILL_EVENTS_001, FILL_EVENTS_015],
)
@pytest.mark.parametrize(
    'park_id,profile_id,duration,expected',
    [
        pytest.param(
            'park3',
            'profile3',
            3600 * 13,
            {
                'park_id': 'park3',
                'profile_id': 'profile3',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 10:59:59.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='duration within today',
        ),
        pytest.param(
            'park3',
            'profile3',
            3600 * 24 * 2,
            {
                'park_id': 'park3',
                'profile_id': 'profile3',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-24 23:59:59.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-25 12:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='duration within two days',
        ),
        pytest.param(
            'park3',
            'profile3',
            # NOTE: REQUEST_DURATION_MAX_DAYS
            3600 * 24 * 100,
            {
                'park_id': 'park3',
                'profile_id': 'profile3',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-24 23:59:59.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-25 12:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='long duration',
        ),
    ],
)
async def test_duration(
        taxi_contractor_status_history,
        mocked_time,
        park_id,
        profile_id,
        duration,
        expected,
        testpoint,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )
    mocked_time.set(NOW)

    req = {
        'interval': {'duration': duration},
        'contractors': [{'park_id': park_id, 'profile_id': profile_id}],
    }
    response = await taxi_contractor_status_history.post(
        'extended-events', json=req,
    )
    assert response.status_code == 200

    expected_resp = {'contractors': [expected]}
    assert expected_resp == response.json()


@pytest.mark.pgsql('contractor_status_history', queries=[FILL_EVENTS_007])
async def test_merge(taxi_contractor_status_history, mocked_time, testpoint):
    now_tp = utils.parse_date_str('2020-11-17 23:59:59.0+00')
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, now_tp,
    )
    mocked_time.set(now_tp)

    req = {
        'interval': {'duration': 3600 * 13},
        'contractors': [{'park_id': 'park7', 'profile_id': 'profile7'}],
    }
    response = await taxi_contractor_status_history.post(
        'extended-events', json=req,
    )
    assert response.status_code == 200

    expected_resp = {
        'contractors': [
            {
                'park_id': 'park7',
                'profile_id': 'profile7',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 10:59:59.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 11:59:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:01.0+00',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:02.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [OrderStatus.kDriving],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:04.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [
                            OrderStatus.kDriving,
                            OrderStatus.kWaiting,
                        ],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:05.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [
                            OrderStatus.kWaiting,
                            OrderStatus.kDriving,
                        ],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:06.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [OrderStatus.kTransporting],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:07.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [
                            OrderStatus.kTransporting,
                            OrderStatus.kComplete,
                        ],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:08.0+00',
                        ),
                        'status': Status.Online,
                        'order_statuses': [OrderStatus.kComplete],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:09.0+00',
                        ),
                        'status': Status.Busy,
                        'order_statuses': [OrderStatus.kComplete],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 12:00:10.0+00',
                        ),
                        'status': Status.Busy,
                    },
                ],
            },
        ],
    }
    assert expected_resp == response.json()


@pytest.mark.pgsql('contractor_status_history', queries=[FILL_EVENTS_000])
async def test_merge_verbose(
        taxi_contractor_status_history, mocked_time, testpoint,
):
    now_tp = utils.parse_date_str('2020-11-26 23:59:59.0+00')
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, now_tp,
    )
    mocked_time.set(now_tp)
    req = {
        'interval': {'duration': 3600 * 13},
        'verbose': True,
        'contractors': [{'park_id': 'park4', 'profile_id': 'profile4'}],
    }
    response = await taxi_contractor_status_history.post(
        'extended-events', json=req,
    )
    assert response.status_code == 200

    expected_resp = {
        'contractors': [
            {
                'park_id': 'park4',
                'profile_id': 'profile4',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 10:59:59.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:05:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:10:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:15:00.0+00',
                        ),
                        'status': Status.Busy,
                        'order_statuses': [OrderStatus.kWaiting],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:20:00.0+00',
                        ),
                        'status': Status.Busy,
                        'order_statuses': [OrderStatus.kWaiting],
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 12:25:00.0+00',
                        ),
                        'status': Status.Busy,
                        'order_statuses': [
                            OrderStatus.kWaiting,
                            OrderStatus.kDriving,
                        ],
                    },
                ],
            },
        ],
    }
    assert expected_resp == response.json()
