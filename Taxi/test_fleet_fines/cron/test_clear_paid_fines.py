import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.generated.cron import run_cron


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.fines_vc
        (uin, vc_normalized, payment_link, bill_date, sum, loaded_at,
         disappeared_at)
    VALUES
        ('1', 'vc1', 'payme1', '2020-01-01', 100.0, '2020-01-02',
         '2020-01-03'),
        ('3', 'vc2', 'payme1', '2020-01-01', 100.0, '2020-01-02',
         '2020-01-04')
    """,
        """
    INSERT INTO fleet_fines.fines_dl
        (uin, dl_pd_id_normalized, payment_link, bill_date, sum, loaded_at,
         disappeared_at)
    VALUES
        ('2', 'dl1', 'payme2', '2020-01-01', 100.0, '2020-01-02',
         '2020-01-03'),
        ('4', 'dl2', 'payme3', '2020-01-01', 100.0, '2020-01-02',
         '2020-01-04')
    """,
    ],
)
@pytest.mark.now('2020-01-04T12:00:00+0')
@pytest.mark.config(
    FLEET_FINES_CLEAR_PAID={'is_enabled': True, 'paid_days_ago': 1},
)
async def test_clear_paid_fines(cron_context: context_module.Context, patch):

    await run_cron.main(['fleet_fines.crontasks.clear_paid_fines', '-t', '0'])

    left_fines_vc_raw = await cron_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.fines_vc',
    )
    assert len(left_fines_vc_raw) == 1
    assert left_fines_vc_raw[0]['uin'] == '3'

    left_fines_dl_raw = await cron_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.fines_dl',
    )
    assert len(left_fines_dl_raw) == 1
    assert left_fines_dl_raw[0]['uin'] == '4'
