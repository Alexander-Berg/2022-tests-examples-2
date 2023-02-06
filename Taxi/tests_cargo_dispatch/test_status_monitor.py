import pytest


STATISTICS_STATUS_MONITOR = 'statistics-status-monitor'


@pytest.fixture(name='run_status_monitor')
def _run_status_monitor(run_task_once):
    async def wrapper():
        return await run_task_once(STATISTICS_STATUS_MONITOR)

    return wrapper


def get_config(*, with_ttl, segment_statuses=None, waybill_statuses=None):
    config = {
        'enabled': True,
        'job-throttling-delay-ms': 0,
        'time-range': 120,
        'pg-timeout-ms': 1000,
        'segment-non-terminal-statuses': ['new', 'routers_chosen'],
        'waybill-non-terminal-statuses': [
            'new',
            'ready_for_gambling',
            'accepted',
        ],
    }
    if with_ttl:
        config['ttl'] = 10
    if segment_statuses:
        config['segment-non-terminal-statuses'] = segment_statuses
    if waybill_statuses:
        config['waybill-non-terminal-statuses'] = waybill_statuses

    return config.copy()


class PositiveNumber:
    def __eq__(self, other):
        return other > 0


@pytest.mark.config(CARGO_DRAGON_STATUS_MONITOR=get_config(with_ttl=False))
async def test_nonterminal_statuses(
        happy_path_state_fallback_waybills_proposed, run_status_monitor,
):
    result = await run_status_monitor()
    assert result['s']['dur'] == {
        'new': 0.0,
        'routers_chosen': PositiveNumber(),
    }
    assert result['w']['dur'] == {
        'new': PositiveNumber(),
        'ready_for_gambling': PositiveNumber(),
        'accepted': 0.0,
    }


@pytest.mark.config(
    CARGO_DRAGON_STATUS_MONITOR=get_config(
        with_ttl=False,
        segment_statuses=['new'],
        waybill_statuses=['accepted'],
    ),
)
async def test_mappings(
        happy_path_state_fallback_waybills_proposed, run_status_monitor,
):
    result = await run_status_monitor()
    assert result['s']['dur'] == {'new': 0.0}
    assert result['w']['dur'] == {'accepted': 0.0}


@pytest.mark.config(CARGO_DRAGON_STATUS_MONITOR=get_config(with_ttl=False))
async def test_status_lags_processed(
        happy_path_state_orders_created, run_status_monitor, pgsql,
):
    result = await run_status_monitor()

    assert result['segments_wait_for_resolution_lags_count'] == 3
    assert result['waybills_processing_lags_count'] == 2


@pytest.mark.config(CARGO_DRAGON_STATUS_MONITOR=get_config(with_ttl=False))
async def test_status_lags_cursor_stored(
        happy_path_state_orders_created, run_status_monitor, cursors_storage,
):
    await run_status_monitor()

    assert int(cursors_storage('sm_segments_wait_for_resolution')) > 0
    assert int(cursors_storage('sm_waybills_processing')) > 0
