import pytest

from quality_control.generated.cron import run_cron


@pytest.mark.config(
    QC_VACCINATION_JOB_SETTINGS={'enabled': False, 'limit': 100},
)
async def test_disabled():
    # crontask
    await run_cron.main(
        [
            'quality_control.crontasks.validate_vaccination_certificate',
            '-t',
            '0',
        ],
    )
