from fleet_fines.generated.cron import cron_context as context_module


async def test_cursor(cron_context: context_module.Context):
    job_id1 = 'JOB_ID1'
    # Starts at 0
    value11 = await cron_context.pg_access.cursor.get_cursor(job_id1)
    assert value11 is None
    # Stores given
    await cron_context.pg_access.cursor.set_cursor(job_id1, '10')
    value12 = await cron_context.pg_access.cursor.get_cursor(job_id1)
    assert value12 == '10'
    await cron_context.pg_access.cursor.set_cursor(job_id1, '20')
    value13 = await cron_context.pg_access.cursor.get_cursor(job_id1)
    assert value13 == '20'
    # Doesn't interfere
    job_id2 = 'JOB_ID2'
    value21 = await cron_context.pg_access.cursor.get_cursor(job_id2)
    assert value21 is None
