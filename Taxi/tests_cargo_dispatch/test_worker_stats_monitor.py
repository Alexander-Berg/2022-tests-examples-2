import pytest


def get_job_settings(worker_name: str, query_queue_size: bool):
    job_settings = {
        'disabled_pause_ms': 10000,
        'is_enabled': True,
        'launches_pause_ms': 0,
        'choose_routers_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'choose_waybills_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'create_orders_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'handle_processing_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'notify_claims_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'notify_orders_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'segments_journal_mover_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
        'waybills_journal_mover_settings': {
            'is_enabled': False,
            'query_queue_size': False,
        },
    }

    job_settings[f'{worker_name}_settings'] = {
        'is_enabled': True,
        'query_queue_size': query_queue_size,
    }

    return job_settings


async def test_no_stats(run_worker_stats_monitor):
    result = await run_worker_stats_monitor()
    assert result == {
        'choose-routers': {'queue-size': 0},
        'choose-waybills': {'queue-size': 0},
        'create-orders': {'queue-size': 0},
        'notify-claims': {'queue-size': 0},
        'notify-orders': {'queue-size': 0},
        'segments-journal-mover': {'queue-size': 0},
        'waybills-journal-mover': {'queue-size': 0},
    }


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='choose_routers', query_queue_size=False,
    ),
)
async def test_empty_config_stats_set(
        happy_path_state_first_import, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['choose-routers']['queue-size'] == 0


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='choose_routers', query_queue_size=True,
    ),
)
async def test_choose_routers_stats(
        happy_path_state_first_import, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['choose-routers']['queue-size'] == 5


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='choose_waybills', query_queue_size=True,
    ),
)
async def test_choose_waybills_stats(
        happy_path_state_all_waybills_proposed, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['choose-waybills']['queue-size'] == 2


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='create_orders', query_queue_size=True,
    ),
)
async def test_create_orders_stats(
        state_fallback_chosen, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['create-orders']['queue-size'] == 1


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='notify_claims', query_queue_size=True,
    ),
)
async def test_notify_claims_stats(
        happy_path_state_performer_found, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['notify-claims']['queue-size'] == 1


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='notify_orders', query_queue_size=True,
    ),
)
async def test_notify_orders_stats(
        happy_path_state_orders_created,
        run_worker_stats_monitor,
        pgsql,
        waybill_ref='waybill_smart_1',
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        'UPDATE cargo_dispatch.waybills '
        'SET claims_changes_version = claims_changes_version + 1 '
        'WHERE external_ref=%s',
        (waybill_ref,),
    )

    result = await run_worker_stats_monitor()
    assert result['notify-orders']['queue-size'] == 1


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='segments_journal_mover', query_queue_size=True,
    ),
)
async def test_segments_journal_mover_stats(
        happy_path_state_routers_chosen, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['segments-journal-mover']['queue-size'] == 10


@pytest.mark.config(
    CARGO_DISPATCH_WORKER_STATS_MONITOR_SETTINGS=get_job_settings(
        worker_name='waybills_journal_mover', query_queue_size=True,
    ),
)
async def test_waybills_journal_mover_stats(
        happy_path_state_all_waybills_proposed, run_worker_stats_monitor,
):
    result = await run_worker_stats_monitor()
    assert result['waybills-journal-mover']['queue-size'] == 4
