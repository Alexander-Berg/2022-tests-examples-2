import pytest


@pytest.mark.parametrize(
    'use_cold_store,sim_fail,expect_yt_targets_usage',
    (
        pytest.param(
            True,
            True,
            1,
            marks=[
                pytest.mark.processing_queue_config(
                    'replication-enabled.yaml',
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
        pytest.param(
            False,
            False,
            0,
            marks=[
                pytest.mark.processing_queue_config(
                    'replication-disabled.yaml',
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
    ),
)
async def test_replication_enabled_but_failed(
        processing,
        testpoint,
        use_cold_store,
        sim_fail,
        expect_yt_targets_usage,
):
    @testpoint('default-testpoint')
    def default_testpoint(data):
        pass

    @testpoint('GetReplicationState_yt_targets_cache')
    def yt_targets_cache_testpoint(data):
        return {'fail': sim_fail}

    event_id = await processing.testsuite.example.send_event(
        item_id='123', payload={}, idempotency_token='foo',
    )
    assert event_id
    assert yt_targets_cache_testpoint.times_called == expect_yt_targets_usage
    assert default_testpoint.times_called == 1
