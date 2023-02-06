import pytest


def get_job_settings(enabled: bool = True, limit: int = 1000):
    return {'enabled': enabled, 'limit': limit}


async def get_buffer_events(pgsql):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
        SELECT
            segment_id, segment_revision,
            waybill_building_version, is_processed
        FROM cargo_dispatch.segments_journal_v2_buffer
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_journal_v2_events(pgsql):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
        SELECT
            segment_id, segment_revision,
            waybill_building_version, router_id
        FROM cargo_dispatch.segments_journal_v2
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def test_no_events(run_segments_journal_mover):
    result = await run_segments_journal_mover()
    assert result['stats']['processed-events-count'] == 0


async def test_routers_chosen(
        run_segments_journal_mover, happy_path_state_routers_chosen, pgsql,
):
    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('seg1', 1, 1, False),
        ('seg2', 1, 1, False),
        ('seg3', 1, 1, False),
        ('seg5', 1, 1, False),
        ('seg6', 1, 1, False),
        ('seg1', 2, 1, False),
        ('seg2', 2, 1, False),
        ('seg3', 2, 1, False),
        ('seg5', 2, 1, False),
        ('seg6', 2, 1, False),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == []

    result = await run_segments_journal_mover()
    assert result['stats']['processed-events-count'] == 10

    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('seg1', 1, 1, True),
        ('seg2', 1, 1, True),
        ('seg3', 1, 1, True),
        ('seg5', 1, 1, True),
        ('seg6', 1, 1, True),
        ('seg1', 2, 1, True),
        ('seg2', 2, 1, True),
        ('seg3', 2, 1, True),
        ('seg5', 2, 1, True),
        ('seg6', 2, 1, True),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    journal_events = sorted(journal_events, key=lambda x: (x[1], x[0], x[3]))
    assert journal_events == [
        ('seg1', 1, 1, 'fallback_router'),
        ('seg1', 1, 1, 'smart_router'),
        ('seg2', 1, 1, 'fallback_router'),
        ('seg2', 1, 1, 'smart_router'),
        ('seg3', 1, 1, 'fallback_router'),
        ('seg5', 1, 1, 'fallback_router'),
        ('seg6', 1, 1, 'fallback_router'),
        ('seg6', 1, 1, 'smart_router'),
        ('seg1', 2, 1, 'fallback_router'),
        ('seg1', 2, 1, 'smart_router'),
        ('seg2', 2, 1, 'fallback_router'),
        ('seg2', 2, 1, 'smart_router'),
        ('seg3', 2, 1, 'fallback_router'),
        ('seg5', 2, 1, 'fallback_router'),
        ('seg6', 2, 1, 'fallback_router'),
        ('seg6', 2, 1, 'smart_router'),
    ]


async def test_no_routers(
        run_segments_journal_mover, happy_path_state_first_import, pgsql,
):
    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('seg1', 1, 1, False),
        ('seg2', 1, 1, False),
        ('seg3', 1, 1, False),
        ('seg5', 1, 1, False),
        ('seg6', 1, 1, False),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == []

    result = await run_segments_journal_mover()
    assert result['stats']['processed-events-count'] == 5

    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('seg1', 1, 1, True),
        ('seg2', 1, 1, True),
        ('seg3', 1, 1, True),
        ('seg5', 1, 1, True),
        ('seg6', 1, 1, True),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == [
        ('seg1', 1, 1, None),
        ('seg2', 1, 1, None),
        ('seg3', 1, 1, None),
        ('seg5', 1, 1, None),
        ('seg6', 1, 1, None),
    ]


@pytest.mark.now('2020-04-01T10:35:01+0000')
@pytest.mark.config(
    CARGO_DISPATCH_SEGMENTS_JOURNAL_MOVER=get_job_settings(limit=2),
)
async def test_metrics(
        run_segments_journal_mover, happy_path_state_routers_chosen, pgsql,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
            UPDATE cargo_dispatch.segments_journal_v2_buffer
            SET created_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_segments_journal_mover()
    assert result['stats'] == {
        'processed-events-count': 2,
        'oldest-waybill-lag-ms': 1000,
    }


async def insert_segments_journal_buffer(
        pgsql, pkey: int, revision_addition=0,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_dispatch.segments_journal_v2_buffer
            (id, segment_id, segment_revision, waybill_building_version,
                created_ts, is_processed)
        VALUES (\'{pkey}\', 'seg1', \'{pkey + revision_addition}\',
                1, CURRENT_TIMESTAMP, False)
        """,
    )


async def flush_segments_journal_buffer(pgsql):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""
        DELETE FROM cargo_dispatch.segments_journal_v2_buffer
        WHERE is_processed = True
        """,
    )


async def test_equal_segments(
        pgsql, happy_path_state_routers_chosen, run_segments_journal_mover,
):

    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('seg1', 1, 1, False),
        ('seg2', 1, 1, False),
        ('seg3', 1, 1, False),
        ('seg5', 1, 1, False),
        ('seg6', 1, 1, False),
        ('seg1', 2, 1, False),
        ('seg2', 2, 1, False),
        ('seg3', 2, 1, False),
        ('seg5', 2, 1, False),
        ('seg6', 2, 1, False),
    ]
    await run_segments_journal_mover()
    await flush_segments_journal_buffer(pgsql)

    await insert_segments_journal_buffer(pgsql, 2, -1)
    await run_segments_journal_mover()
