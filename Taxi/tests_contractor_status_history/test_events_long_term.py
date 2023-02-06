# pylint: disable=import-error
# pylint: disable=import-only-modules
# pylint: disable=too-many-lines
import pytest

from tests_contractor_status_history.consts import OrderStatus
from tests_contractor_status_history.consts import Status
import tests_contractor_status_history.fbs_helpers as fbs
import tests_contractor_status_history.utils as utils

try:
    import lz4.block as lz4
except ImportError:
    import lz4

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

FILL_ARCH_CHECK = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-26 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_015 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-25 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_014 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-24 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_013 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-23 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_012 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-22 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_011 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-21 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_010 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-20 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_009 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-19 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_008 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-18 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_007 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-17 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_006 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-16 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_005 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-15 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_004 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-14 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_003 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-13 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_002 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-12 01:00:00.0+00\', \'busy\', \'{}\')::event_tuple'
    ']); '
    'INSERT INTO events_001 VALUES '
    '(\'park4\', \'profile4\', ARRAY['
    '(\'2020-11-11 01:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'COMMIT;'
)


def _convert_tuple_to_dict_event(tuple_event):
    converted = {
        'ts': utils.parse_date_str(tuple_event[0]),
        'status': tuple_event[1],
        'orders': tuple_event[2],
    }
    return converted


def _put_driver_event_history(mds_s3_storage, key, events):
    # NOTE: we add '/mds-s3' path in service.yaml
    # to distinguish mockserver requests
    # there is no '/mds-s3' prefix in production
    path = f'/mds-s3/{key[0]}/{key[1]}/{key[2]}'
    events_list = [
        _convert_tuple_to_dict_event(tuple_event) for tuple_event in events
    ]
    packed_data = fbs.pack_status_history({'events': events_list})
    mds_s3_storage.put_object(path, lz4.compress(bytes(packed_data)))


@pytest.fixture
def _fill_long_term_storage(mds_s3_storage):
    input_data = {
        ('park1', 'profile1', '2020-11-07'): [
            ('2020-11-07 14:00:00.0+03', Status.Online, []),
            ('2020-11-07 15:00:00.0+03', Status.Busy, []),
            (
                '2020-11-07 16:00:00.0+03',
                Status.Online,
                [OrderStatus.kDriving],
            ),
            ('2020-11-07 16:01:00.0+03', Status.Offline, []),
        ],
        ('park1', 'profile1', '2020-11-08'): [
            ('2020-11-08 10:00:00.0+03', Status.Online, []),
            (
                '2020-11-08 10:30:00.0+03',
                Status.Online,
                [OrderStatus.kDriving],
            ),
            (
                '2020-11-08 10:35:00.0+03',
                Status.Online,
                [OrderStatus.kWaiting],
            ),
            (
                '2020-11-08 10:36:00.0+03',
                Status.Online,
                [OrderStatus.kTransporting],
            ),
            ('2020-11-08 14:00:00.0+03', Status.Busy, []),
            # intentionally not in order
            ('2020-11-08 11:01:00.0+03', Status.Online, []),
            ('2020-11-08 16:01:00.0+03', Status.Offline, []),
        ],
        ('park2', 'profile2', '2020-11-05'): [
            ('2020-11-05 14:00:00.0+03', Status.Online, []),
            (
                '2020-11-05 16:00:00.0+03',
                Status.Online,
                [OrderStatus.kDriving],
            ),
            # intentionally not in order
            ('2020-11-05 15:00:00.0+03', Status.Busy, []),
            ('2020-11-05 16:01:00.0+03', Status.Offline, []),
            # intentionally duplication
            ('2020-11-05 15:00:00.0+03', Status.Busy, []),
        ],
        ('park3', 'profile3', '2020-11-06'): [
            ('2020-11-06 10:00:00.0+03', Status.Online, []),
            (
                '2020-11-06 10:30:00.0+03',
                Status.Online,
                [OrderStatus.kDriving],
            ),
            (
                '2020-11-06 10:35:00.0+03',
                Status.Online,
                [OrderStatus.kWaiting],
            ),
            (
                '2020-11-06 10:36:00.0+03',
                Status.Online,
                [OrderStatus.kTransporting],
            ),
            ('2020-11-06 11:01:00.0+03', Status.Online, []),
            ('2020-11-06 14:00:00.0+03', Status.Busy, []),
            ('2020-11-06 16:01:00.0+03', Status.Offline, []),
        ],
        ('park4', 'profile4', '2020-11-10'): [
            ('2020-11-10 01:00:00.0+00', Status.Online, []),
        ],
        ('park4', 'profile4', '2020-11-11'): [
            ('2020-11-11 01:00:00.0+00', Status.Online, []),
        ],
        ('park4', 'profile4', '2020-11-12'): [
            ('2020-11-12 01:00:00.0+00', Status.Online, []),
        ],
        ('park4', 'profile4', '2020-11-13'): [
            ('2020-11-13 01:00:00.0+00', Status.Online, []),
        ],
        ('park4', 'profile4', '2020-11-14'): [
            ('2020-11-14 01:00:00.0+00', Status.Online, []),
        ],
        ('park5', 'profile5', '2020-11-23'): [
            ('2020-11-23 23:59:50.0+00', Status.Online, []),
            ('2020-11-23 23:59:55.0+00', Status.Busy, []),
            ('2020-11-23 23:59:59.0+00', Status.Online, []),
        ],
    }
    for key, event_tuples in input_data.items():
        _put_driver_event_history(mds_s3_storage, key, event_tuples)


@pytest.mark.pgsql(
    'contractor_status_history',
    queries=[FILL_EVENTS_000, FILL_EVENTS_001, FILL_EVENTS_015],
)
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=365,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=64,
)
@pytest.mark.parametrize(
    'park_id,profile_id,from_ts,to_ts,expected',
    [
        pytest.param(
            'park1',
            'profile1',
            '2020-11-07 00:00:00+00',
            '2020-11-26 15:01:00+03',
            {
                'park_id': 'park1',
                'profile_id': 'profile1',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-07 03:00:00.0+03',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-07 14:00:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-07 15:00:00.0+03',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-07 16:00:00.0+03',
                        ),
                        'status': Status.Online,
                        'on_order': True,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-07 16:01:00.0+03',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-08 10:00:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-08 10:30:00.0+03',
                        ),
                        'status': Status.Online,
                        'on_order': True,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-08 11:01:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-08 14:00:00.0+03',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-08 16:01:00.0+03',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 15:00:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 15:01:00.0+03',
                        ),
                        'status': Status.Online,
                        'on_order': True,
                    },
                ],
            },
            id='from today to several days ago',
        ),
        pytest.param(
            'park2',
            'profile2',
            '2020-11-05 00:00:00+03',
            '2020-11-05 16:01:00+03',
            {
                'park_id': 'park2',
                'profile_id': 'profile2',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-05 00:00:00.0+03',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-05 14:00:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-05 15:00:00.0+03',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-05 16:00:00.0+03',
                        ),
                        'status': Status.Online,
                        'on_order': True,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-05 16:01:00.0+03',
                        ),
                        'status': Status.Offline,
                    },
                ],
            },
            id='for one day profile 2',
        ),
        pytest.param(
            'park3',
            'profile3',
            '2020-11-06 10:00:00+03',
            '2020-11-06 16:01:00+03',
            {
                'park_id': 'park3',
                'profile_id': 'profile3',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-06 10:00:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-06 10:30:00.0+03',
                        ),
                        'status': Status.Online,
                        'on_order': True,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-06 11:01:00.0+03',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-06 14:00:00.0+03',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-06 16:01:00.0+03',
                        ),
                        'status': Status.Offline,
                    },
                ],
            },
            id='for one day profile 3',
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_events_long_term(
        taxi_contractor_status_history,
        mocked_time,
        testpoint,
        park_id,
        profile_id,
        from_ts,
        to_ts,
        expected,
        _fill_long_term_storage,
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
    response = await taxi_contractor_status_history.post('events', json=req)
    assert response.status_code == 200

    expected_resp = {'contractors': [expected]}
    assert expected_resp == response.json()


@pytest.mark.pgsql(
    'contractor_status_history',
    queries=[FILL_EVENTS_000, FILL_EVENTS_001, FILL_EVENTS_015],
)
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=365,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=64,
)
@pytest.mark.parametrize(
    'contractors,from_ts,to_ts,expected',
    [
        pytest.param(
            [
                ('park1', 'profile1'),
                ('park2', 'profile2'),
                ('park3', 'profile3'),
            ],
            '2020-11-05 00:00:00+00',
            '2020-11-26 15:01:00+03',
            [
                {
                    'park_id': 'park1',
                    'profile_id': 'profile1',
                    'events': [
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 03:00:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-07 14:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-07 15:00:00.0+03',
                            ),
                            'status': Status.Busy,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-07 16:00:00.0+03',
                            ),
                            'status': Status.Online,
                            'on_order': True,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-07 16:01:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-08 10:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-08 10:30:00.0+03',
                            ),
                            'status': Status.Online,
                            'on_order': True,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-08 11:01:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-08 14:00:00.0+03',
                            ),
                            'status': Status.Busy,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-08 16:01:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-26 15:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-26 15:01:00.0+03',
                            ),
                            'status': Status.Online,
                            'on_order': True,
                        },
                    ],
                },
                {
                    'park_id': 'park2',
                    'profile_id': 'profile2',
                    'events': [
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 03:00:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 14:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 15:00:00.0+03',
                            ),
                            'status': Status.Busy,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 16:00:00.0+03',
                            ),
                            'status': Status.Online,
                            'on_order': True,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 16:01:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-25 15:00:00.0+03',
                            ),
                            'status': Status.Busy,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-26 15:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                    ],
                },
                {
                    'park_id': 'park3',
                    'profile_id': 'profile3',
                    'events': [
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-05 03:00:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-06 10:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-06 10:30:00.0+03',
                            ),
                            'status': Status.Online,
                            'on_order': True,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-06 11:01:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-06 14:00:00.0+03',
                            ),
                            'status': Status.Busy,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-06 16:01:00.0+03',
                            ),
                            'status': Status.Offline,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-25 15:00:00.0+03',
                            ),
                            'status': Status.Busy,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-26 15:00:00.0+03',
                            ),
                            'status': Status.Online,
                        },
                    ],
                },
            ],
            id='from today to several days ago',
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_events_several_contractors(
        taxi_contractor_status_history,
        mocked_time,
        contractors,
        testpoint,
        from_ts,
        to_ts,
        expected,
        _fill_long_term_storage,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )
    mocked_time.set(NOW)
    request_contractors = [
        {'park_id': contractor[0], 'profile_id': contractor[1]}
        for contractor in contractors
    ]
    req = {
        'interval': {
            'from': utils.date_str_to_sec(from_ts),
            'to': utils.date_str_to_sec(to_ts),
        },
        'contractors': request_contractors,
    }
    response = await taxi_contractor_status_history.post('events', json=req)
    assert response.status_code == 200

    expected_resp = {'contractors': expected}
    assert expected_resp == response.json()


@pytest.mark.pgsql('contractor_status_history', queries=[FILL_ARCH_CHECK])
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=365,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=64,
)
@pytest.mark.parametrize(
    'park_id,profile_id,from_ts,to_ts,expected',
    [
        pytest.param(
            'park4',
            'profile4',
            '2020-11-10 00:00:01+00',
            '2020-11-26 23:00:01+00',
            {
                'park_id': 'park4',
                'profile_id': 'profile4',
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-10 00:00:01.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-10 01:00:00.0+00',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-11 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-12 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-13 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-14 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-15 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-16 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-17 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-18 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-19 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-20 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-21 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-22 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-24 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-25 01:00:00.0+00',
                        ),
                        'status': Status.Offline,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-26 01:00:00.0+00',
                        ),
                        'status': Status.Busy,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_events_arch_check(
        taxi_contractor_status_history,
        mocked_time,
        testpoint,
        park_id,
        profile_id,
        from_ts,
        to_ts,
        expected,
        _fill_long_term_storage,
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
    response = await taxi_contractor_status_history.post('events', json=req)
    assert response.status_code == 200

    expected_resp = {'contractors': [expected]}
    assert expected_resp == response.json()


@pytest.mark.fail_s3mds({'code': 429, 'msg': 'Too Many Requests'})
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=30,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=30,
)
async def test_failures(
        taxi_contractor_status_history, mocked_time, testpoint,
):

    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )

    from_ts = '2020-11-07 00:00:00+00'
    to_ts = '2020-11-26 15:01:00+03'

    mocked_time.set(NOW)
    request_contractors = [{'park_id': 'park', 'profile_id': 'profile'}]
    req = {
        'interval': {
            'from': utils.date_str_to_sec(from_ts),
            'to': utils.date_str_to_sec(to_ts),
        },
        'contractors': request_contractors,
    }
    response = await taxi_contractor_status_history.post('events', json=req)
    assert response.status_code == 429


@pytest.mark.parametrize(
    'from_ts,to_ts,cfg_threshold,cfg_max_percent,expected',
    [
        pytest.param(
            '2020-11-23 23:59:50+00',
            '2020-11-25 23:59:50+00',
            5000,
            3,
            {
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 23:59:50.0+00',
                        ),
                        'status': Status.Online,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 23:59:55.0+00',
                        ),
                        'status': Status.Busy,
                    },
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 23:59:59.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='above threshold',
        ),
        pytest.param(
            '2020-11-23 23:59:56+00',
            '2020-11-25 23:59:50+00',
            5000,
            3,
            {'events': []},
            id='below threshold',
        ),
        pytest.param(
            '2020-11-23 23:59:59+00',
            '2020-11-24 00:00:01+00',
            1001,
            1,
            {
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 23:59:59.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='threshold > range * percent',
        ),
        pytest.param(
            '2020-11-23 23:59:59+00',
            '2020-11-24 23:59:01+00',
            1001,
            50,
            {'events': []},
            id='threshold < range * percent',
        ),
        pytest.param(
            '2020-11-23 23:59:59+00',
            '2020-11-24 00:00:00+00',
            0,
            50,
            {
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 23:59:59.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='zero threshold',
        ),
        pytest.param(
            '2020-11-23 23:59:59+00',
            '2020-11-24 00:00:00+00',
            10000,
            0,
            {
                'events': [
                    {
                        'timestamp': utils.date_str_to_sec(
                            '2020-11-23 23:59:59.0+00',
                        ),
                        'status': Status.Online,
                    },
                ],
            },
            id='0 percent',
        ),
        pytest.param(
            '2020-11-23 23:59:50+00',
            '2020-11-24 23:59:50+00',
            10001,
            100,
            {'events': []},
            id='100 percent',
        ),
    ],
)
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=30,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=30,
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_mds_threshold(
        taxi_contractor_status_history,
        from_ts,
        to_ts,
        cfg_threshold,
        cfg_max_percent,
        expected,
        mocked_time,
        testpoint,
        taxi_config,
        _fill_long_term_storage,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )
    taxi_config.set(
        CONTRACTOR_STATUS_HISTORY_MDS_LOOKUP_THRESHOLD={
            'threshold_ms': cfg_threshold,
            'threshold_max_percent': cfg_max_percent,
        },
    )
    await taxi_contractor_status_history.invalidate_caches()

    park_id = 'park5'
    profile_id = 'profile5'
    mocked_time.set(NOW)
    req = {
        'interval': {
            'from': utils.date_str_to_sec(from_ts),
            'to': utils.date_str_to_sec(to_ts),
        },
        'contractors': [{'park_id': park_id, 'profile_id': profile_id}],
    }
    response = await taxi_contractor_status_history.post('events', json=req)
    assert response.status_code == 200

    expected_resp = {
        'contractors': [
            {
                'park_id': park_id,
                'profile_id': profile_id,
                'events': expected['events'],
            },
        ],
    }
    assert expected_resp == response.json()
