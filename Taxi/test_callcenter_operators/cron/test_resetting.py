import pytest

from callcenter_operators import models
from callcenter_operators import utils
from callcenter_operators.storage.postgresql import db


async def _select_agent_status(context, internal_id):
    pool = await db.OperatorsRepo.get_ro_pool(context)

    async with pool.acquire() as conn:
        query = 'SELECT status FROM callcenter_auth.current_info WHERE id=$1'
        result = await utils.execute_query(
            query, conn, 'fetchval', internal_id,
        )
    return result


async def _select_form_opened(context, internal_id):
    pool = await db.OperatorsRepo.get_ro_pool(context)

    async with pool.acquire() as conn:
        query = """SELECT is_form_opened FROM
        callcenter_auth.current_info WHERE id=$1"""
        result = await utils.execute_query(
            query, conn, 'fetchval', internal_id,
        )
    return result


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 60,
                'connected_idle_time_cutoff': 60,  # < 10 minutes
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_connected_resetting(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    status = await _select_agent_status(cron_context, 1)
    assert status == models.Operator.CONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 1)
    assert new_status == models.Operator.DISCONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 6000,
                'connected_idle_time_cutoff': 6000,  # > 10 minutes
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_connected_not_resetting(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    status = await _select_agent_status(cron_context, 1)
    assert status == models.Operator.CONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 1)
    assert new_status == models.Operator.CONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 60,  # < 10 minutes
                'connected_idle_time_cutoff': 60,
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_paused_resetting(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000001
    status = await _select_agent_status(cron_context, 2)
    assert status == models.Operator.PAUSED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 2)
    assert new_status == models.Operator.DISCONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 6000,
                'connected_idle_time_cutoff': 6000,  # > 10 minutes
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_paused_not_resetting(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000001
    status = await _select_agent_status(cron_context, 2)
    assert status == models.Operator.PAUSED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 2)
    assert new_status == models.Operator.PAUSED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 1,
                'connected_idle_time_cutoff': 1,
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_disconnected_not_touched(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000002
    status = await _select_agent_status(cron_context, 3)
    assert status == models.Operator.DISCONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 3)
    assert new_status == models.Operator.DISCONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': False,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 60,
                'connected_idle_time_cutoff': 60,  # < 10 minutes
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_disable_all(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    status = await _select_agent_status(cron_context, 1)
    assert status == models.Operator.CONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 1)
    assert new_status == models.Operator.CONNECTED
    assert not mock_set_status_cc_queues.handle_urls.times_called
    assert not mock_save_status.handle_urls.times_called


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 60,
                'connected_idle_time_cutoff': 60,  # < 10 minutes
                'enabled': False,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_disable_queue(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    status = await _select_agent_status(cron_context, 1)
    assert status == models.Operator.CONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 1)
    assert new_status == models.Operator.CONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            '__default__': {
                'paused_idle_time_cutoff': 60,
                'connected_idle_time_cutoff': 60,  # < 10 minutes
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1', '2']},
        {'name': 'ru_taxi_help', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_resetting_with_default_rules(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    status = await _select_agent_status(cron_context, 1)
    assert status == models.Operator.CONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 1)
    assert new_status == models.Operator.DISCONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES={
        'enabled': True,
        'rules': {
            '__default__': {
                'paused_idle_time_cutoff': 60,
                'connected_idle_time_cutoff': 60,  # < 10 minutes
                'enabled': True,
            },
            'ru_taxi_disp': {
                'paused_idle_time_cutoff': 6000,
                'connected_idle_time_cutoff': 6000,  # > 10 minutes
                'enabled': True,
            },
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_taxi_disp', 'allowed_clusters': ['1', '2']},
        {'name': 'ru_taxi_help', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_not_resetting_with_rules_override(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    status = await _select_agent_status(cron_context, 1)
    assert status == models.Operator.CONNECTED
    await cron_runner.status_resetting()
    new_status = await _select_agent_status(cron_context, 1)
    assert new_status == models.Operator.CONNECTED


@pytest.mark.config(
    CALLCENTER_OPERATORS_USE_ONLY_FORM_OPENED_IN_IDLE=True,
    CALLCENTER_STATS_USE_NEW_DATA=True,
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES_NEW={
        'enabled': True,
        'cutoff': 60,  # < 10 minutes
    },
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_resetting_new(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    is_form_opened = await _select_form_opened(cron_context, 1)
    assert is_form_opened
    await cron_runner.status_resetting()
    assert mock_save_status.save_status_cc_reg.times_called
    is_form_opened = await _select_form_opened(cron_context, 1)
    assert not is_form_opened


@pytest.mark.config(
    CALLCENTER_OPERATORS_USE_ONLY_FORM_OPENED_IN_IDLE=True,
    CALLCENTER_STATS_USE_NEW_DATA=True,
    CALLCENTER_OPERATORS_AUTOMATIC_STATUS_RESETTING_RULES_NEW={
        'enabled': True,
        'cutoff': 6000,  # > 10 minutes
    },
)
@pytest.mark.now('2018-06-22 19:10:00+00')
# 10 minutes have gone since last visit
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_not_resetting_new(
        cron_runner, cron_context, mock_set_status_cc_queues, mock_save_status,
):
    # agent with id = 1000000000
    is_form_opened = await _select_form_opened(cron_context, 1)
    assert is_form_opened
    await cron_runner.status_resetting()
    assert not mock_save_status.save_status_cc_reg.times_called
    is_form_opened = await _select_form_opened(cron_context, 1)
    assert is_form_opened
