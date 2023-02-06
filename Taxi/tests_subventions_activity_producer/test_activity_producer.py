import pytest

from tests_subventions_activity_producer import common
from tests_subventions_activity_producer import pg_helpers
from tests_subventions_activity_producer import redis_helpers


def _sort_activity_events_unsent(events):
    def _get_key(event):
        activity_event = event['activity_event']
        return (
            activity_event['start']
            + activity_event['dbid']
            + activity_event['uuid']
        )

    return sorted(events, key=_get_key)


def _check_activity_events_unsent(
        load_json, pgsql, datafiles_expected_by_shard,
):
    for i, datafile in enumerate(datafiles_expected_by_shard):
        expected = _sort_activity_events_unsent(load_json(datafile))
        schema = 'shard{}'.format(i)
        actual = _sort_activity_events_unsent(
            pg_helpers.get_activity_events_unsent(pgsql, schema),
        )
        assert expected == actual, 'Unexpected data for shard #{}'.format(i)


def _check_raw_events_grouped(pgsql, expected_by_shard):
    for i, expected in enumerate(expected_by_shard):
        schema = 'shard{}'.format(i)
        actual = pg_helpers.get_raw_driver_events_grouped(pgsql, schema)
        assert expected == actual, 'Unexpected data for shard #{}'.format(i)


@pytest.mark.parametrize(
    'additional_settings,init_raw_events_grouped_docs,'
    'expected_activity_events_docs,expected_raw_events_grouped_docs',
    [
        pytest.param(
            # additional_settings
            dict(),
            # init_raw_events_grouped_docs
            [
                'common_init_raw_events_grouped_shard0.json',
                'common_init_raw_events_grouped_shard1.json',
            ],
            # expected_activity_events_docs
            [
                'common_expected_activity_events_shard0.json',
                'common_expected_activity_events_shard1.json',
            ],
            # expected_raw_events_grouped_docs
            [[], []],
            id='common',
            marks=[pytest.mark.now('2020-02-03T10:39:00+00:00')],
        ),
        pytest.param(
            # additional_settings
            dict(),
            # init_raw_events_grouped_docs
            [
                'different_intervals_init_raw_events_grouped_shard0.json',
                'different_intervals_init_raw_events_grouped_shard1.json',
            ],
            # expected_activity_events
            [
                'different_intervals_expected_activity_events_shard0.json',
                'different_intervals_expected_activity_events_shard1.json',
            ],
            # expected_raw_events_grouped
            [[], []],
            id='different_intervals',
            marks=[pytest.mark.now('2020-02-03T10:45:35+00:00')],
        ),
        pytest.param(
            # additional_settings
            dict(),
            # init_raw_events_grouped_docs
            [
                'multiple_zones_init_raw_events_grouped_shard0.json',
                'multiple_zones_init_raw_events_grouped_shard1.json',
            ],
            # expected_activity_events
            [
                'multiple_zones_expected_activity_events_shard0.json',
                'multiple_zones_expected_activity_events_shard1.json',
            ],
            # expected_raw_events_grouped
            [[], []],
            id='multiple_zones',
            marks=[pytest.mark.now('2020-02-03T10:39:00+00:00')],
        ),
        pytest.param(
            # additional_settings
            {},
            # init_raw_events_grouped_docs
            [
                'add_billing_types_init_raw_events_grouped_all_shards.json',
                'add_billing_types_init_raw_events_grouped_all_shards.json',
            ],
            # expected_activity_events_docs
            [
                'add_billing_types_expected_activity_events_all_shards.json',
                'add_billing_types_expected_activity_events_all_shards.json',
            ],
            # expected_raw_events_grouped_docs
            [[], []],
            id='add_billing_types',
            marks=[pytest.mark.now('2020-02-03T10:39:00+00:00')],
        ),
    ],
)
@common.suspend_all_periodic_tasks
async def test_activity_producer(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        additional_settings,
        init_raw_events_grouped_docs,
        expected_activity_events_docs,
        expected_raw_events_grouped_docs,
):
    pg_helpers.init_raw_driver_events_grouped(
        load_json, pgsql, datafiles_by_shard=init_raw_events_grouped_docs,
    )

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer, taxi_config, **additional_settings,
    )

    _check_activity_events_unsent(
        load_json,
        pgsql,
        datafiles_expected_by_shard=expected_activity_events_docs,
    )

    _check_raw_events_grouped(
        pgsql, expected_by_shard=expected_raw_events_grouped_docs,
    )


def _build_df_constraints_on_tags(
        violate_tags, apply_tags, is_frozen_timer_restriction,
):
    dct = {
        'violate_if': violate_tags,
        'should_freeze_timer': is_frozen_timer_restriction,
    }
    if apply_tags is not None:
        dct['apply_if'] = apply_tags
    return {'test_constraint': dct}


@pytest.mark.parametrize(
    'blocker_enabled,blocked_tags,workmodes,driver_workmodes,'
    'df_constraints_enabled,df_block_if,df_apply_if,df_should_freeze_timer,'
    'expected_status',
    [
        (
            False,  # blocker_enabled
            ['blocked_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['blocked_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'blocked',  # expected_status
        ),
        (
            False,  # blocker_enabled
            [],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            [],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag', 'blocked_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'blocked',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag', 'blocked_tag'],  # blocked_tags
            ['some_other_workmode'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            False,  # df_constraints_enabled
            [],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            ['blocked_tag'],  # df_block_if
            None,  # df_apply_if
            True,  # df_should_freeze_timer
            'blocked',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['not_driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            ['blocked_tag'],  # df_block_if
            None,  # df_apply_if
            True,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            ['blocked_tag'],  # df_block_if
            None,  # df_apply_if
            False,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            ['blocked_tag'],  # df_block_if
            ['fixer'],  # df_apply_if
            True,  # df_should_freeze_timer
            'blocked',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            ['blocked_tag'],  # df_block_if
            ['not_fixer'],  # df_apply_if
            True,  # df_should_freeze_timer
            'free',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            {'all_of': ['blocked_tag']},  # df_block_if
            {'any_of': ['fixer']},  # df_apply_if
            True,  # df_should_freeze_timer
            'blocked',  # expected_status
        ),
        (
            True,  # blocker_enabled
            ['wrong_tag'],  # blocked_tags
            ['driver_fix', 'geo_booking'],  # workmodes
            ['driver_fix'],  # driver_workmodes
            True,  # df_constraints_enabled
            None,  # df_block_if
            {'any_of': ['fixer', 'wrong_tag']},  # df_apply_if
            True,  # df_should_freeze_timer
            'blocked',  # expected_status
        ),
    ],
)
@pytest.mark.now('2020-02-03T10:39:00+00:00')
@common.suspend_all_periodic_tasks
async def test_blocker_tags(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        blocker_enabled,
        blocked_tags,
        workmodes,
        driver_workmodes,
        df_constraints_enabled,
        df_block_if,
        df_apply_if,
        df_should_freeze_timer,
        expected_status,
):
    taxi_config.set_values(
        {
            'SUBVENTIONS_ACTIVITY_PRODUCER_BLOCKER_TAGS': {
                'enabled': blocker_enabled,
                'enable_blocking_by_driver_fix_constraints_on_tags': (
                    df_constraints_enabled
                ),
                'tags': blocked_tags,
                'workmodes': workmodes,
            },
            'DRIVER_FIX_CONSTRAINTS_ON_TAGS': _build_df_constraints_on_tags(
                df_block_if, df_apply_if, df_should_freeze_timer,
            ),
        },
    )

    raw_event = load_json('init_raw_event_prototype.json')
    raw_event['driver_data']['billing_types'] = driver_workmodes

    pg_helpers.prepare_raw_driver_events(pgsql, 'shard0', docs=[raw_event])

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer, taxi_config,
    )

    for schema in ['shard0']:
        activity_events = pg_helpers.get_activity_events_unsent(pgsql, schema)
        assert activity_events != []
        for event in activity_events:
            activities = event['activity_event']['activities']
            assert activities != []
            for act in activities:
                assert act['status'] == expected_status


@pytest.mark.now('2020-02-03T10:45:35+00:00')
@common.suspend_all_periodic_tasks
async def test_activity_producer_exceed_db_max_size(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
):
    pg_helpers.init_raw_driver_events_grouped(
        load_json, pgsql, datafiles_by_shard=['init_raw_events_grouped.json'],
    )

    pg_helpers.init_activity_events_unsent(
        load_json,
        pgsql,
        datafiles_by_shard=['init_activity_events_unsent.json'],
    )

    @testpoint(
        'postgresql-subventions-activity-producer'
        ':shard0-activity_producer-task',
    )
    def _mock_producer_shard0(request):
        return {}

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        time_diff=15,
        db_activity_events_unsent_max_size=3,
    )

    assert _mock_producer_shard0.times_called == 0


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'additional_settings,init_redis_doc,'
    'expected_activity_events_docs,expected_redis_doc',
    [
        pytest.param(
            # additional_settings
            dict(),
            # init_redis_doc
            'common_init_redis.json',
            # expected_activity_events_docs
            [
                'common_expected_activity_events_shard0.json',
                'common_expected_activity_events_shard1.json',
            ],
            # expected_redis_doc
            None,
            id='common',
        ),
        pytest.param(
            # additional_settings
            {'aggregate_delay_ms': 10000},
            # init_redis_doc
            'respect_updated_at_init_redis.json',
            # expected_activity_events_docs
            [
                'respect_updated_at_expected_activity_events_shard0.json',
                'respect_updated_at_expected_activity_events_shard1.json',
            ],
            # expected_redis_doc
            'respect_updated_at_expected_redis.json',
            id='respect_updated_at',
        ),
        pytest.param(
            # additional_settings
            {},
            # init_redis_doc
            'add_billing_types_init_redis.json',
            # expected_activity_events_docs
            [
                'add_billing_types_expected_activity_events_all_shards.json',
                'add_billing_types_expected_activity_events_all_shards.json',
            ],
            # expected_redis_doc
            None,
            id='add_billing_types',
        ),
    ],
)
@pytest.mark.now('2020-02-03T10:39:00+00:00')
@common.suspend_all_periodic_tasks
async def test_activity_producer_redis(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        redis_store,
        additional_settings,
        init_redis_doc,
        expected_activity_events_docs,
        expected_redis_doc,
):
    redis_helpers.prepare_storage(redis_store, load_json(init_redis_doc))

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        enable_redis=True,
        **additional_settings,
    )

    _check_activity_events_unsent(
        load_json,
        pgsql,
        datafiles_expected_by_shard=expected_activity_events_docs,
    )

    if expected_redis_doc is None:
        assert redis_helpers.get_dbsize(redis_store) == 0
    else:
        expected_redis = load_json(expected_redis_doc)
        actual_redis = redis_helpers.get_state_as_doc(redis_store)
        assert expected_redis == actual_redis


@pytest.mark.parametrize(
    'init_raw_events_grouped_docs,init_incomplete_event_groups,'
    'expected_incomplete_event_groups',
    [
        pytest.param(
            # init_raw_events_grouped_docs
            [
                'init_raw_event_groups_incomplete.json',
                'init_raw_event_groups_incomplete.json',
            ],
            # init_incomplete_event_groups
            None,
            # expected_incomplete_event_groups
            [
                'expected_incomplete_event_groups.json',
                'expected_incomplete_event_groups.json',
            ],
            id='incomplete_events_basic',
        ),
        pytest.param(
            # init_raw_events_grouped_docs
            [
                'init_raw_event_groups_incomplete.json',
                'init_raw_event_groups_incomplete.json',
            ],
            # init_incomplete_event_groups
            [
                'init_incomplete_event_groups_same.json',
                'init_incomplete_event_groups_same.json',
            ],
            # expected_incomplete_event_groups
            [
                'expected_incomplete_event_groups_same.json',
                'expected_incomplete_event_groups_same.json',
            ],
            id='incomplete_events_with_repetition',
        ),
    ],
)
@common.suspend_all_periodic_tasks
async def test_incomplete_events(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        init_raw_events_grouped_docs,
        init_incomplete_event_groups,
        expected_incomplete_event_groups,
):
    pg_helpers.init_raw_driver_events_grouped(
        load_json, pgsql, datafiles_by_shard=init_raw_events_grouped_docs,
    )

    if init_incomplete_event_groups is not None:
        pg_helpers.init_incomplete_event_groups(
            load_json, pgsql, init_incomplete_event_groups,
        )

    additional_settings = {
        'destinations': ['activity_events_unsent', 'incomplete_events'],
    }

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        enable_redis=True,
        **additional_settings,
    )

    expected, actual = pg_helpers.extract_incomplete_event_groups(
        load_json, pgsql, expected_incomplete_event_groups,
    )
    assert expected == actual


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'additional_settings,init_redis_doc,expected_activity_events_docs,'
    'expected_incomplete_event_groups',
    [
        pytest.param(
            # additional_settings
            {'destinations': ['activity_events_unsent', 'incomplete_events']},
            # init_redis_doc
            'init_redis_incomplete.json',
            # expected_activity_events_docs
            None,
            # expected_incomplete_event_groups
            [
                'expected_incomplete_event_groups_shard0.json',
                'expected_incomplete_event_groups_shard1.json',
            ],
            id='incomplete_events',
        ),
        pytest.param(
            # additional_settings
            {
                'gather_info_across_event_group_in_redis': True,
                'destinations': [
                    'activity_events_unsent',
                    'incomplete_events',
                ],
            },
            # init_redis_doc
            'init_redis_incomplete_fixable.json',
            # expected_activity_events_docs
            [
                'expected_activity_events_fixed.json',
                'expected_activity_events_fixed.json',
            ],
            # expected_incomplete_event_groups
            None,
            id='incomplete_events_fixable',
        ),
    ],
)
@pytest.mark.now('2020-02-03T10:39:00+00:00')
@common.suspend_all_periodic_tasks
async def test_incomplete_events_redis(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        redis_store,
        additional_settings,
        init_redis_doc,
        expected_activity_events_docs,
        expected_incomplete_event_groups,
):
    redis_helpers.prepare_storage(redis_store, load_json(init_redis_doc))

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        enable_redis=True,
        **additional_settings,
    )

    if expected_activity_events_docs is not None:
        _check_activity_events_unsent(
            load_json,
            pgsql,
            datafiles_expected_by_shard=expected_activity_events_docs,
        )

    if expected_incomplete_event_groups is not None:
        expected, actual = pg_helpers.extract_incomplete_event_groups(
            load_json, pgsql, expected_incomplete_event_groups,
        )
        assert expected == actual

    assert redis_helpers.get_dbsize(redis_store) == 0


@pytest.mark.servicetest
@pytest.mark.now('2020-02-03T10:40:00+00:00')
@common.suspend_all_periodic_tasks
async def test_activity_producer_redis_migration(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        redis_store,
):
    redis_helpers.prepare_storage(
        redis_store, load_json('migrated_init_redis.json'),
    )

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        enable_redis=True,
        destinations=['activity_events_unsent', 'incomplete_events'],
    )

    _check_activity_events_unsent(
        load_json,
        pgsql,
        datafiles_expected_by_shard=[
            'migrated_expected_activity_events_shard0.json',
            'migrated_expected_activity_events_shard1.json',
        ],
    )

    expected, actual = pg_helpers.extract_incomplete_event_groups(
        load_json,
        pgsql,
        [
            'empty_shard.json',
            'migrated_expected_incomplete_event_groups_shard1.json',
        ],
    )
    assert expected == actual

    assert redis_helpers.get_dbsize(redis_store) == 0
