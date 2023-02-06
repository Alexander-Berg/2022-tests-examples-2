import datetime

import pytest

from fleet_rent.generated.cron import run_cron


@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.config(
    FLEET_RENT_EXTERNAL_PARK_TRANSACTIONS_PROCESSING={
        'create': {'is_enabled': True},
    },
)
async def test_run_cspt(patch):
    @patch(
        'fleet_rent.pg_access.external_park_transactions_log.'
        'EPTLAccessor.fill',
    )
    async def _fill(up_to: datetime.datetime):
        assert up_to == datetime.datetime.now(datetime.timezone.utc)

    await run_cron.main(
        ['fleet_rent.crontasks.create_external_park_transactions', '-t', '0'],
    )
