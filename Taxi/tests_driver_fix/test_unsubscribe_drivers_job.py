import copy
import dataclasses

import pytest

UNSUBSCRIBE_DRIVERS_TASK = 'geobooking_drivers_unsubscriber'


JOB_DEFAULT_CONFIG = {
    'enabled': True,
    'max_tasks_count': 100,
    'work_mode': 'geobooking',
    'driver_max_offline_time_in_minutes': 10,
}


def _update_config(key, value):
    res = copy.deepcopy(JOB_DEFAULT_CONFIG)
    res[key] = value
    return res


MOCK_NOW = '2019-05-04T09:00:00+00:00'


def _check_drivers(drivers):
    assert drivers.times_called == 1
    request = drivers.next_call()['request'].json
    assert request == {'mode': {'work_mode': 'geobooking'}}


def _check_statuses(statuses, drivers, times_called=1):
    assert statuses.times_called == times_called
    if not times_called or times_called > 1:
        return
    request = statuses.next_call()['request'].json
    driver_ids = [
        {'park_id': driver.park_id, 'driver_id': driver.driver_profile_id}
        for driver in drivers
    ]
    assert request == {'driver_ids': driver_ids}


def _check_history(history, times_called=1):
    assert history.times_called == times_called
    if not times_called or times_called > 1:
        return
    request = history.next_call()['request'].json
    assert request == {
        'driver': {'park_id': 'dbid', 'driver_profile_id': 'uuid'},
        'begin_at': '1970-01-01T00:00:00+00:00',
        'end_at': '2019-05-04T09:00:00+00:00',
        'limit': 1,
        'sort': 'desc',
    }


def _check_rules_select(rules_select, rule_id=None, times_called=2):
    assert rules_select.times_called == times_called
    if not times_called or times_called > 2:
        return
    for _ in range(times_called):
        request = rules_select.next_call()['request'].json
        if 'rule_ids' in request:
            assert request == {
                'rule_ids': [rule_id],
                'types': ['geo_booking'],
                'limit': 1,
            }
        else:
            assert request == {
                'tariff_zone': 'moscow',
                'time_range': {
                    'start': '2019-05-03T21:00:00+00:00',
                    'end': '2019-05-04T09:00:00+00:00',
                },
                'is_personal': False,
                'profile_tags': ['tag1'],
                'geoarea': 'subv_zone1',
                'limit': 10,
                'types': ['geo_booking'],
            }


def _check_by_driver(
        by_driver, times_called, rule_ids=None, subscription_time=None,
):
    assert by_driver.times_called == times_called
    if not times_called or times_called > 2:
        return
    requests = [by_driver.next_call()['request'].json]
    if times_called == 2:
        requests.append(by_driver.next_call()['request'].json)

    def _make_request(end_time):
        return {
            'unique_driver_id': 'very_unique_id',
            'subvention_rule_ids': rule_ids,
            'time_range': {
                'start_time': '2019-05-03T21:00:00+00:00',
                'end_time': end_time,
            },
        }

    assert _make_request(MOCK_NOW) in requests
    if times_called == 2:
        assert _make_request(subscription_time) in requests


def _check_mode_reset(mode_reset, driver, times_called=1):
    assert mode_reset.times_called == times_called
    if not times_called or times_called > 1:
        return
    request = mode_reset.next_call()['request'].json
    expected_request = {
        'driver_profile_id': driver.driver_profile_id,
        'park_id': driver.park_id,
        'reason': 'geobooking_violations',
    }
    assert all(item in request.items() for item in expected_request.items())


@dataclasses.dataclass
class Driver:
    park_id: str
    driver_profile_id: str


@dataclasses.dataclass
class DriverStatus(Driver):
    on_order: bool


@dataclasses.dataclass
class Subscription(Driver):
    rule_id: str
    event_at: str


@dataclasses.dataclass
class ByDriverInfo:
    udid: str
    rule_id: str
    time_on_order: int
    time_free: int


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'unsubscribe,time_on_order,time_free,subscription_time',
    (
        (True, 0, 49, '2019-05-04T08:00:00+00:00'),
        (False, 0, 51, '2019-05-04T08:00:00+00:00'),
        (False, 25, 0, '2019-05-04T08:00:00+00:00'),
        (True, 0, 229, '2019-05-03T08:00:00+00:00'),
        (False, 0, 230, '2019-05-03T08:00:00+00:00'),
    ),
)
@pytest.mark.config(
    DRIVER_FIX_UNSUBSCRIBE_GEOBOOKING_DRIVERS_JOB=JOB_DEFAULT_CONFIG,
)
@pytest.mark.suspend_periodic_tasks(UNSUBSCRIBE_DRIVERS_TASK)
async def test_unsubscribe_driver_base(
        taxi_driver_fix,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe,
        time_on_order,
        time_free,
        subscription_time,
):
    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')
    mock_drivers_job_requirements.add_driver('dbid_uuid')
    mock_drivers_job_requirements.add_status(
        DriverStatus('dbid', 'uuid', on_order=False),
    )
    mock_drivers_job_requirements.add_subscription(
        Subscription('dbid', 'uuid', '_id/1', subscription_time),
    )
    mock_drivers_job_requirements.add_rules(
        load_json('rules_select_base.json'),
    )
    mock_drivers_job_requirements.add_by_driver(
        ByDriverInfo('very_unique_id', '_id/1', time_on_order, time_free),
    )

    await taxi_driver_fix.run_periodic_task(UNSUBSCRIBE_DRIVERS_TASK)
    _check_drivers(mock_drivers_job_requirements.mock_drivers)
    _check_statuses(
        mock_drivers_job_requirements.mock_statuses,
        drivers=[Driver('dbid', 'uuid')],
    )
    _check_history(mock_drivers_job_requirements.mock_history)
    _check_rules_select(
        mock_drivers_job_requirements.mock_rules_select, rule_id='_id/1',
    )
    by_driver_times_called = 1 + (
        subscription_time > '2019-05-03T21:00:00+00:00'
    )
    _check_by_driver(
        mock_drivers_job_requirements.mock_by_driver,
        rule_ids=['_id/1'],
        subscription_time=subscription_time,
        times_called=by_driver_times_called,
    )
    _check_mode_reset(
        mock_drivers_job_requirements.mock_mode_reset,
        Driver('dbid', 'uuid'),
        times_called=int(unsubscribe),
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    DRIVER_FIX_UNSUBSCRIBE_GEOBOOKING_DRIVERS_JOB=JOB_DEFAULT_CONFIG,
)
@pytest.mark.parametrize(
    'unsubscribe,time_on_order_id1,'
    'time_free_id1,time_on_order_id2,time_free_id2',
    (
        (True, 0, 25, 0, 24),
        (False, 0, 25, 0, 26),
        (False, 0, 27, 0, 24),
        (True, 10, 5, 10, 4),
        (False, 10, 5, 10, 6),
    ),
)
@pytest.mark.suspend_periodic_tasks(UNSUBSCRIBE_DRIVERS_TASK)
async def test_rule_was_replaced_during_the_day(
        taxi_driver_fix,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe,
        time_on_order_id1,
        time_free_id1,
        time_on_order_id2,
        time_free_id2,
):
    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')
    mock_drivers_job_requirements.add_driver('dbid_uuid')
    mock_drivers_job_requirements.add_status(
        DriverStatus('dbid', 'uuid', on_order=False),
    )
    mock_drivers_job_requirements.add_subscription(
        Subscription('dbid', 'uuid', '_id/2', '2019-05-04T08:30:00+00:00'),
    )
    mock_drivers_job_requirements.add_rules(
        load_json('rules_select_two_the_same_rules.json'),
    )
    mock_drivers_job_requirements.add_by_driver(
        ByDriverInfo(
            'very_unique_id', '_id/1', time_on_order_id1, time_free_id1,
        ),
    )
    mock_drivers_job_requirements.add_by_driver(
        ByDriverInfo(
            'very_unique_id', '_id/2', time_on_order_id2, time_free_id2,
        ),
    )

    await taxi_driver_fix.run_periodic_task(UNSUBSCRIBE_DRIVERS_TASK)
    _check_drivers(mock_drivers_job_requirements.mock_drivers)
    _check_statuses(
        mock_drivers_job_requirements.mock_statuses,
        drivers=[Driver('dbid', 'uuid')],
    )
    _check_history(mock_drivers_job_requirements.mock_history)
    _check_rules_select(
        mock_drivers_job_requirements.mock_rules_select, rule_id='_id/2',
    )
    _check_by_driver(
        mock_drivers_job_requirements.mock_by_driver,
        rule_ids=['_id/2', '_id/1'],
        subscription_time='2019-05-04T08:30:00+00:00',
        times_called=2,
    )
    _check_mode_reset(
        mock_drivers_job_requirements.mock_mode_reset,
        Driver('dbid', 'uuid'),
        times_called=int(unsubscribe),
    )


VALUES = [
    (True, True, 24, 1, 5, 9),
    (True, False, 15, 18, 5, 10),
    (False, True, 12, 27, 4, 11),
    (False, False, 17, 20, 7, 11),
]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'unsubscribe_1st,unsubscribe_2nd,'
    'time_on_order_1st,time_free_1st,time_on_order_2nd,time_free_2nd',
    VALUES,
)
@pytest.mark.config(
    DRIVER_FIX_UNSUBSCRIBE_GEOBOOKING_DRIVERS_JOB=(
        _update_config('max_tasks_count', 1)
    ),
)
@pytest.mark.suspend_periodic_tasks(UNSUBSCRIBE_DRIVERS_TASK)
async def test_unsubscribe_two_drivers_one_task(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe_1st,
        unsubscribe_2nd,
        time_on_order_1st,
        time_free_1st,
        time_on_order_2nd,
        time_free_2nd,
):
    await unsubscribe_two_drivers_impl(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe_1st,
        unsubscribe_2nd,
        time_on_order_1st,
        time_free_1st,
        time_on_order_2nd,
        time_free_2nd,
        max_tasks_count=1,
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'unsubscribe_1st,unsubscribe_2nd,'
    'time_on_order_1st,time_free_1st,time_on_order_2nd,time_free_2nd',
    VALUES,
)
@pytest.mark.config(
    DRIVER_FIX_UNSUBSCRIBE_GEOBOOKING_DRIVERS_JOB=(
        _update_config('max_tasks_count', 2)
    ),
)
@pytest.mark.suspend_periodic_tasks(UNSUBSCRIBE_DRIVERS_TASK)
async def test_unsubscribe_two_drivers_two_tasks(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe_1st,
        unsubscribe_2nd,
        time_on_order_1st,
        time_free_1st,
        time_on_order_2nd,
        time_free_2nd,
):
    await unsubscribe_two_drivers_impl(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe_1st,
        unsubscribe_2nd,
        time_on_order_1st,
        time_free_1st,
        time_on_order_2nd,
        time_free_2nd,
        max_tasks_count=2,
    )


async def unsubscribe_two_drivers_impl(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
        unsubscribe_1st,
        unsubscribe_2nd,
        time_on_order_1st,
        time_free_1st,
        time_on_order_2nd,
        time_free_2nd,
        max_tasks_count,
):
    unique_drivers.add_driver('dbid1', 'uuid1', 'very_unique_id1')
    unique_drivers.add_driver('dbid2', 'uuid2', 'very_unique_id2')
    mock_drivers_job_requirements.add_drivers(
        drivers=['dbid1_uuid1', 'dbid2_uuid2'],
    )
    mock_drivers_job_requirements.add_statuses(
        [
            DriverStatus('dbid1', 'uuid1', on_order=False),
            DriverStatus('dbid2', 'uuid2', on_order=False),
        ],
    )
    mock_drivers_job_requirements.add_subscription(
        Subscription('dbid1', 'uuid1', '_id/1', '2019-05-04T11:00:00+0300'),
    )
    mock_drivers_job_requirements.add_subscription(
        Subscription('dbid2', 'uuid2', '_id/1', '2019-05-04T11:30:00+0300'),
    )
    mock_drivers_job_requirements.add_rules(
        load_json('rules_select_base.json'),
    )
    mock_drivers_job_requirements.add_by_driver(
        ByDriverInfo(
            'very_unique_id1', '_id/1', time_on_order_1st, time_free_1st,
        ),
    )
    mock_drivers_job_requirements.add_by_driver(
        ByDriverInfo(
            'very_unique_id2', '_id/1', time_on_order_2nd, time_free_2nd,
        ),
    )

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/set')
    async def _mode_set(request):
        return {
            'active_mode': 'orders',
            'active_mode_type': 'display_mode',
            'active_since': MOCK_NOW,
        }

    await taxi_driver_fix.run_periodic_task(UNSUBSCRIBE_DRIVERS_TASK)
    expected_called = 2 if max_tasks_count == 1 else 1
    _check_drivers(mock_drivers_job_requirements.mock_drivers)
    _check_statuses(
        mock_drivers_job_requirements.mock_statuses,
        drivers=[Driver('dbid1', 'uuid1'), Driver('dbid2', 'uuid2')],
        times_called=expected_called,
    )
    assert (
        unique_drivers.mock_retrieve_by_profiles.times_called
        == expected_called
    )
    _check_history(mock_drivers_job_requirements.mock_history, times_called=2)
    _check_rules_select(
        mock_drivers_job_requirements.mock_rules_select, rule_id='_id/1',
    )
    _check_by_driver(
        mock_drivers_job_requirements.mock_by_driver, times_called=4,
    )
    driver = (
        Driver('dbid1', 'uuid1')
        if unsubscribe_1st
        else Driver('dbid2', 'uuid2')
    )
    _check_mode_reset(
        mock_drivers_job_requirements.mock_mode_reset,
        driver,
        times_called=int(unsubscribe_1st) + int(unsubscribe_2nd),
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    DRIVER_FIX_UNSUBSCRIBE_GEOBOOKING_DRIVERS_JOB=_update_config(
        'driver_keep_subscribed_tag',
        {'tag': 'keep_unsubscribed', 'topic': 'geobooking_topic'},
    ),
)
@pytest.mark.suspend_periodic_tasks(UNSUBSCRIBE_DRIVERS_TASK)
async def test_drivers_skipped(
        taxi_driver_fix,
        mockserver,
        load_json,
        mock_drivers_job_requirements,
        driver_tags_mocks,
):
    driver_tags_mocks.set_tags_info(
        'dbid1', 'uuid1', tags=['tag1', 'keep_unsubscribed', 'tag2'],
    )
    driver_tags_mocks.set_tags_info(
        'dbid1',
        'uuid1',
        tags_info={'keep_unsubscribed': {'topics': ['geobooking_topic']}},
    )
    mock_drivers_job_requirements.add_drivers(['dbid1_uuid1', 'dbid2_uuid2'])
    mock_drivers_job_requirements.add_statuses(
        [
            DriverStatus('dbid1', 'uuid1', on_order=False),
            DriverStatus('dbid2', 'uuid2', on_order=True),
        ],
    )

    await taxi_driver_fix.run_periodic_task(UNSUBSCRIBE_DRIVERS_TASK)
    _check_drivers(mock_drivers_job_requirements.mock_drivers)
    _check_statuses(
        mock_drivers_job_requirements.mock_statuses,
        drivers=[Driver('dbid1', 'uuid1'), Driver('dbid2', 'uuid2')],
    )
    assert driver_tags_mocks.v1_match_profiles.times_called == 1
    assert driver_tags_mocks.v1_match_profiles.next_call()['request'].json == {
        'drivers': [{'dbid': 'dbid1', 'uuid': 'uuid1'}],
        'topics': ['geobooking_topic'],
    }

    _check_history(mock_drivers_job_requirements.mock_history, times_called=0)
    _check_rules_select(
        mock_drivers_job_requirements.mock_rules_select, times_called=0,
    )
    _check_by_driver(
        mock_drivers_job_requirements.mock_by_driver, times_called=0,
    )
    _check_mode_reset(
        mock_drivers_job_requirements.mock_mode_reset,
        driver=None,
        times_called=0,
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    DRIVER_FIX_UNSUBSCRIBE_GEOBOOKING_DRIVERS_JOB=JOB_DEFAULT_CONFIG,
)
@pytest.mark.suspend_periodic_tasks(UNSUBSCRIBE_DRIVERS_TASK)
async def test_empty_rules_response(
        taxi_driver_fix,
        mockserver,
        unique_drivers,
        load_json,
        mock_drivers_job_requirements,
):
    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')
    mock_drivers_job_requirements.add_driver('dbid_uuid')
    mock_drivers_job_requirements.add_status(
        DriverStatus('dbid', 'uuid', on_order=False),
    )
    mock_drivers_job_requirements.add_subscription(
        Subscription('dbid', 'uuid', '_id/1', '2019-05-03T11:00:00+0300'),
    )
    mock_drivers_job_requirements.add_rules(
        load_json('rules_select_base.json'),
    )
    mock_drivers_job_requirements.add_by_driver(
        ByDriverInfo('very_unique_id', '_id/1', time_on_order=0, time_free=0),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def _rules_select(request):
        subventions = (
            load_json('rules_select_base.json')
            if 'rule_ids' in request.json
            else []
        )
        return {'subventions': subventions}

    await taxi_driver_fix.run_periodic_task(UNSUBSCRIBE_DRIVERS_TASK)
    _check_drivers(mock_drivers_job_requirements.mock_drivers)
    _check_statuses(
        mock_drivers_job_requirements.mock_statuses,
        drivers=[Driver('dbid', 'uuid')],
    )
    _check_history(mock_drivers_job_requirements.mock_history)
    _check_rules_select(_rules_select, rule_id='_id/1')
    _check_by_driver(
        mock_drivers_job_requirements.mock_by_driver,
        rule_ids=['_id/1'],
        times_called=0,
    )
    _check_mode_reset(
        mock_drivers_job_requirements.mock_mode_reset,
        driver=None,
        times_called=0,
    )
