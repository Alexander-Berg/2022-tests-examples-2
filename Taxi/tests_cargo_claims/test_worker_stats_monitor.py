import pytest

JOB_NAME = 'cargo-claims-worker-stats-monitor'

CARGO_CLAIMS_WORKER_STATS_MONITOR = {
    'enabled': True,
    'sleep_ms': 50,
    'processing_events_stats_settings': {
        'enabled': True,
        'queue_size_stat': {'db_read_chunk_size': 1},
    },
    'journal_events_mover_settings': {'enabled': True},
    'claim_estimator_settings': {'enabled': True},
}


@pytest.mark.pgsql('cargo_claims', files=['insert_events.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_WORKER_STATS_MONITOR=CARGO_CLAIMS_WORKER_STATS_MONITOR,
)
async def test_worker_processing_events_stats(
        taxi_cargo_claims, run_worker_stats_monitor, pgsql,
):
    stats = await run_worker_stats_monitor()
    processing_events_stats = stats['processing-events']
    assert processing_events_stats['all-new-events-in-queue'] == 5

    cursor = pgsql['cargo_claims'].cursor()

    cursor.execute(
        """
            UPDATE cargo_claims.processing_events SET is_stq_set = false;
        """,
    )

    stats = await run_worker_stats_monitor()
    processing_events_stats = stats['processing-events']
    assert processing_events_stats['all-new-events-in-queue'] == 0

    cursor.execute(
        """
            UPDATE cargo_claims.processing_events SET is_stq_set = null;
        """,
    )

    stats = await run_worker_stats_monitor()
    processing_events_stats = stats['processing-events']
    assert processing_events_stats['all-new-events-in-queue'] == 10

    cursor.execute(
        """
            UPDATE cargo_claims.processing_events SET is_stq_set = true;
        """,
    )

    stats = await run_worker_stats_monitor()
    processing_events_stats = stats['processing-events']
    assert processing_events_stats['all-new-events-in-queue'] == 0


@pytest.mark.now('2020-04-01T10:35:01+0000')
@pytest.mark.config(
    CARGO_CLAIMS_WORKER_STATS_MONITOR=CARGO_CLAIMS_WORKER_STATS_MONITOR,
)
async def test_worker_journal_events_mover(
        taxi_cargo_claims, create_segment, run_worker_stats_monitor, pgsql,
):
    await create_segment()

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
            UPDATE cargo_claims.claim_segments_journal_v2_buffer
            SET created_ts='2020-04-01T10:35:00+0000'
        """,
    )

    stats = await run_worker_stats_monitor()
    journal_events_mover_stats = stats['journal-events-mover']
    assert journal_events_mover_stats['queue-size'] == 1


@pytest.mark.now('2020-04-01T10:35:01+0000')
@pytest.mark.config(
    CARGO_CLAIMS_WORKER_STATS_MONITOR=CARGO_CLAIMS_WORKER_STATS_MONITOR,
)
async def test_worker_claim_estimator(
        taxi_cargo_claims, state_controller, run_worker_stats_monitor, pgsql,
):
    await state_controller.apply(target_status='new')

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
            UPDATE cargo_claims.claims
            SET last_status_change_ts='2020-04-01T10:35:00+0000'
        """,
    )

    stats = await run_worker_stats_monitor()
    claim_estimator_stats = stats['claim-estimator']
    assert claim_estimator_stats['queue-size'] == 1
    assert claim_estimator_stats['oldest-event-lag-ms'] == 1000
