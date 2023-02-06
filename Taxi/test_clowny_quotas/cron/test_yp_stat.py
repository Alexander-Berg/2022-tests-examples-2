# pylint: disable=redefined-outer-name
import pytest

from clowny_quotas.generated.cron import run_cron


@pytest.mark.usefixtures('taxi_clowny_quotas_mocks')
async def test_yp_stat(yp_mockserver):
    yp_mockserver()

    await run_cron.main(['clowny_quotas.crontasks.yp_stat', '-t', '0'])
