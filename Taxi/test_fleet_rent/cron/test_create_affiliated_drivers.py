import pytest

from fleet_rent.generated.cron import run_cron


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_run_cad(patch):
    processed_ids = set()

    @patch('fleet_rent.utils.create_affiliated_driver.run')
    async def _run(context, affiliation):
        processed_ids.add(affiliation.record_id)

    await run_cron.main(
        ['fleet_rent.crontasks.create_affiliated_drivers', '-t', '0'],
    )

    assert processed_ids == {'a1'}
