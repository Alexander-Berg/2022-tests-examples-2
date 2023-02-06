# pylint: disable=unused-variable
import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = [
    'signal_device_api_worker.crontasks.video_partitions_cleanup',
    '-t',
    '0',
]


def _get_amount_of_video_chunks(pgsql) -> int:
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT COUNT(*)
        FROM signal_device_api.video_chunks;
        """,
    )
    return list(db)[0][0]


@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_S3_DELETE_OBJECTS_V2={
        'delete_objects_parallel_requests_amount': 2,
        'delete_objects_total_requests_amount': 4,
        'delete_objects_keys_amount': 1,
        'delete_objects_delay_seconds': 1,
    },
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_ok(pgsql):
    assert _get_amount_of_video_chunks(pgsql) == 5
    await run_cron.main(CRON_PARAMS)
    assert _get_amount_of_video_chunks(pgsql) == 1
    await run_cron.main(CRON_PARAMS)
    assert _get_amount_of_video_chunks(pgsql) == 0
