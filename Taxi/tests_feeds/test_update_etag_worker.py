import datetime

import psycopg2
import pytest


def _pg_dttm(dttm):
    pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
    pg_dttm = datetime.datetime.strptime(dttm, '%Y-%m-%dT%H:%M:%S')
    return pg_dttm.replace(tzinfo=pg_tz)


WORKER_ITERATION = 0


@pytest.mark.config(
    FEEDS_UPDATE_ETAG_WORKER={
        'enable': True,
        'work_interval_sec': 1,
        'max_update_channels': 100,
        'update_query_timeout': 30000,
    },
    FEEDS_SERVICES={
        'tariffeditor': {
            'description': 'description',
            'feed_count': 3,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'polling_delay_randomize_sec': 0,
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['feeds.sql'])
@pytest.mark.now('2018-12-20T00:00:00Z')
async def test_worker(taxi_feeds, taxi_config, pgsql, testpoint):
    @testpoint('update-etag-worker-tariffeditor-finished-ok')
    def worker_finished(data):
        if worker_finished.first_call:
            assert data['channels_affected'] == 2
        else:
            assert data['channels_affected'] == 0

    worker_finished.first_call = True
    async with taxi_feeds.spawn_task('distlock/update-etag-worker'):
        await worker_finished.wait_call()

    worker_finished.first_call = False
    async with taxi_feeds.spawn_task('distlock/update-etag-worker'):
        await worker_finished.wait_call()

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT name, updated FROM channels ORDER BY name')
    assert list(cursor) == [
        ('channel0:not_updated', _pg_dttm('2018-12-01T03:00:00')),
        ('channel1:tobe_updated', _pg_dttm('2018-12-20T03:00:00')),
        ('channel2:tobe_updated', _pg_dttm('2018-12-20T03:00:00')),
    ]

    cursor.execute(
        'SELECT DISTINCT etag FROM channels WHERE name LIKE \'%not_updated\'',
    )
    assert list(cursor) == [('358af307-61eb-454d-b8af-9c8f9666e5a8',)]

    cursor.execute(
        'SELECT DISTINCT etag FROM channels WHERE name LIKE \'%tobe_updated\'',
    )
    assert list(cursor) != [('358af307-61eb-454d-b8af-9c8f9666e5a8',)]
