# pylint: disable=global-statement
import pytest

from taxi import opentracing
from taxi.maintenance import run

from signal_device_api_worker.generated.cron import cron_context
from signal_device_api_worker.generated.cron import run_cron  # noqa F401


CRON_PARAMS = [
    'signal_device_api_worker.crontasks.video_concat_monitoring',
    '-t',
    '0',
]

TEST_CONTEXT = None
OK_LABELS = [
    {'sensor': 'videos.stat', 'type': 'not_concatenated'},
    {'sensor': 'videos.stat', 'type': 'concatenating'},
    {'sensor': 'videos.stat', 'type': 'not_concatenated_videos_size'},
    {'sensor': 'videos.stat', 'type': 'concat_ratio_20_mins'},
    {'sensor': 'videos.stat', 'type': 'oldest_not_concat_video_min_from_now'},
]


async def create_app(loop=None, db=None):
    context = cron_context.create_context()
    global TEST_CONTEXT
    TEST_CONTEXT = context
    opentracing.init_tracing(context.unit_name, context.config)
    await context.on_startup()
    try:
        yield context
    finally:
        await context.on_shutdown()


@pytest.mark.now('2019-09-16T12:00:00.0+0000')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_ok_monitoring(pgsql, get_stats_by_label_values):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        UPDATE signal_device_api.videos
        SET created_at = NOW() - interval '5 minutes'
        """,
    )
    db.execute(
        """
        UPDATE signal_device_api.video_chunks
        SET created_at = NOW() - interval '5 minutes'
        """,
    )
    db.execute(
        """
        UPDATE signal_device_api.video_chunks
        SET created_at = NOW() - interval '6 minutes'
        WHERE s3_path =
        'v1/e58e753c44e548ce9edaec0e0ef9c8c1/videos/partitions/test4/0_5.part'
        """,
    )
    db.execute(
        """
        UPDATE signal_device_api.video_chunks
        SET created_at = NOW() - interval '30 minutes'
        WHERE s3_path =
        'v1/e58e753c44e548ce9edaec0e0ef9c8c1/videos/partitions/test4/5_10.part'
        """,
    )
    db.execute(
        """
        UPDATE signal_device_api.video_chunks
        SET created_at = NOW()
        WHERE file_id = 'test_now'
        """,
    )
    db.execute(
        """
        WITH data AS (
            SELECT
            UNNEST(array[NOW() - interval '30 minutes',
                        NOW() - interval '10 minutes',
                        NOW() - interval '25 minutes',
                        NOW() - interval '100 minutes',
                        NOW()])
                        AS created_at,
            UNNEST(array['test4', 'test6', 'test7',
                        'missing_start', 'test_now'])
                        AS file_id
        )
        UPDATE signal_device_api.videos v
        SET created_at = data.created_at
        FROM data
        WHERE v.file_id = data.file_id
        """,
    )
    await run.run(
        create_app,
        'yandex-taxi-signal-device-api-worker-cron',
        CRON_PARAMS,
        loop=None,
        task_type=run_cron.Crontask,
        opentracing_enabled=False,
    )

    stats = get_stats_by_label_values(TEST_CONTEXT, {'sensor': 'videos.stat'})
    ok_values = [7, 1, 54.0, 0.20]
    assert len(stats) == 5
    assert [stat['labels'] for stat in stats] == OK_LABELS
    assert [stat['value'] for stat in stats[:-1]] == ok_values
    assert stats[4]['value'] >= 6.0
    assert stats[4]['value'] <= 10


@pytest.mark.now('2019-09-16T12:00:00.0+0000')
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_empty_db(pgsql, get_stats_by_label_values):
    await run.run(
        create_app,
        'yandex-taxi-signal-device-api-worker-cron',
        CRON_PARAMS,
        loop=None,
        task_type=run_cron.Crontask,
        opentracing_enabled=False,
    )

    stats = get_stats_by_label_values(TEST_CONTEXT, {'sensor': 'videos.stat'})
    ok_values = [0, 0, 0, 1.0, 0]
    assert len(stats) == 5
    assert [stat['labels'] for stat in stats] == OK_LABELS
    assert [stat['value'] for stat in stats] == ok_values
