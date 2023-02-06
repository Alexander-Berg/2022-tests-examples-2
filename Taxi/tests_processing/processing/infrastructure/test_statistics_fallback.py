import pytest

# pylint: disable=redefined-outer-name
@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.mark.processing_queue_config(
    'do_nothing.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize('stats_fallback', [True, False])
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_statistics_fallback_do_nothing(
        stq,
        processing,
        statistics,
        taxi_processing,
        stats_fallback,
        use_ydb,
        use_fast_flow,
):
    if stats_fallback:
        statistics.fallbacks = [
            'processing.handler.testsuite.example.fallback-handler.fallback',
        ]
        await taxi_processing.invalidate_caches()

    item_id = '11'
    await processing.testsuite.example.send_event(
        item_id, payload={}, expect_fail=False,
    )


@pytest.mark.processing_queue_config(
    'disable_handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize('stats_fallback', [True, False])
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_statistics_fallback_disable_handler(
        stq,
        processing,
        statistics,
        taxi_processing,
        stats_fallback,
        use_ydb,
        use_fast_flow,
):
    if stats_fallback:
        statistics.fallbacks = [
            'processing.handler.testsuite.example.fallback-handler.fallback',
        ]
        await taxi_processing.invalidate_caches()

    item_id = '22'
    shared_state = await processing.testsuite.example.handle_single_event(
        item_id, payload={},
    )

    assert shared_state.get('handler-called', False) != stats_fallback


@pytest.mark.processing_queue_config(
    'run_fallback_policy.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize('stats_fallback', [True, False])
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_statistics_fallback_run_fallback_policy(
        stq,
        processing,
        statistics,
        taxi_processing,
        stats_fallback,
        use_ydb,
        use_fast_flow,
):

    if stats_fallback:
        statistics.fallbacks = [
            'processing.handler.testsuite.example.fallback-handler.fallback',
        ]
        await taxi_processing.invalidate_caches()

    item_id = '33'
    async with statistics.capture(taxi_processing) as cpt:
        await processing.testsuite.example.send_event(
            item_id, payload={}, expect_fail=stats_fallback,
        )

    assert (
        cpt.statistics.get(
            'processing.handler.testsuite.example.fallback-handler.success', 0,
        )
        != stats_fallback
    )
    assert (
        cpt.statistics.get(
            'processing.handler.testsuite.example.fallback-handler.error', 0,
        )
        == 0
    )
