import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401


CRON_PARAMS = [
    'signal_device_api_worker.crontasks.set_parks_resolutions',
    '-t',
    '0',
]


@pytest.mark.now('2019-09-16T12:00:00.0+0000')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_SET_PARKS_RESOLUTIONS_V2={
        'enabled': True,
        'park_id': 'some_park_id',
        'event_types': ['eyeclose', 'distraction', 'seatbelt'],
    },
)
async def test_ok(mockserver, pgsql):
    async def run():
        return await run_cron.main(CRON_PARAMS)

    await run()

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT COUNT(*) FROM signal_device_api.events
        WHERE event_type = 'eyeclose'
          AND resolution is not NULL
        """,
    )
    assert list(db)[0][0] == 1

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT COUNT(*) FROM signal_device_api.events
        WHERE event_type = 'distraction'
          AND resolution is not NULL
        """,
    )
    assert list(db)[0][0] == 3

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT COUNT(*) FROM signal_device_api.events
        WHERE event_type = 'seatbelt'
          AND resolution is not NULL
        """,
    )
    assert list(db)[0][0] == 1
