import datetime
import sys


import dateutil.parser
import pytest


from tests_subvention_schedule import utils


async def update_rule_test_base(
        rules,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        updates_throws_call=None,
        check_bsx_calls=True,
        mocked_time=None,
):
    bsx.reset()

    if updates_throws_call:
        bsx.set_updates_throws_call(updates_throws_call)

    if rules:
        bsx.set_rules(load_json(rules)['rules'][0])
    bsx.set_updated_rules(load_json(closed)['rules'])

    if original_db:
        utils.load_db(pgsql, load_json(original_db), mocked_time)

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'update-schedules'},
        )
    ).status_code == (500 if updates_throws_call else 200)

    print(utils.get_affected_schedules(pgsql), file=sys.stderr)

    # process all of shards sequently in a single worker
    await taxi_subvention_schedule.run_periodic_task('update-job-sharded-0')

    assert utils.get_schedules(pgsql) == load_json(expected_db)

    if check_bsx_calls:
        assert bsx.updates.times_called == len(expected_update_calls)
        for call in expected_update_calls:
            assert bsx.updates.next_call()['request_data'].json == call

    assert utils.check_update_time_valid(pgsql)
    assert utils.get_last_updated(pgsql) == [(expected_last_updated,)]


EXPECTED_CALLS = [
    {
        'cursor': {},
        'limit': 100,
        'time_range': {
            'end': '2021-02-01T09:00:00+00:00',
            'start': '2020-01-31T21:00:00+00:00',
        },
    },
]


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    CLAMP_ITEMS_TO_DESCRIPTOR_BEGIN=True,
    UPDATE_JOB_SETTINGS={
        'update_delay': 600,
        'batch_size': 100,
        'process_updates_type': 'atomic',
        'process_descriptors_type': 'atomic',
    },
    DONT_ROUND_INVALIDATION_POINT=True,
    USE_TAGS_FOR_UPDATE=True,
)
@pytest.mark.parametrize(
    'closed, original_db, expected_db,' 'expected_last_updated',
    [
        (
            'rule_closed_no_activity.json',
            'rule_closed_no_activity_db.json',
            'rule_closed_no_activity_db_expected.json',
            '2022-01-10 09:00:00',
        ),
    ],
)
@pytest.mark.now('2022-01-10T12:10:00+0300')
async def test_schedule_close_no_activity(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        mocked_time,
):
    utils.set_last_updated(pgsql, '2019-01-31 21:00:00')
    await update_rule_test_base(
        closed,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        None,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        check_bsx_calls=False,
        mocked_time=mocked_time,
    )

    assert utils.get_affected_schedules(pgsql) == {'affected': []}
    assert utils.get_schedules(pgsql) == load_json(expected_db)


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    APPEND_NEW_TAGS_TO_AFFECTED_SCHEDULES_SETTINGS={
        'use_whitelist': False,
        'whitelist': [],
        'blacklist': [],
        'check_schedules_existense': False,
    },
)
@pytest.mark.parametrize(
    'closed, original_db, expected_db,'
    'expected_last_updated, expected_update_calls',
    [
        (
            'simple_rule_closed.json',
            'simple_rule_db_current_week.json',
            'simple_rule_db_current_week.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_closed.json',
            'simple_rule_db.json',
            'simple_rule_db.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_closed_late.json',
            'simple_rule_db.json',
            'simple_rule_db.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created.json',
            'simple_rule_db.json',
            'simple_rule_db_created.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created_early.json',
            'simple_rule_db.json',
            'expected_empty_db.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'another_zone_rule.json',
            'simple_rule_db.json',
            'simple_rule_db.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created_activity.json',
            'simple_rule_db_two_activities.json',
            'expected_db_two_new_activities.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'multiple_activity_rules.json',
            'simple_rule_db_two_activities.json',
            'expected_db_multiple_activity.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created.json',
            'simple_rule_db_2_descr.json',
            'expected_db_2_descr_created.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created.json',
            'simple_rule_db_2_descr_part_upd.json',
            'expected_db_2_descr_created.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
    ],
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_schedule(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    await update_rule_test_base(
        closed,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    APPEND_NEW_TAGS_TO_AFFECTED_SCHEDULES_SETTINGS={
        'use_whitelist': False,
        'whitelist': [],
        'blacklist': [],
        'check_schedules_existense': False,
        'attempts': 3,
    },
)
@pytest.mark.parametrize(
    'closed, original_db, expected_db,'
    'expected_last_updated, expected_update_calls, inject_error',
    [
        (
            'simple_rule_created_new_tags_moscow.json',
            'simple_rule_db_created_test_new_tags_in_moscow.json',
            'expected_db_new_tags.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
            False,
        ),
        (
            'simple_rule_created_new_tags_moscow.json',
            'simple_rule_db_created_test_new_tags_in_moscow.json',
            'expected_db_new_tags_appending_failed.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
            True,
        ),
    ],
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_schedule_new_tags(
        taxi_subvention_schedule,
        testpoint,
        pgsql,
        load_json,
        bsx,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
        inject_error,
):
    @testpoint('append_affected_with_new_tags_injected_error')
    def _testpoint_call(_):
        return {'inject_error': inject_error}

    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    await update_rule_test_base(
        closed,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_continious_updates(
        taxi_subvention_schedule, mocked_time, pgsql, load_json, bsx,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    await update_rule_test_base(
        'another_zone_rule.json',
        'another_zone_rule.json',
        'simple_rule_db.json',
        'simple_rule_db.json',
        '2021-02-01 09:00:00',
        EXPECTED_CALLS,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )

    mocked_time.sleep(600)
    await update_rule_test_base(
        'simple_rule_created_early.json',
        'simple_rule_created_early.json',
        None,
        'expected_empty_db.json',
        '2021-02-01 09:10:00',
        [
            {
                'cursor': {},
                'limit': 100,
                'time_range': {
                    'start': '2021-02-01T09:00:00+00:00',
                    'end': '2021-02-01T09:10:00+00:00',
                },
            },
        ],
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    BILLING_SUBVENTIONS_X_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 5000},
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_update_fails(taxi_subvention_schedule, pgsql, load_json, bsx):

    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    await update_rule_test_base(
        None,
        'simple_rule_2_batches.json',
        'simple_rule_db.json',
        'simple_rule_db_2_batches.json',
        '2020-01-31 21:00:00',  # eq rule updated_at
        [
            {
                'cursor': {},
                'limit': 100,
                'time_range': {
                    'start': '2020-01-31T21:00:00+00:00',
                    'end': '2021-02-01T09:00:00+00:00',
                },
            },
            {
                'limit': 100,
                'cursor': {'pos': '1'},
                'time_range': {
                    'start': '2020-01-31T21:00:00+00:00',
                    'end': '2021-02-01T09:00:00+00:00',
                },
            },
        ],
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        1,
    )

    utils.execute(
        'TRUNCATE sch.schedule_descriptiors RESTART IDENTITY CASCADE;', pgsql,
    )
    assert utils.get_schedules(pgsql) == {'descriptors': [], 'items': []}

    await update_rule_test_base(
        None,
        'simple_rule_2_batches.json',
        'simple_rule_db.json',
        'simple_rule_db_2_batches.json',
        '2021-02-01 09:00:00',
        [
            {
                'limit': 100,
                'cursor': {},
                'time_range': {
                    'end': '2021-02-01T09:00:00+00:00',
                    'start': '2020-01-31T21:00:00+00:00',
                },
            },
            {
                'limit': 100,
                'cursor': {'pos': '1'},
                'time_range': {
                    'end': '2021-02-01T09:00:00+00:00',
                    'start': '2020-01-31T21:00:00+00:00',
                },
            },
        ],
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
    )


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    UPDATE_JOB_SETTINGS={
        'update_delay': 600,
        'batch_size': 100,
        'batch_window': 61,
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_schedule_update_window(
        taxi_subvention_schedule, mockserver, pgsql,
):
    start_time = dateutil.parser.parse('2020-01-31 21:00:00')
    tz_info = datetime.timezone(datetime.timedelta(hours=0))
    start_time = start_time.replace(tzinfo=tz_info)

    @mockserver.json_handler('/billing-subventions-x/v2/rules/updates')
    async def _mock_updates(request_data):
        return {'rules': []}

    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    for i in range(0, 3):
        assert (
            await taxi_subvention_schedule.post(
                '/service/cron', json={'task_name': 'update-schedules'},
            )
        ).status_code == 200

        expected_start = start_time + datetime.timedelta(seconds=61) * i
        expected_end = expected_start + datetime.timedelta(seconds=61)
        assert _mock_updates.next_call()['request_data'].json == {
            'cursor': {},
            'limit': 100,
            'time_range': {
                'start': expected_start.isoformat(),
                'end': expected_end.isoformat(),
            },
        }

        last_updated = dateutil.parser.parse(
            utils.get_last_updated(pgsql)[0][0],
        )
        last_updated = last_updated.replace(tzinfo=tz_info)
        assert last_updated == expected_end


@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
@pytest.mark.config(
    UPDATE_JOB_SETTINGS={
        'update_delay': 600,
        'batch_size': 100,
        'number_of_workers_per_host': 1,
        'number_of_shards': 4,
    },
)
async def test_schedule_update_job_sharded_infrastructure(
        taxi_subvention_schedule, testpoint,
):
    processed_shard_indices = set()

    @testpoint('testpoint::update_job_started')
    def handle_test_point(data):
        processed_shard_indices.add(data['shard_idx'])

    await taxi_subvention_schedule.run_periodic_task('update-job-sharded-0')
    assert handle_test_point.times_called > 0

    assert processed_shard_indices == {0, 1, 2, 3}


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    UPDATE_JOB_SETTINGS={'update_delay': 600, 'batch_size': 100},
    APPEND_NEW_TAGS_TO_AFFECTED_SCHEDULES_SETTINGS={
        'use_whitelist': True,
        'whitelist': ['moscow', 'spb'],
        'blacklist': [],
        'attempts': 3,
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
@pytest.mark.parametrize(
    'original_db,updated_rules,expected_affected_schedules,inject_error',
    [
        (
            'simple_rule_db_created.json',
            'simple_rule_created_2.json',
            'simple_rule_affected_schedules.json',
            False,
        ),
        (
            'simple_rule_db_2_zones_with_tags.json',
            'simple_rule_created_new_tags.json',
            'expected_db_affected_schedules_new_tags.json',
            False,
        ),
        (
            'simple_rule_db_2_zones_with_tags.json',
            'simple_rule_created_new_tags.json',
            'expected_db_affected_schedules_new_tags_appending_failed.json',
            True,
        ),
    ],
)
async def test_store_affected_descriptor_ids(
        taxi_subvention_schedule,
        testpoint,
        pgsql,
        load_json,
        bsx,
        original_db,
        updated_rules,
        expected_affected_schedules,
        inject_error,
):
    @testpoint('append_affected_with_new_tags_injected_error')
    def _testpoint_call(_):
        return {'inject_error': inject_error}

    bsx.reset()
    bsx.set_updated_rules(load_json(updated_rules)['rules'])

    utils.load_db(pgsql, load_json(original_db))
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')

    await taxi_subvention_schedule.post(
        '/service/cron', json={'task_name': 'update-schedules'},
    )

    assert utils.get_affected_schedules(pgsql) == load_json(
        expected_affected_schedules,
    )


@pytest.mark.parametrize(
    'bsx_rules,db_before,db_after',
    [
        pytest.param(
            'simple_rule_created_affected_by_id.json',
            'simple_rule_db_affected_by_id.json',
            'expected_db_affected_by_id.json',
            id='one_affected_descriptor',
        ),
        pytest.param(
            'simple_rule_created_affected_by_id.json',
            'simple_rule_db_empty_affected_descriptor.json',
            'expected_db_empty_affected_descriptor.json',
            id='empty_affected_descriptor',
        ),
    ],
)
@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {
            'enabled': True,
            'update_period': 100,
            'number_of_shards': 1,
            'number_of_workers_per_host': 1,
        },
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
async def test_update_affected_descriptors_in_sharded_job(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        bsx_rules,
        db_before,
        db_after,
):
    bsx.reset()
    bsx.set_rules(load_json(bsx_rules)['rules'][0])

    utils.load_db(pgsql, load_json(db_before))

    # process all of shards sequently in a single worker
    await taxi_subvention_schedule.run_periodic_task('update-job-sharded-0')

    assert utils.get_schedules(pgsql) == load_json(db_after)
    assert utils.get_affected_schedules(pgsql) == {'affected': []}


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_use_new_update_cursor(
        taxi_subvention_schedule, mockserver, pgsql,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')

    @mockserver.json_handler('/billing-subventions-x/v2/rules/updates')
    async def _mock_updates(request):
        return {'rules': []}

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'update-schedules'},
        )
    ).status_code == 200

    assert _mock_updates.times_called == 1
    assert _mock_updates.next_call()['request'].json == {
        'limit': 100,
        'time_range': {
            'end': '2021-02-01T09:00:00+00:00',
            'start': '2020-01-31T21:00:00+00:00',
        },
        'cursor': {},
    }


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    UPDATE_JOB_SETTINGS={
        'update_delay': 600,
        'batch_size': 1,
        'batch_window': 61,
        'process_updates_type': 'atomic',
        'process_descriptors_type': 'non_atomic',
    },
)
@pytest.mark.parametrize(
    'updated_rules,affected_schedules',
    [
        (
            'two_rules_created.json',
            {
                'affected': [
                    [
                        'single_ride',
                        'moscow',
                        'eco',
                        '{activity}',
                        ['t1'],
                        0,
                        '2020-02-01 21:00:00',
                        '2020-02-02 21:00:00',
                    ],
                ],
            },
        ),
        (
            'two_rules_created_different_update_time.json',
            {
                'affected': [
                    [
                        'single_ride',
                        'moscow',
                        'eco',
                        '{activity}',
                        ['t1'],
                        0,
                        '2020-02-01 22:00:00',
                        '2020-02-02 21:00:00',
                    ],
                ],
            },
        ),
        (
            'two_rules_created_different_update_time_reverse.json',
            {
                'affected': [
                    [
                        'single_ride',
                        'moscow',
                        'eco',
                        '{activity}',
                        ['t1'],
                        0,
                        '2020-02-01 22:00:00',
                        '2020-02-02 21:00:00',
                    ],
                ],
            },
        ),
    ],
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
async def test_affected_schedules_duplicates(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        updated_rules,
        affected_schedules,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    utils.load_db(pgsql, load_json('simple_rule_db.json'))

    bsx.reset()
    bsx.set_updated_rules(load_json(updated_rules)['rules'])

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'update-schedules'},
        )
    ).status_code == 200

    assert utils.get_affected_schedules(pgsql) == affected_schedules


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=[]),
        pytest.param(
            marks=[
                pytest.mark.config(
                    UPDATE_JOB_SETTINGS={
                        'update_delay': 600,
                        'batch_size': 100,
                        'process_updates_type': 'atomic',
                        'process_descriptors_type': 'atomic',
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    DONT_ROUND_INVALIDATION_POINT=True,
)
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
@pytest.mark.parametrize(
    'closed, original_db, expected_db,'
    'expected_last_updated, expected_update_calls',
    [
        (
            'simple_rule_created_mid_week.json',
            'simple_rule_db_2.json',
            'simple_rule_db_created_mid_week.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created.json',
            'simple_rule_db.json',
            'simple_rule_db_created.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created_early.json',
            'simple_rule_db.json',
            'expected_empty_db_opt.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created_activity.json',
            'simple_rule_db_two_activities.json',
            'expected_db_two_new_activities.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'multiple_activity_rules.json',
            'simple_rule_db_two_activities.json',
            'expected_db_multiple_activity_opt.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created.json',
            'simple_rule_db_2_descr.json',
            'expected_db_2_descr_created.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
        (
            'simple_rule_created.json',
            'simple_rule_db_2_descr_part_upd.json',
            'expected_db_2_descr_created.json',
            '2021-02-01 09:00:00',
            EXPECTED_CALLS,
        ),
    ],
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_new_invalidation_point(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    await update_rule_test_base(
        closed,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        None,
        True,
    )


@pytest.mark.config(
    UPDATE_JOB_SETTINGS={'update_delay': 600, 'batch_size': 100},
    SUBVENTION_SCHEDULE_RPS_LIMITER_SETTINGS_V2=utils.RPS_LIMITER_CONFIG,
)
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
@pytest.mark.now('2021-02-02T12:10:00+0300')
async def test_rps_limiter_type(
        taxi_subvention_schedule, pgsql, load_json, bsx, testpoint,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')

    bsx.reset()
    bsx.set_rules(
        load_json('simple_rule_created_affected_by_id.json')['rules'][0],
    )

    utils.load_db(pgsql, load_json('simple_rule_db_affected_by_id.json'))

    used_limiter = []

    @testpoint('testpoint::add_limiter_call')
    def _add_limiter_call(data):
        nonlocal used_limiter
        used_limiter.append(data['queue_name'])

    await taxi_subvention_schedule.run_periodic_task('update-job-sharded-0')
    assert used_limiter == ['rules_select_limiter', 'rules_match_limiter']


@pytest.mark.parametrize(
    'bsx_rules,db_before',
    [
        pytest.param(
            'simple_rule_created_affected_by_id.json',
            'test_error_drop_db.json',
            id='one_affected_descriptor',
        ),
    ],
)
@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {
            'enabled': True,
            'update_period': 100,
            'number_of_shards': 1,
            'number_of_workers_per_host': 1,
        },
    },
    CLAMP_ITEMS_TO_DESCRIPTOR_BEGIN=True,
    DROP_SCHEDULE_ON_UPDATE_CONFLICT_SETTINGS={
        'enabled': True,
        'drop_every': 1,
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
async def test_drop_schedules_fallback(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        bsx_rules,
        db_before,
        testpoint,
):
    bsx.reset()
    bsx.set_rules(load_json(bsx_rules)['rules'][0])

    utils.load_db(pgsql, load_json(db_before))

    @testpoint('atomic::drop_scheudles')
    def _inject_error(data):
        return {'do_drop': True}

    # process all of shards sequently in a single worker
    await taxi_subvention_schedule.run_periodic_task('update-job-sharded-0')

    assert utils.get_affected_schedules(pgsql) == {'affected': []}
    assert utils.get_schedules(pgsql) == {'descriptors': [], 'items': []}
