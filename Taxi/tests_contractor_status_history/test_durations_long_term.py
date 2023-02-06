# pylint: disable=import-error
# pylint: disable=import-only-modules
import pytest

from tests_contractor_status_history.consts import OrderStatus
from tests_contractor_status_history.consts import Status
import tests_contractor_status_history.fbs_helpers as fbs
import tests_contractor_status_history.utils as utils

try:
    import lz4.block as lz4
except ImportError:
    import lz4

# legend:
#   | - some event within day
#   || - days boundary
#   no events, online, online + order, etc - event description

NOW = utils.parse_date_str('2020-11-26 23:59:59.0+00')

# corresponds to 2020-11-26 ('today')
FILL_EVENTS_000 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    '(\'park\', \'profile1\',  ARRAY['
    '(\'2020-11-26 09:00:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 10:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'COMMIT;'
)


# corresponds to 2020-11-25 ('yesterday')
FILL_EVENTS_015 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_015 VALUES '
    '(\'park\', \'profile1\',  ARRAY['
    '(\'2020-11-25 09:00:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-25 10:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
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
        ('park', 'profile1', '2020-11-20'): [
            ('2020-11-20 14:00:00.0+00', Status.Online, []),
            ('2020-11-20 16:00:00.0+00', Status.Offline, []),
        ],
        ('park', 'profile1', '2020-11-21'): [
            ('2020-11-21 09:00:00.0+00', Status.Online, []),
            ('2020-11-21 10:00:00.0+00', Status.Busy, []),
            ('2020-11-21 11:00:00.0+00', Status.Offline, []),
        ],
        ('park', 'profile1', '2020-11-22'): [
            ('2020-11-22 09:00:00.0+00', Status.Online, []),
            (
                '2020-11-22 10:00:00.0+00',
                Status.Online,
                [OrderStatus.kDriving],
            ),
            ('2020-11-22 11:00:00.0+00', Status.Busy, []),
            ('2020-11-22 12:00:00.0+00', Status.Offline, []),
        ],
        ('park', 'profile1', '2020-11-23'): [
            ('2020-11-23 09:00:00.0+00', Status.Online, []),
            ('2020-11-23 10:00:00.0+00', Status.Busy, []),
            ('2020-11-23 11:00:00.0+00', Status.Busy, [OrderStatus.kDriving]),
            ('2020-11-23 12:00:00.0+00', Status.Offline, []),
            ('2020-11-23 23:00:00.0+00', Status.Online, []),
        ],
    }
    for key, event_tuples in input_data.items():
        _put_driver_event_history(mds_s3_storage, key, event_tuples)


@pytest.mark.pgsql(
    'contractor_status_history', queries=[FILL_EVENTS_000, FILL_EVENTS_015],
)
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=8,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=8,
    CONTRACTOR_STATUS_HISTORY_CONSIDER_OFFLINE_AFTER_HOURS=24,
)
@pytest.mark.parametrize(
    'profile, interval, expected',
    [
        pytest.param(
            'profile1',
            ('2020-11-19 23:59:59.0+00', '2020-11-20 00:00:00.0+00'),
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='0. On history border call. No events',
        ),
        pytest.param(
            'profile1',
            ('2020-11-20 13:59:59.0+00', '2020-11-20 17:00:00.0+00'),
            {
                'online': {'total': 7200, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='1. profile1 2020-11-20 [ no events | online ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-21 09:00:00.0+00', '2020-11-21 17:00:00.0+00'),
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 3600, 'on_order': 0},
            },
            id='2. profile1 2020-11-21 [ online | busy ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-21 00:00:00.0+00', '2020-11-21 17:00:00.0+00'),
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 3600, 'on_order': 0},
            },
            id='3. profile1 2020-11-21 [ offline || online | busy ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-20 15:00:00.0+00', '2020-11-21 17:00:00.0+00'),
            {
                'online': {'total': 7200, 'on_order': 0},
                'busy': {'total': 3600, 'on_order': 0},
            },
            id='4. profile1 2020-11-20 to 11-21 '
            '[ online | offline || online | busy ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-22 08:00:00.0+00', '2020-11-22 12:00:00.0+00'),
            {
                'online': {'total': 7200, 'on_order': 3600},
                'busy': {'total': 3600, 'on_order': 0},
            },
            id='5. profile1 2020-11-22 '
            '[ offline || online | online+on_order | busy | offline ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-23 08:00:00.0+00', '2020-11-23 12:00:00.0+00'),
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 7200, 'on_order': 3600},
            },
            id='6. profile1 2020-11-23 '
            '[ offline || online | busy+on_order | busy | offline ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-20 15:00:00.0+00', '2020-11-23 12:00:00.0+00'),
            {
                'online': {'total': 18000, 'on_order': 3600},
                'busy': {'total': 14400, 'on_order': 3600},
            },
            id='7. profile1 2020-11-20 - 2020-11-23 ',
        ),
        pytest.param(
            'profile1',
            ('2020-11-24 22:00:00.0+00', '2020-11-24 23:00:00.0+00'),
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='8. profile1 2020-11-24 [ online || no events ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-25 00:00:00.0+00', '2020-11-25 01:00:00.0+00'),
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='9. profile1 2020-11-25 '
            '[ online || no events || no events ] count to be offline!',
        ),
        pytest.param(
            'profile1',
            ('2020-11-25 00:00:00.0+00', '2020-11-25 11:00:00.0+00'),
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='10. profile1 2020-11-25 [no_events | online | offline ]',
        ),
        pytest.param(
            'profile1',
            ('2020-11-24 23:00:00.0+00', '2020-11-25 11:00:00.0+00'),
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='11. profile1 2020-11-23 - 2020-11-25 '
            '[ online (too far) || no events || online ]',
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_durations(
        taxi_contractor_status_history,
        mocked_time,
        profile,
        interval,
        expected,
        testpoint,
        _fill_long_term_storage,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )

    mocked_time.set(NOW)

    req = {
        'interval': {
            'from': utils.date_str_to_sec(interval[0]),
            'to': utils.date_str_to_sec(interval[1]),
        },
        'contractors': [{'park_id': 'park', 'profile_id': profile}],
    }
    response = await taxi_contractor_status_history.post('durations', json=req)
    assert response.status_code == 200

    expected_contractor = expected
    expected_contractor['park_id'] = 'park'
    expected_contractor['profile_id'] = profile
    expected_resp = {'contractors': [expected_contractor]}
    assert expected_resp == response.json()


@pytest.mark.fail_s3mds({'code': 429, 'msg': 'Too Many Requests'})
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_MAX_DAYS=30,
    CONTRACTOR_STATUS_HISTORY_REQUEST_DURATION_MAX_DAYS=30,
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def test_failures(
        taxi_contractor_status_history, mocked_time, testpoint,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )
    mocked_time.set(NOW)

    from_ts = '2020-11-07 00:00:00+00'
    to_ts = '2020-11-26 15:01:00+03'

    request_contractors = [{'park_id': 'park', 'profile_id': 'profile'}]
    req = {
        'interval': {
            'from': utils.date_str_to_sec(from_ts),
            'to': utils.date_str_to_sec(to_ts),
        },
        'contractors': request_contractors,
    }
    response = await taxi_contractor_status_history.post('durations', json=req)
    assert response.status_code == 429
