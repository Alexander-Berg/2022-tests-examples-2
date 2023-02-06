from taxi.scripts import cron_run


async def test_dummy_run():
    # test on compatibility with taxi.maintenance.run.run
    await cron_run.main(
        ['taxi.scripts.execute', '-p', 'test_project', '-l', 'test-log-ident'],
    )
