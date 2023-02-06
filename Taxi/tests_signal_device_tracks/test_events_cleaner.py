import pytest


@pytest.mark.pgsql('signal_device_tracks', files=['test_data.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_CLEANUP_SETTINGS={
        '__default__': 1,
        'lol': 10000,
        'driver_lost': 2,
        'some_other_event_type_not_in_base': 2,
    },
    SIGNAL_DEVICE_TRACKS_EVENTS_CLEANUP_TASK_SETTINGS={
        'enabled': True,
        'task_delay_secs': 0,
        'events_cleanup_batch': 100,
    },
)
async def test_ok(testpoint, pgsql, taxi_signal_device_tracks):
    @testpoint('events-cleaner-ok-testpoint')
    def ok_testpoint(arg):
        pass

    async with taxi_signal_device_tracks.spawn_task('signalq-events-cleaner'):
        await ok_testpoint.wait_call()

    db = pgsql['signal_device_tracks'].cursor()
    db.execute(
        'SELECT event_id FROM signal_device_tracks.events ORDER BY event_id',
    )
    assert list(db) == [
        ('0ef0466e6e1331b3a7d35c5859830666',),
        ('0ef0466e6e1331b3a7d35c5859830777',),
        ('d68841a1f4b7816b84ccf4fcb7d886f7',),
    ]


@pytest.mark.pgsql('signal_device_tracks', files=['test_data.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_TRACKS_EVENTS_CLEANUP_TASK_SETTINGS={
        'enabled': False,
        'task_delay_secs': 0,
        'events_cleanup_batch': 100,
    },
)
async def test_disabled(testpoint, pgsql, taxi_signal_device_tracks):
    @testpoint('events-cleaner-disabled-testpoint')
    def disabled_testpoint(arg):
        pass

    async with taxi_signal_device_tracks.spawn_task('signalq-events-cleaner'):
        await disabled_testpoint.wait_call()

    db = pgsql['signal_device_tracks'].cursor()
    db.execute(
        'SELECT event_id FROM signal_device_tracks.events ORDER BY event_id',
    )
    assert list(db) == [
        ('0a252859f6e1e3942eed9b5f16bd9bf5',),
        ('0ef0466e6e1331b3a7d35c5859830666',),
        ('0ef0466e6e1331b3a7d35c5859830777',),
        ('d58841a1f4b7816b84ccf4fcb7d886f7',),
        ('d68841a1f4b7816b84ccf4fcb7d886f7',),
    ]
