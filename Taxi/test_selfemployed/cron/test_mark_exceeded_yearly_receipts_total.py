import pytest

from selfemployed.generated.cron import run_cron


@pytest.mark.pgsql('selfemployed_main', files=['base.sql'])
@pytest.mark.config(
    SELFEMPLOYED_REPORTED_INCOME_BLOCKING={
        'is_enabled': True,
        'blocking_total_threshold': 1,
    },
)
@pytest.mark.now('2022-08-01T12:00:00Z')
async def test_mark(se_cron_context, patch):
    @patch(
        'selfemployed.services.replica_access.'
        'Service.get_reported_income_by_inn',
    )
    async def _get_reported_income_by_inn(*args, **kwargs):
        return {'in1_pd': 2, 'in3_pd': 3}

    await run_cron.main(
        [
            'selfemployed.crontasks.mark_exceeded_yearly_receipts_total',
            '-t',
            '0',
        ],
    )

    bindings_rows = await se_cron_context.pg.main_master.fetch(
        """
        SELECT inn_pd_id, exceeded_reported_income_year
        FROM se.nalogru_phone_bindings
        ORDER BY inn_pd_id
        """,
    )
    bindings = list(dict(**row) for row in bindings_rows)
    assert bindings == [
        {'inn_pd_id': 'in1_pd', 'exceeded_reported_income_year': 2022},
        {'inn_pd_id': 'in2_pd', 'exceeded_reported_income_year': None},
        {'inn_pd_id': 'in3_pd', 'exceeded_reported_income_year': 2022},
    ]


@pytest.mark.pgsql('selfemployed_main', files=['base.sql'])
@pytest.mark.config(
    SELFEMPLOYED_REPORTED_INCOME_BLOCKING={
        'is_enabled': True,
        'blocking_total_threshold': 0,
    },
)
@pytest.mark.now('2022-08-01T12:00:00Z')
async def test_unmark_all(se_cron_context, patch):
    await run_cron.main(
        [
            'selfemployed.crontasks.mark_exceeded_yearly_receipts_total',
            '-t',
            '0',
        ],
    )

    bindings_rows = await se_cron_context.pg.main_master.fetch(
        """
        SELECT inn_pd_id, exceeded_reported_income_year
        FROM se.nalogru_phone_bindings
        ORDER BY inn_pd_id
        """,
    )
    bindings = list(dict(**row) for row in bindings_rows)
    assert bindings == [
        {'inn_pd_id': 'in1_pd', 'exceeded_reported_income_year': None},
        {'inn_pd_id': 'in2_pd', 'exceeded_reported_income_year': None},
        {'inn_pd_id': 'in3_pd', 'exceeded_reported_income_year': None},
    ]
