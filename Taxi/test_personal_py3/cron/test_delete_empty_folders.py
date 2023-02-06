from personal_py3.generated.cron import run_cron


async def test_delete_empty_folders(yt_client, yt_apply, cron_context):
    service_path = '//home/taxi/unittests/services/personal-py3/'
    yt_client.mkdir(service_path + 'TESTTICKET-2', recursive=True)
    await run_cron.main(
        ['personal_py3.crontasks.delete_empty_folders', '-t', '0'],
    )
    get_expired_folders = cron_context.postgres_queries[
        'get_expired_folders.sql'
    ]
    rows = await cron_context.pg.master_pool.fetch(get_expired_folders)
    assert len(rows) == 2
    assert not yt_client.exists(service_path + 'TESTTICKET-2')
