# pylint: disable=redefined-outer-name
import datetime
import typing as tp

import pytest

from testsuite.utils import ordered_object

from fleet_drivers_scoring.generated.cron import cron_context as context_module
from fleet_drivers_scoring.generated.cron import run_cron
import test_fleet_drivers_scoring.utils as global_utils

CONFIG_ENABLED: tp.Dict[str, tp.Any] = {
    'batch_delay': 1,
    'batch_limit': 1,
    'is_enabled': True,
    'max_batches_per_run': 1,
    'save_revisions': 1,
}


async def _run_cron_task():
    await run_cron.main(
        ['fleet_drivers_scoring.crontasks.yt_cleaner', '-t', '0'],
    )


async def _updates_count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.write_pool.fetchval(
        'SELECT COUNT(id) FROM fleet_drivers_scoring.yt_updates;',
    )


async def _update_states_count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.write_pool.fetchval(
        'SELECT COUNT(id) FROM fleet_drivers_scoring.yt_update_states;',
    )


def _patch_dates(patch, datetime_str):
    @patch('datetime.date.today')
    def _date_today():
        return datetime.datetime.fromisoformat(datetime_str)

    @patch('datetime.datetime.today')
    def _datetime_today():
        return datetime.datetime.fromisoformat(datetime_str)

    @patch('datetime.datetime.utcnow')
    def _utcnow():
        return datetime.datetime.fromisoformat(datetime_str)


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_CLEANER={**CONFIG_ENABLED, 'is_enabled': False},
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_success.sql'])
async def test_config_disabled(cron_context: context_module.Context):
    before_updates_count = await _updates_count(cron_context)
    before_update_states_count = await _update_states_count(cron_context)

    await _run_cron_task()

    after_updates_count = await _updates_count(cron_context)
    after_update_states_count = await _update_states_count(cron_context)

    assert before_updates_count == after_updates_count
    assert before_update_states_count == after_update_states_count


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_CLEANER={
        **CONFIG_ENABLED,
        'schedule': {'start_at': '12:00', 'end_at': '17:00'},
    },
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_success.sql'])
async def test_config_disable_by_schedule(
        cron_context: context_module.Context, patch,
):
    datetime_str = '2020-06-06T11:30'
    _patch_dates(patch, datetime_str)

    before_updates_count = await _updates_count(cron_context)
    before_update_states_count = await _update_states_count(cron_context)

    await _run_cron_task()

    after_updates_count = await _updates_count(cron_context)
    after_update_states_count = await _update_states_count(cron_context)

    assert before_updates_count == after_updates_count
    assert before_update_states_count == after_update_states_count


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_CLEANER={
        **CONFIG_ENABLED,
        'schedule': {'start_at': '12:00', 'end_at': '17:00'},
    },
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_success.sql'])
async def test_success(cron_context: context_module.Context, patch):
    datetime_str = '2020-06-06T12:30'
    _patch_dates(patch, datetime_str)

    @patch('taxi.yt_wrapper.YtClient.remove')
    def _remove(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.exists')
    def _exists(*args, **kwargs):
        return True

    before_updates_count = await _updates_count(cron_context)
    before_update_states_count = await _update_states_count(cron_context)

    await _run_cron_task()

    after_updates_count = await _updates_count(cron_context)
    after_update_states_count = await _update_states_count(cron_context)

    assert before_updates_count > after_updates_count
    assert before_update_states_count > after_update_states_count

    assert after_updates_count == 1
    assert after_update_states_count == 3


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_CLEANER={
        **CONFIG_ENABLED,
        'schedule': {'start_at': '12:00', 'end_at': '17:00'},
    },
)
@pytest.mark.parametrize(
    'db_state, expected_yt_updates',
    [
        (
            'test_different_names_1.sql',
            [
                {
                    'name': 'orders',
                    'path': 'path_to_table_orders',
                    'revision': '2020-06-06 02:00',
                },
                {
                    'name': 'ratings',
                    'path': 'path_to_table_ratings',
                    'revision': '2020-06-05 02:00',
                },
            ],
        ),
        (
            'test_different_names_2.sql',
            [
                {
                    'name': 'orders',
                    'path': 'path_to_table_orders2',
                    'revision': '2020-06-06 03:00',
                },
                {
                    'name': 'ratings',
                    'path': 'path_to_table_ratings',
                    'revision': '2020-06-05 02:00',
                },
            ],
        ),
    ],
)
async def test_different_names(
        cron_context: context_module.Context,
        patch,
        pgsql,
        load,
        db_state,
        expected_yt_updates,
):
    global_utils.execute_file(pgsql, load, db_state)

    datetime_str = '2020-06-06T12:30'
    _patch_dates(patch, datetime_str)

    @patch('taxi.yt_wrapper.YtClient.remove')
    def _remove(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.exists')
    def _exists(*args, **kwargs):
        return True

    await _run_cron_task()

    after_update_states_count = await _update_states_count(cron_context)
    assert after_update_states_count == 6

    yt_updates = global_utils.fetch_all_yt_updates(pgsql)
    for update in yt_updates:
        update.pop('id')
        update.pop('created_at')

    ordered_object.assert_eq(
        yt_updates, global_utils.date_parsed(expected_yt_updates), paths=[''],
    )


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_CLEANER={
        **CONFIG_ENABLED,
        'schedule': {'start_at': '12:00', 'end_at': '17:00'},
    },
)
@pytest.mark.parametrize(
    'db_state, expected_yt_updates, expected_yt_update_states',
    [
        (
            'test_dont_delete_yt_update_state_of_different_type.sql',
            [
                {
                    'name': 'high_speed_driving',
                    'revision': '2020-05-05 02:00:00',
                },
                {'name': 'passenger_tags', 'revision': '2020-05-04 02:00:00'},
            ],
            [
                {
                    'name': 'high_speed_driving',
                    'type': 'calc',
                    'revision': '2020-05-05 02:00:00',
                },
                {
                    'name': 'high_speed_driving',
                    'type': 'copy',
                    'revision': '2020-05-05 02:00:00',
                },
                {
                    'name': 'high_speed_driving',
                    'type': 'convert',
                    'revision': '2020-05-05 02:00:00',
                },
                {
                    'name': 'passenger_tags',
                    'type': 'calc',
                    'revision': '2020-05-04 02:00:00',
                },
                {
                    'name': 'passenger_tags',
                    'type': 'copy',
                    'revision': '2020-05-04 02:00:00',
                },
                {
                    'name': 'passenger_tags',
                    'type': 'convert',
                    'revision': '2020-05-04 02:00:00',
                },
            ],
        ),
    ],
)
async def test_dont_delete_yt_update_state_of_different_type(
        cron_context: context_module.Context,
        patch,
        pgsql,
        load,
        db_state,
        expected_yt_updates,
        expected_yt_update_states,
):
    global_utils.execute_file(pgsql, load, db_state)

    datetime_str = '2020-06-06T12:30'
    _patch_dates(patch, datetime_str)

    @patch('taxi.yt_wrapper.YtClient.remove')
    def _remove(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.exists')
    def _exists(*args, **kwargs):
        return True

    await _run_cron_task()

    yt_updates = global_utils.fetch_all_yt_updates(pgsql)
    yt_updates = [
        {'name': x['name'], 'revision': x['revision']} for x in yt_updates
    ]

    ordered_object.assert_eq(
        yt_updates, global_utils.date_parsed(expected_yt_updates), paths=[''],
    )

    yt_update_states = global_utils.fetch_all_yt_update_states(pgsql)
    yt_update_states = [
        {'name': x['name'], 'type': x['type'], 'revision': x['revision']}
        for x in yt_update_states
    ]

    ordered_object.assert_eq(
        yt_update_states,
        global_utils.date_parsed(expected_yt_update_states),
        paths=[''],
    )
