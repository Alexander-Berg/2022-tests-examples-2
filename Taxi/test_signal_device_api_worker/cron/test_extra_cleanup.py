# pylint: disable=unused-variable
import pytest

from signal_device_api_worker.generated.cron import run_cron

CRON_PARAMS = ['signal_device_api_worker.crontasks.extra_cleanup', '-t', '0']


def _get_amount_of_not_null_extra(pgsql) -> int:
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT COUNT(*)
        FROM signal_device_api.events
        WHERE extra IS NOT NULL;
        """,
    )
    return list(db)[0][0]


@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_EXTRA_CLEANUP_SETTINGS={'days': 1, 'limit': 2},
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_ok(pgsql):
    assert _get_amount_of_not_null_extra(pgsql) == 5
    await run_cron.main(CRON_PARAMS)
    assert _get_amount_of_not_null_extra(pgsql) == 3
    await run_cron.main(CRON_PARAMS)
    assert _get_amount_of_not_null_extra(pgsql) == 2
