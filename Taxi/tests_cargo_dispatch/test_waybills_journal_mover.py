import pytest


def get_job_settings(enabled: bool = True, limit: int = 1000):
    return {'enabled': enabled, 'limit': limit}


async def get_buffer_events(pgsql):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
        SELECT
            external_ref, router_id, waybill_revision, is_processed
        FROM cargo_dispatch.waybills_journal_v2_buffer
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def get_journal_v2_events(pgsql):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
        SELECT
            external_ref, router_id, waybill_revision
        FROM cargo_dispatch.waybills_journal_v2
        ORDER BY id
        """,
    )
    return cursor.fetchall()


async def test_no_events(run_waybills_journal_mover):
    result = await run_waybills_journal_mover()
    assert result['stats']['processed-events-count'] == 0


async def test_waybills_proposed(
        run_waybills_journal_mover,
        happy_path_state_fallback_waybills_proposed,
        pgsql,
):
    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('waybill_fb_1', 'fallback_router', 1, False),
        ('waybill_fb_2', 'fallback_router', 1, False),
        ('waybill_fb_3', 'fallback_router', 1, False),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == []

    result = await run_waybills_journal_mover()
    assert result['stats']['processed-events-count'] == 3

    buffer_events = await get_buffer_events(pgsql)
    assert buffer_events == [
        ('waybill_fb_1', 'fallback_router', 1, True),
        ('waybill_fb_2', 'fallback_router', 1, True),
        ('waybill_fb_3', 'fallback_router', 1, True),
    ]

    journal_events = await get_journal_v2_events(pgsql)
    assert journal_events == [
        ('waybill_fb_1', 'fallback_router', 1),
        ('waybill_fb_2', 'fallback_router', 1),
        ('waybill_fb_3', 'fallback_router', 1),
    ]


@pytest.mark.now('2020-04-01T10:35:01+0000')
@pytest.mark.config(
    CARGO_DISPATCH_WAYBILLS_JOURNAL_MOVER=get_job_settings(limit=2),
)
async def test_metrics(
        run_waybills_journal_mover,
        happy_path_state_fallback_waybills_proposed,
        pgsql,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
            UPDATE cargo_dispatch.waybills_journal_v2_buffer
            SET created_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_waybills_journal_mover()
    assert result['stats'] == {
        'processed-events-count': 2,
        'oldest-waybill-lag-ms': 1000,
    }
