import datetime

import pytest

from workforce_management.generated.cron import run_cron
from workforce_management.storage.postgresql import db

DEFAULT = '__default__'


@pytest.mark.now('2010-11-03 14:30:00.0 +0000')
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PERIOD_CLOSE_SETTINGS={
        DEFAULT: [
            {
                'enabled': True,
                'dry_run': False,
                'run_on': {'day': 3, 'hour': 14},
                'backdate': 3,
            },
        ],
        'taxi': [
            {
                'enabled': True,
                'dry_run': True,
                'run_on': {'day': 3, 'hour': 14},
                'backdate': 3,
            },
        ],
        'eats': [],
        'lavka2': [
            {
                'enabled': True,
                'dry_run': False,
                'run_on': {'day': 5, 'hour': 14},
                'backdate': 3,
            },
        ],
    },
)
@pytest.mark.pgsql('workforce_management', files=['allowed_periods.sql'])
@pytest.mark.parametrize(
    'tst_domain, expected_result',
    [
        (
            'lavka',
            datetime.datetime(
                2010, 10, 31, hour=14, tzinfo=datetime.timezone.utc,
            ),
        ),
        (
            'taxi',
            datetime.datetime(
                2010, 10, 22, hour=12, tzinfo=datetime.timezone.utc,
            ),
        ),
        (
            'eats',
            datetime.datetime(
                2010, 10, 22, hour=12, tzinfo=datetime.timezone.utc,
            ),
        ),
        (
            'lavka2',
            datetime.datetime(
                2010, 10, 22, hour=12, tzinfo=datetime.timezone.utc,
            ),
        ),
    ],
)
async def test_base(cron_context, tst_domain, expected_result):
    await run_cron.main(
        ['workforce_management.crontasks.hourly_period_close_check'],
    )

    operators_db = db.OperatorsRepo(context=cron_context)
    async with operators_db.master.acquire() as conn:
        records = await operators_db.get_allowed_period(conn, tst_domain)
        assert records
        allowed_period = records[0]

    assert allowed_period['datetime_from'] == expected_result
