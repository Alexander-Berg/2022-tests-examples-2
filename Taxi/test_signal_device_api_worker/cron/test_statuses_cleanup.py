import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = [
    'signal_device_api_worker.crontasks.status_history_cleanup',
    '-t',
    '0',
]


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_STATUSES_CLEANUP_SETTINGS={
        'status_history_ttl_hours': 5,
        'status_history_cleanup_size': 2,
    },
)
async def test_ok(mockserver, pgsql):
    async def run():
        return await run_cron.main(CRON_PARAMS)

    await run()

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT id FROM signal_device_api.status_history')
    assert set(db) == {('xxx',), ('yyy',)}
