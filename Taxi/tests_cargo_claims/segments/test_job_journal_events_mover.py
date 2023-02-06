import pytest

from testsuite.utils import matching


async def get_buffer_events(pgsql):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        SELECT
            segment_id, segment_revision, claim_uuid,
            segment_status, points_user_version, is_processed
        FROM cargo_claims.claim_segments_journal_v2_buffer
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_journal_v2_events(pgsql):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        SELECT
            segment_id, segment_revision, claim_uuid,
            segment_status, points_user_version
        FROM cargo_claims.claim_segments_journal_v2
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def test_no_events(
        run_journal_events_mover,
        create_segment,
        get_db_segment_ids,
        mockserver,
        pgsql,
):
    result = await run_journal_events_mover()
    assert result['stats']['processed-events-count'] == 0


async def test_one_segment_event(
        run_journal_events_mover,
        create_segment,
        get_segment_id,
        mockserver,
        pgsql,
):
    claim_info = await create_segment()

    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        (
            matching.AnyString(),
            1,
            claim_info.claim_id,
            'performer_lookup',
            1,
            False,
        ),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == []

    result = await run_journal_events_mover()
    assert result['stats']['processed-events-count'] == 1

    segment_id = await get_segment_id()
    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        (segment_id, 1, claim_info.claim_id, 'performer_lookup', 1, True),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == [
        (segment_id, 1, claim_info.claim_id, 'performer_lookup', 1),
    ]


@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_metrics(
        run_journal_events_mover,
        create_segment,
        get_segment_id,
        mockserver,
        pgsql,
):
    await create_segment()

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
            UPDATE cargo_claims.claim_segments_journal_v2_buffer
            SET created_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_journal_events_mover()
    assert result['stats'] == {
        'processed-events-count': 1,
        'oldest-event-lag-ms': 1000,
    }
