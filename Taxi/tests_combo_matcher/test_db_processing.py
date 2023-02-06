import datetime

import pytest

import tests_combo_matcher.utils as utils


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize('clean_order_meta', [True, False])
@pytest.mark.parametrize('clean_matchings', [True, False])
async def test_db_cleaner_scheduling(
        taxi_combo_matcher,
        taxi_config,
        stq,
        stq_runner,
        clean_order_meta,
        clean_matchings,
):
    config = {}
    # watchdog rescheduled
    expected_tasks = []

    if clean_matchings:
        config['matchings'] = {'interval_sec': 120, 'chunk_size': 10}
        expected_tasks.append(
            {
                'queue': 'combo_matcher_db_processing',
                'id': 'matchings_cleaner_task',
                'args': [],
                'kwargs': {},
                'eta': datetime.datetime(2020, 2, 2, 0, 2),
            },
        )

    if clean_order_meta:
        config['order_meta'] = {
            'interval_sec': 180,
            'chunk_size': 3,
            'status_cleanup_settings': {},
        }
        expected_tasks.append(
            {
                'queue': 'combo_matcher_db_processing',
                'id': 'order_meta_cleaner_task',
                'args': [],
                'kwargs': {},
                'eta': datetime.datetime(2020, 2, 2, 0, 3),
            },
        )

    taxi_config.set_values({'COMBO_MATCHER_DB_CLEANER_SETTINGS': config})

    await taxi_combo_matcher.invalidate_caches()
    await taxi_combo_matcher.enable_testpoints()

    queue = stq_runner.combo_matcher_db_processing
    queue_call = stq.combo_matcher_db_processing

    # start processing
    await taxi_combo_matcher.run_task('db_cleaner_watchdog')

    # cleaner tasks in queue
    number_of_tasks = int(clean_matchings) + int(clean_order_meta)
    assert queue_call.times_called == number_of_tasks
    tasks = [queue_call.next_call() for _ in range(number_of_tasks)]

    for task in tasks:
        # workaround for testsuite reschedule
        if task['kwargs'] is not None:
            task['kwargs'].pop('log_extra')

    tasks = sorted(tasks, key=lambda x: x['id'])
    assert tasks == expected_tasks


@pytest.mark.now('2020-02-02T00:10:00+00:00')
@pytest.mark.pgsql('combo_matcher', files=['db_cleaner_setup.sql'])
@pytest.mark.config(
    COMBO_MATCHER_DB_CLEANER_SETTINGS={
        'matchings': {'interval_sec': 120, 'chunk_size': 10},
        'order_meta': {
            'interval_sec': 180,
            'chunk_size': 3,
            'status_cleanup_settings': {
                'idle': {'cleanup_ttl_sec': 400},
                'matched': {'cleanup_ttl_sec': 200},
            },
        },
    },
)
async def test_db_cleaner_tasks(
        taxi_combo_matcher, stq, stq_runner, pgsql, testpoint,
):
    @testpoint('clean_order_meta')
    def clean_order_meta(_):
        return

    # order_id1 - old idle
    # order_id2 - new idle
    # order_id3, order_id4 -> matching_id = 0
    # order_id5, order_id6 -> matching_id = 1
    # order_id3, order_id4, order_id5 - old matched
    # order_id6 - new matched

    await taxi_combo_matcher.invalidate_caches()
    await taxi_combo_matcher.enable_testpoints()

    queue = stq_runner.combo_matcher_db_processing
    queue_call = stq.combo_matcher_db_processing

    assert len(await utils.select_order_ids(pgsql)) == 6
    assert len(await utils.select_matchings(pgsql)) == 2

    # can't delete matchings now
    await queue.call(task_id='matchings_cleaner_task', kwargs={})
    assert len(await utils.select_matchings(pgsql)) == 2

    # call order_meta cleaner task - max deleted = 3
    await queue.call(task_id='order_meta_cleaner_task', kwargs={})
    assert (await utils.select_order_ids(pgsql)) == ['order_id2', 'order_id6']
    assert clean_order_meta.times_called == 2

    # can delete matching
    await queue.call(task_id='matchings_cleaner_task', kwargs={})
    assert (await utils.select_matchings(pgsql)) == [
        {'id': 0, 'orders': ['order_id5', 'order_id6'], 'performer': None},
    ]
