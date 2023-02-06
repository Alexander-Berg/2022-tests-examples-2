import datetime as dt
from typing import List

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_resets_tools as db_tools
from tests_driver_mode_subscription import scheduled_slots_tools

_NOW = '2020-05-01T12:05:00+00:00'

_DRIVER_MODE_RULES = mode_rules.patched(
    [
        mode_rules.Patch(rule_name='prev_work_mode'),
        mode_rules.Patch(rule_name='next_work_mode'),
    ],
)

_SCHEDULED_RESET_1 = db_tools.ScheduledReset(
    'parkid1',
    'uuid1',
    'test_reason',
    dt.datetime.fromisoformat('2020-04-04T05:00:00+00:00'),
    None,
)

_SCHEDULED_RESET_2 = db_tools.ScheduledReset(
    'parkid2',
    'uuid2',
    'test_reason',
    dt.datetime.fromisoformat('2020-04-04T05:00:00+00:00'),
    None,
)

_SUBSCRIPTION_TIME_PREV_MODE = {
    'prev_work_mode': {
        'tariff_zones_settings': {
            '__default__': {
                'subscription_schedule': [
                    {
                        'start': {'time': '13:00', 'weekday': 'sat'},
                        'stop': {'time': '16:00', 'weekday': 'sat'},
                    },
                ],
            },
        },
        'time_zone': 'utc',
    },
}

_SUBSCRIPTION_TIME_NEXT_MODE = {
    'next_work_mode': {
        'tariff_zones_settings': {
            '__default__': {
                'subscription_schedule': [
                    {
                        'start': {'time': '13:00', 'weekday': 'sat'},
                        'stop': {'time': '16:00', 'weekday': 'sat'},
                    },
                ],
            },
        },
        'time_zone': 'utc',
    },
}


_SUBSCRIPTION_TIME_PREV_NEXT_MODE = {
    'prev_work_mode': {
        'tariff_zones_settings': {
            '__default__': {
                'subscription_schedule': [
                    {
                        'start': {'time': '13:00', 'weekday': 'sat'},
                        'stop': {'time': '16:00', 'weekday': 'sat'},
                    },
                ],
            },
        },
        'time_zone': 'utc',
    },
    'next_work_mode': {
        'tariff_zones_settings': {
            '__default__': {
                'subscription_schedule': [
                    {
                        'start': {'time': '16:00', 'weekday': 'sat'},
                        'stop': {'time': '18:00', 'weekday': 'sat'},
                    },
                ],
            },
        },
        'time_zone': 'local',
    },
}

_SAGA_SETTINGS_ENABLE_SCHEDULE = {'enable_scheduled_resets': True}

_OFFER_IDENTITY_SLOT_ID = 'ba033cb256b544b5addfdf9cdb753297'
_OFFER_IDENTITY = {'slot_id': _OFFER_IDENTITY_SLOT_ID, 'rule_version': 1}


@pytest.mark.pgsql(
    'driver_mode_subscription',
    files=['saga_from_scheduled_reset.sql'],
    queries=[
        db_tools.insert_scheduled_resets(
            [_SCHEDULED_RESET_1, _SCHEDULED_RESET_2],
        ),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
async def test_subscription_saga_source_scheduled_mode_reset(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    assert db_tools.get_scheduled_mode_resets(pgsql) == [
        _SCHEDULED_RESET_1,
        _SCHEDULED_RESET_2,
    ]

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert db_tools.get_scheduled_mode_resets(pgsql) == [_SCHEDULED_RESET_2]


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['saga_from_manual_change.sql'],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS_ENABLE_SCHEDULE,
)
@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'expected_scheduled_resets',
    (
        pytest.param(
            [_SCHEDULED_RESET_2],
            id='delete reset from prev_mode',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets(
                            [_SCHEDULED_RESET_1, _SCHEDULED_RESET_2],
                        ),
                    ],
                ),
                pytest.mark.config(
                    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2=(
                        _SUBSCRIPTION_TIME_PREV_MODE
                    ),
                ),
            ],
        ),
        pytest.param(
            [
                db_tools.ScheduledReset(
                    park_id='parkid1',
                    driver_id='uuid1',
                    reason='subscription_time_restriction',
                    scheduled_at=dt.datetime(
                        2020, 4, 4, 16, 0, tzinfo=dt.timezone.utc,
                    ),
                ),
                _SCHEDULED_RESET_2,
            ],
            id='schedule reset',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets([_SCHEDULED_RESET_2]),
                    ],
                ),
                pytest.mark.config(
                    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2=(
                        _SUBSCRIPTION_TIME_NEXT_MODE
                    ),
                ),
            ],
        ),
        pytest.param(
            [
                db_tools.ScheduledReset(
                    park_id='parkid1',
                    driver_id='uuid1',
                    reason='subscription_time_restriction',
                    scheduled_at=dt.datetime(
                        2020, 4, 4, 15, 0, tzinfo=dt.timezone.utc,
                    ),
                ),
            ],
            id='reschedule reset',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets([_SCHEDULED_RESET_1]),
                    ],
                ),
                pytest.mark.config(
                    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2=(
                        _SUBSCRIPTION_TIME_PREV_NEXT_MODE
                    ),
                ),
            ],
        ),
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
async def test_subscription_saga_scheduled_mode_reset_by_feature(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        expected_scheduled_resets: List[db_tools.ScheduledReset],
):
    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert (
        db_tools.get_scheduled_mode_resets(pgsql) == expected_scheduled_resets
    )


_TEST_PROFILE = driver.Profile(f'parkid1_uuid1')


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        saga_tools.make_insert_saga_query(
            _TEST_PROFILE.park_id(),
            _TEST_PROFILE.profile_id(),
            next_mode='next_work_mode',
            next_mode_timepoint='2020-04-05 12:00:00+01',
            next_mode_settings=_OFFER_IDENTITY,
            prev_mode='prev_work_mode',
            prev_mode_timepoint='2020-04-05 12:00:00+01',
            prev_mode_settings={
                'slot_id': '1b488dd524d948bb8bfa65c013755a22',
                'rule_version': 2,
            },
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS_ENABLE_SCHEDULE,
)
@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'prev_mode_has_logistic_workshift, '
    'next_mode_has_logistic_workshift, '
    'expected_scheduled_resets',
    (
        pytest.param(
            True,
            False,
            [_SCHEDULED_RESET_2],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets(
                            [_SCHEDULED_RESET_1, _SCHEDULED_RESET_2],
                        ),
                    ],
                ),
            ],
            id='delete reset from prev_mode',
        ),
        pytest.param(
            False,
            True,
            [
                db_tools.ScheduledReset(
                    _TEST_PROFILE.park_id(),
                    _TEST_PROFILE.profile_id(),
                    'scheduled_slot_stop',
                    dt.datetime.fromisoformat('2020-04-05T12:00:00+00:00'),
                    _OFFER_IDENTITY_SLOT_ID,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _OFFER_IDENTITY_SLOT_ID,
                            'next_work_mode',
                            _OFFER_IDENTITY,
                            dt.datetime.fromisoformat(
                                '2020-04-05T10:00:00+00:00',
                            ),
                            dt.datetime.fromisoformat(
                                '2020-04-05T12:00:00+00:00',
                            ),
                            'some_quota',
                            1,
                        ),
                        scheduled_slots_tools.make_slot_reservation_query(
                            'next_work_mode',
                            _OFFER_IDENTITY_SLOT_ID,
                            _TEST_PROFILE,
                        ),
                    ],
                ),
            ],
            id='schedule reset from slot',
        ),
        pytest.param(
            False,
            True,
            [
                db_tools.ScheduledReset(
                    _TEST_PROFILE.park_id(),
                    _TEST_PROFILE.profile_id(),
                    'scheduled_reset_fallback',
                    dt.datetime.fromisoformat(_NOW),
                ),
            ],
            id='no slot found',
        ),
    ),
)
async def test_subscription_saga_scheduled_mode_reset_logistics(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        prev_mode_has_logistic_workshift: bool,
        next_mode_has_logistic_workshift: bool,
        expected_scheduled_resets: List[db_tools.ScheduledReset],
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode',
                    features={'logistic_workshifts': {}}
                    if next_mode_has_logistic_workshift
                    else None,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode',
                    features={'logistic_workshifts': {}}
                    if prev_mode_has_logistic_workshift
                    else None,
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        r'/(logistic-supply-conductor/internal/v1/courier/)(?P<name>.+)',
        regex=True,
    )
    def _handlers_mock(request, name):
        return {}

    scene = scenario.Scene(
        profiles={_TEST_PROFILE: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, _TEST_PROFILE)

    assert (
        db_tools.get_scheduled_mode_resets(pgsql) == expected_scheduled_resets
    )


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        db_tools.insert_scheduled_resets(
            [_SCHEDULED_RESET_1, _SCHEDULED_RESET_2],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS_ENABLE_SCHEDULE,
    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2=_SUBSCRIPTION_TIME_PREV_NEXT_MODE,
)
@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'expected_scheduled_resets, expect_error',
    (
        pytest.param(
            [_SCHEDULED_RESET_1, _SCHEDULED_RESET_2],
            False,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        saga_tools.make_insert_saga_query(
                            park_id='parkid1',
                            driver_id='uuid1',
                            next_mode='prev_work_mode',
                            next_mode_timepoint='2020-04-04 14:00:00+01',
                            next_mode_settings={'rule_id': 'next_rule'},
                            prev_mode='prev_work_mode',
                            prev_mode_timepoint='2020-04-02 13:00:00+01',
                            prev_mode_settings={'rule_id': 'prev_rule'},
                            source=saga_tools.SOURCE_SERVICE_MODE_CHANGE,
                        ),
                    ],
                ),
            ],
            id='keep reset from prev_mode',
        ),
        pytest.param(
            [_SCHEDULED_RESET_1, _SCHEDULED_RESET_2],
            True,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        saga_tools.make_insert_saga_query(
                            park_id='parkid1',
                            driver_id='uuid1',
                            next_mode='next_work_mode',
                            next_mode_timepoint='2020-04-04 14:00:00+01',
                            next_mode_settings={'rule_id': 'next_rule'},
                            prev_mode='prev_work_mode',
                            prev_mode_timepoint='2020-04-02 13:00:00+01',
                            prev_mode_settings={'rule_id': 'prev_rule'},
                            source=saga_tools.SOURCE_SERVICE_MODE_CHANGE,
                        ),
                    ],
                ),
            ],
            id='try to get tariff zone',
        ),
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
async def test_subscription_saga_scheduled_reset_keep(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
        expected_scheduled_resets: List[db_tools.ScheduledReset],
        expect_error: bool,
):
    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                'prev_work_mode', mode_settings={'rule_id': 'prev_rule'},
            ),
        },
    )
    scene.setup(mockserver, mocked_time, mock_driver_trackstory=False)
    trackstory_mock = scene.mock_driver_trackstory(
        mockserver, None, scenario.ServiceError.NoError,
    )

    await saga_tools.call_stq_saga_task(stq_runner, test_profile, expect_error)

    assert (
        db_tools.get_scheduled_mode_resets(pgsql) == expected_scheduled_resets
    )

    assert expect_error == trackstory_mock.has_calls
