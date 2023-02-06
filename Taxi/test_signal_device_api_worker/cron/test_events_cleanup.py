import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = ['signal_device_api_worker.crontasks.events_cleanup', '-t', '0']


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_CLEANUP_SETTINGS={
        '__default__': 1,
        'lol': 10000,
        'driver_lost': 2,
        'some_other_event_type_not_in_base': 2,
    },
)
async def test_ok(mockserver, pgsql):
    async def run():
        return await run_cron.main(CRON_PARAMS)

    await run()

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT id FROM signal_device_api.events')
    assert list(db) == [(5,), (7,), (8,)]

    db.execute('SELECT file_id FROM signal_device_api.videos')
    assert list(db) == [('video_id_1',), ('video_id_42',)]

    db.execute('SELECT file_id FROM signal_device_api.photos')
    assert list(db)[0][0] == 'photo_id_42'
