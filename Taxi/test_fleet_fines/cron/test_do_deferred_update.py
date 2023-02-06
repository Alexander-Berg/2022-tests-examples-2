import datetime

import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.generated.cron import run_cron


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.fines_vc
        (uin, vc_normalized, payment_link, bill_date, sum, loaded_at)
    VALUES
        ('3', 'vc1', 'payme1', '2020-01-01', 100.0, '2020-01-02')
    """,
        """
    INSERT INTO fleet_fines.fines_dl
        (uin, dl_pd_id_normalized, payment_link, bill_date, sum, loaded_at)
    VALUES
        ('1', 'dl1', 'payme1', '2020-01-01', 100.0, '2020-01-02'),
        ('2', 'dl1', 'payme2', '2020-01-01', 100.0, '2020-01-02'),
        ('4', 'dl2', 'payme3', '2020-01-01', 100.0, '2020-01-02')
    """,
        """
    INSERT INTO fleet_fines.deferred_updates
        (uin, eta)
    VALUES
        ('1', '2020-01-01 12:00'),
        ('2', '2020-01-01 12:00'),
        ('3', '2020-01-01 12:00'),
        ('4', '2020-01-01 12:05')
        """,
    ],
)
@pytest.mark.now('2020-01-01T12:00:00+0')
async def test_do_deferred_update(cron_context: context_module.Context, patch):
    requested_dls = []  # type: ignore
    requested_vcs = []  # type: ignore

    @patch('fleet_fines.utils.yamoney.place_new_request')
    async def _place_new_request(context, dl_pd_ids=(), vcs=()):
        requested_dls.extend(dl_pd_ids)
        requested_vcs.extend(vcs)

    await run_cron.main(
        ['fleet_fines.crontasks.do_deferred_update', '-t', '0'],
    )

    assert requested_dls == ['dl1']
    assert requested_vcs == ['vc1']

    unused_defers_raw = await cron_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.deferred_updates',
    )
    unused_defers = [dict(d) for d in unused_defers_raw]
    assert unused_defers == [
        {'id': 4, 'uin': '4', 'eta': datetime.datetime(2020, 1, 1, 12, 5)},
    ]
