# pylint: disable=protected-access
import datetime

import pytest

from vgw_api_tasks.monrun.checks import vgw_disabling

NOW = datetime.datetime(2019, 3, 13, 12, 0, 0)


@pytest.mark.pgsql('vgw_api', files=('gateways.sql',))
@pytest.mark.now(NOW.isoformat())
async def test_check(cron_context):
    class ARGS:
        time_range = 600

    result = await vgw_disabling._check(cron_context, ARGS)
    msg = (
        '1; WARN: 1 providers disabled in the last 10 minutes. '
        'Provider: gateway_id_3, disable reason: test_reason. '
        '1 providers disabled in interval 20-30 minutes. '
        'Provider: gateway_id_2, disable reason: long_reason.'
    )
    assert result == msg
