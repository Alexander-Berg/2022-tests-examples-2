import datetime
import typing

import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.generated.cron import run_cron


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.ym_requests
        (req_id, dl_pd_ids, vcs,
         created_at, next_poll_at)
    VALUES
        ('1', ARRAY ['dl1'], ARRAY ['vc1'],
         '2020-01-01 12:00', '2020-01-01 12:01'),
        ('2', ARRAY ['dl2'], ARRAY ['vc2'],
         '2020-01-01 12:10', '2020-01-01 12:11');
    """,
    ],
)
@pytest.mark.now('2020-01-01T12:10:00Z')
async def test_poll_stuck_requests(
        cron_context: context_module.Context, patch,
):
    @patch('fleet_fines.utils.yamoney.poll_request')
    async def _poll(
            context,
            req_id: str,
            dl_pd_ids: typing.Optional[typing.List[str]],
            vcs: typing.Optional[typing.List[str]],
            create_time: datetime.datetime,
    ):
        assert req_id == '1'

    await run_cron.main(
        ['fleet_fines.crontasks.poll_stuck_requests', '-t', '0'],
    )
