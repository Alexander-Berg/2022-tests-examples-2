import pytest

from taxi.billing.util import dates as billing_dates

from billing_fin_payouts.generated.cron import run_cron
from billing_fin_payouts.utils import schedule_helper
from test_billing_fin_payouts import common_utils


@pytest.mark.pgsql(dbname='billing_fin_payouts', files=('fill_tables.psql',))
@pytest.mark.config(BILLING_FIN_PAYOUTS_SCHEDULE_PAYOUTS_ENABLED=True)
@pytest.mark.now('2022-02-07T00:00:00.000000+00:00')
async def test_schedule_netting_and_payouts(stq, patch):
    cron_name = 'billing_fin_payouts.crontasks.schedule_netting_and_payouts'
    await run_cron.main([cron_name, '-t', '0'])

    expected_calls = [
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting/12345',
            'kwargs': {'payout_ready_flag': False},
            'args': ['12345'],
            'eta': '2022-02-07T09:25:39.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting/12346',
            'kwargs': {'payout_ready_flag': False},
            'args': ['12346'],
            'eta': '2022-02-07T09:25:40.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting/12347',
            'kwargs': {'payout_ready_flag': False},
            'args': ['12347'],
            'eta': '2022-02-07T09:25:41.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting/12348',
            'kwargs': {'payout_ready_flag': False},
            'args': ['12348'],
            'eta': '2022-02-07T09:25:42.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting_with_payout/12345',
            'kwargs': {'payout_ready_flag': True},
            'args': ['12345'],
            'eta': '2022-02-07T19:25:39.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_bank_dry',
            'task_id': 'netting_with_payout/12345',
            'kwargs': {'payout_ready_flag': True},
            'args': ['12345'],
            'eta': '1970-01-01T00:00:00.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting_with_payout/12346',
            'kwargs': {'payout_ready_flag': True},
            'args': ['12346'],
            'eta': '2022-02-07T19:25:40.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_bank_dry',
            'task_id': 'netting_with_payout/12346',
            'kwargs': {'payout_ready_flag': True},
            'args': ['12346'],
            'eta': '1970-01-01T00:00:00.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting_with_payout/12347',
            'kwargs': {'payout_ready_flag': True},
            'args': ['12347'],
            'eta': '2022-02-07T19:25:41.000000+00:00',
        },
        {
            'queue_name': 'billing_fin_payouts_process_payouts_oebs_prod',
            'task_id': 'netting_with_payout/12348',
            'kwargs': {'payout_ready_flag': True},
            'args': ['12348'],
            'eta': '2022-02-07T19:25:42.000000+00:00',
        },
    ]

    queues = [
        stq.billing_fin_payouts_process_payouts,
        stq.billing_fin_payouts_process_payouts_bank_prod,
        stq.billing_fin_payouts_process_payouts_oebs_prod,
        stq.billing_fin_payouts_process_payouts_bank_dry,
        stq.billing_fin_payouts_process_payouts_oebs_dry,
    ]
    common_utils.check_stqs_calls(queues, expected_calls)


@pytest.mark.parametrize(
    'schedule, now, expected_schedule_at',
    [
        ([], '2022-02-07T00:00:00.000000+00:00', None),
        (
            ['09:00', '10:00', '11:00', '12:00', '13:00'],
            '2022-02-07T11:40:00.000000+03:00',
            '2022-02-07T12:00:00.000000+03:00',
        ),
        (
            ['08:00', '10:00', '11:00', '12:00', '13:00'],
            '2022-02-07T07:30:00.000000+03:00',
            '2022-02-07T08:00:00.000000+03:00',
        ),
        (
            ['09:00', '10:00', '11:00', '12:00', '13:00'],
            '2022-02-07T12:00:00.000000+03:00',
            '2022-02-07T13:00:00.000000+03:00',
        ),
        (
            ['09:00', '10:00', '11:00', '12:00', '13:00'],
            '2022-02-07T13:40:00.000000+03:00',
            '2022-02-08T09:00:00.000000+03:00',
        ),
        (
            ['09:08', '10:18', '11:08', '12:18', '13:08'],
            '2022-02-07T11:09:00.000000+03:00',
            '2022-02-07T12:18:00.000000+03:00',
        ),
        (
            ['00:00', '01:00'],
            '2022-02-08T00:00:00.000000+03:00',
            '2022-02-08T01:00:00.000000+03:00',
        ),
        (
            ['00:00'],
            '2022-02-08T00:00:00.000000+03:00',
            '2022-02-09T00:00:00.000000+03:00',
        ),
    ],
    ids=[
        'empty_schedule',
        'schedule_at_12',
        'now_7_schedule_at_8',
        'now_12_schedule_at_13',
        'schedule_next_day',
        'non_round_schedule',
        'now_midnight_schedule_at_1',
        'now_midnight_schedule_next_midnight',
    ],
)
def test_get_next_schedule_point(schedule, now, expected_schedule_at):

    schedule_at = schedule_helper.get_next_schedule_point(
        schedule=schedule, now=billing_dates.parse_datetime(now),
    )
    assert schedule_at == billing_dates.parse_datetime_or_none(
        expected_schedule_at,
    )
