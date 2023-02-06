import datetime

import pytest

from selfemployed.entities import nalogru_binding
from selfemployed.entities import personal
from selfemployed.generated.cron import run_cron


@pytest.mark.pgsql('selfemployed_main', files=['bonds.sql'])
@pytest.mark.config(
    SELFEMPLOYED_FNS_BINDING_SETTINGS={
        'polling_is_enabled': True,
        'request_ttl': '1d',
        'batch_size': 2,
    },
)
@pytest.mark.now('2021-08-01T12:00:00Z')
async def test_poll_requested_fns_bindings(se_cron_context, patch):
    bind_results = {
        'b2': (nalogru_binding.BindingStatus.COMPLETED, 'i2'),
        'b3': (nalogru_binding.BindingStatus.FAILED, None),
        'b4': (nalogru_binding.BindingStatus.IN_PROGRESS, None),
        'b5': (nalogru_binding.BindingStatus.IN_PROGRESS, None),
    }
    phone_from_pd = {'pp2': 'p2', 'pp3': 'p3', 'pp4': 'p4', 'pp5': 'p5'}
    inn_to_pd = {'i2': 'ip2'}

    @patch('selfemployed.services.nalogru.Service.check_binding_status')
    async def _check(request_id):
        return bind_results[request_id]

    @patch('selfemployed.services.personal.PhonesService.from_pd')
    async def _get_phone(pd_id):
        return personal.Phone(normalized=phone_from_pd[pd_id], pd_id=pd_id)

    @patch('selfemployed.services.personal.InnService.from_raw')
    async def _get_inn_pd(raw):
        return personal.INN(normalized=raw, pd_id=inn_to_pd[raw])

    await run_cron.main(
        [
            'selfemployed.crontasks.poll_nalogru_bindings_in_progress',
            '-t',
            '0',
        ],
    )

    binding_rows = await se_cron_context.pg.main_master.fetch(
        """
        SELECT phone_pd_id, inn_pd_id, status,
            bind_request_id, bind_requested_at
        FROM se.nalogru_phone_bindings
        ORDER BY phone_pd_id
        """,
    )
    bindings = [dict(row) for row in binding_rows]
    assert bindings == [
        dict(
            phone_pd_id='pp1',
            inn_pd_id='ip1',
            status='COMPLETED',
            bind_request_id=None,
            bind_requested_at=None,
        ),
        dict(
            phone_pd_id='pp2',
            inn_pd_id='ip2',
            status='COMPLETED',
            bind_request_id=None,
            bind_requested_at=None,
        ),
        dict(
            phone_pd_id='pp3',
            inn_pd_id=None,
            status='FAILED',
            bind_request_id=None,
            bind_requested_at=None,
        ),
        dict(
            phone_pd_id='pp4',
            inn_pd_id=None,
            status='IN_PROGRESS',
            bind_request_id='b4',
            bind_requested_at=datetime.datetime(
                2021, 8, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
        ),
        dict(
            phone_pd_id='pp5',
            inn_pd_id=None,
            status='TIMED_OUT',
            bind_request_id=None,
            bind_requested_at=None,
        ),
    ]
