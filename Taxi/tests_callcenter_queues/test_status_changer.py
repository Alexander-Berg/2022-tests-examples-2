import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ('enabled', 'debug_mode', 'old_positions', 'new_positions', 'users'),
    (
        pytest.param(
            False,
            False,
            {'queues_changes_position': 0, 'status_changes_position': 0},
            {'queues_changes_position': 0, 'status_changes_position': 0},
            None,
            id='disabled',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
                        'enabled': False,  # enabled
                        'status_changes_limit': 100,
                        'queues_changes_limit': 100,
                        'period_ms': 100,
                        'debug_mode': False,  # debug_mode
                    },
                    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
                ),
            ],
        ),
        pytest.param(
            True,
            True,
            {'queues_changes_position': 0, 'status_changes_position': 0},
            {'queues_changes_position': 0, 'status_changes_position': 0},
            [],
            id='enabled_no_data_debug_mode',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
                        'enabled': True,  # enabled
                        'status_changes_limit': 100,
                        'queues_changes_limit': 100,
                        'period_ms': 100,
                        'debug_mode': True,  # debug_mode
                    },
                    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
                ),
            ],
        ),
        pytest.param(
            True,
            False,
            {'queues_changes_position': 0, 'status_changes_position': 0},
            {'queues_changes_position': 0, 'status_changes_position': 0},
            [],
            id='enabled_no_data',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
                        'enabled': True,  # enabled
                        'status_changes_limit': 100,
                        'queues_changes_limit': 100,
                        'period_ms': 100,
                        'debug_mode': False,  # debug_mode
                    },
                    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
                ),
            ],
        ),
        pytest.param(
            True,
            True,
            {'queues_changes_position': 0, 'status_changes_position': 0},
            {'queues_changes_position': 2, 'status_changes_position': 1},
            ['a', 'b'],
            id='enabled_debug_mode',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
                        'enabled': True,  # enabled
                        'status_changes_limit': 100,
                        'queues_changes_limit': 100,
                        'period_ms': 100,
                        'debug_mode': True,  # debug_mode
                    },
                    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
                ),
                pytest.mark.pgsql(
                    'callcenter_queues',
                    files=['add_target_status_and_queues.sql'],
                ),
            ],
        ),
        pytest.param(
            True,
            False,
            {'queues_changes_position': 0, 'status_changes_position': 0},
            {'queues_changes_position': 2, 'status_changes_position': 1},
            ['a', 'b'],
            id='enabled',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
                        'enabled': True,  # enabled
                        'status_changes_limit': 100,
                        'queues_changes_limit': 100,
                        'period_ms': 100,
                        'debug_mode': False,  # debug_mode
                    },
                    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
                ),
                pytest.mark.pgsql(
                    'callcenter_queues',
                    files=['add_target_status_and_queues.sql'],
                ),
            ],
        ),
    ),
)
async def test_status_changer(
        taxi_callcenter_queues,
        testpoint,
        enabled,
        debug_mode,
        old_positions,
        new_positions,
        users,
        stq,
):
    await taxi_callcenter_queues.invalidate_caches()

    @testpoint('status_changer::iteration')
    def testpoint_one_iteration(data):
        pass

    @testpoint('status_changer::old_positions')
    def testpoint_old_positions(data):
        assert data == old_positions

    @testpoint('status_changer::new_positions')
    def testpoint_new_positions(data):
        assert data == new_positions

    @testpoint('status_changer::users')
    def testpoint_users(data):
        assert set(data['users']) == set(users)

    async with taxi_callcenter_queues.spawn_task('status_changer'):
        await testpoint_old_positions.wait_call()
        if users is not None:
            await testpoint_users.wait_call()
        await testpoint_one_iteration.wait_call()
        await testpoint_new_positions.wait_call()

        if users is not None:
            if debug_mode:
                assert not stq.callcenter_queues_status_changer.times_called
            else:
                assert (
                    stq.callcenter_queues_status_changer.times_called
                    == len(users)
                )


@pytest.mark.config(
    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
        'enabled': True,  # enabled
        'status_changes_limit': 100,
        'queues_changes_limit': 100,
        'period_ms': 100,
        'debug_mode': False,  # debug_mode
    },
    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
)
@pytest.mark.pgsql(
    'callcenter_queues', files=['add_target_status_and_queues.sql'],
)
async def test_status_changer_metrics_and_db_saving(
        taxi_callcenter_queues,
        testpoint,
        taxi_callcenter_queues_monitor,
        pgsql,
):
    await taxi_callcenter_queues.invalidate_caches()

    @testpoint('status_changer::iteration')
    def testpoint_one_iteration(data):
        pass

    async with taxi_callcenter_queues.spawn_task('status_changer'):
        await testpoint_one_iteration.wait_call()
        response = await taxi_callcenter_queues_monitor.get('/')
        assert response.status_code == 200
        metrics = response.json()['status_changer']
        assert metrics['current_queues_position'] == 2
        assert metrics['current_status_position'] == 1
        assert metrics['errors']['1min'] == 0
        assert metrics['oks']['1min'] == 1
        assert metrics['tasks_created']['1min'] == 2
        assert metrics['tasks_not_created']['1min'] == 0
    async with taxi_callcenter_queues.spawn_task('status_changer'):
        await testpoint_one_iteration.wait_call()
        response = await taxi_callcenter_queues_monitor.get('/')
        assert response.status_code == 200
        metrics = response.json()['status_changer']
        assert metrics['current_queues_position'] == 2
        assert metrics['current_status_position'] == 1
        assert metrics['errors']['1min'] == 0
        assert metrics['oks']['1min'] == 2
        assert metrics['tasks_created']['1min'] == 2
        assert metrics['tasks_not_created']['1min'] == 0

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        f'SELECT queues_changes_position, status_changes_position'
        f' FROM callcenter_queues.changes_positions',
    )
    result = cursor.fetchall()
    assert result == [(2, 1)]
    cursor.close()


@pytest.mark.config(
    CALLCENTER_QUEUES_STATUS_CHANGER_SETTINGS={
        'enabled': True,  # enabled
        'status_changes_limit': 100,
        'queues_changes_limit': 100,
        'period_ms': 100,
        'debug_mode': False,  # debug_mode
    },
    CALLCENTER_STATS_USE_NEW_DATA=True,  # use_new_data_config
)
@pytest.mark.pgsql(
    'callcenter_queues', files=['add_target_status_and_queues_from_1000.sql'],
)
async def test_limiting(
        taxi_callcenter_queues,
        testpoint,
        taxi_callcenter_queues_monitor,
        pgsql,
):
    # we are at 0 0, check that we will use from 1000 as it is in db
    await taxi_callcenter_queues.invalidate_caches()

    @testpoint('status_changer::iteration')
    def testpoint_one_iteration(data):
        pass

    async with taxi_callcenter_queues.spawn_task('status_changer'):
        await testpoint_one_iteration.wait_call()
        response = await taxi_callcenter_queues_monitor.get('/')
        assert response.status_code == 200
        metrics = response.json()['status_changer']
        assert metrics['current_queues_position'] == 1001
        assert metrics['current_status_position'] == 1000
        assert metrics['errors']['1min'] == 0
        assert metrics['oks']['1min'] == 1
        assert metrics['tasks_created']['1min'] == 2
        assert metrics['tasks_not_created']['1min'] == 0

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        f'SELECT queues_changes_position, status_changes_position'
        f' FROM callcenter_queues.changes_positions',
    )
    result = cursor.fetchall()
    assert result == [(1001, 1000)]
    cursor.close()
