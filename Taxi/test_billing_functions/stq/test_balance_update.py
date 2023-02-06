from aiohttp import web
import pytest

from taxi.stq import async_worker_ng

from billing_functions.stq import balance_update


@pytest.mark.parametrize(
    'data_path',
    [
        'balance_update.json',
        'balance_update_old_balance.json',
        'balance_update_dryrun.json',
    ],
)
@pytest.mark.now('2021-05-21T12:34:00.000000+03:00')
@pytest.mark.config(BILLING_STQ_CONTRACTOR_BALANCE_UPDATE_MODE='enable')
async def test_contractor_balance_update(
        data_path,
        load_json,
        stq3_context,
        patched_stq_queue,
        mockserver,
        monkeypatch,
):
    billing_reports_requests = []
    is_rescheduled = False

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _v1_balances_select(request):
        billing_reports_requests.append(request.json)
        return web.json_response(data['billing_reports_response'])

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _patch_stq_agent_reschedule(request):
        assert (
            request.json['queue_name']
            == 'billing_functions_internal_balance_update'
        )
        nonlocal is_rescheduled
        is_rescheduled = True
        return {}

    data = load_json(data_path)
    # Prepare config and params for stq task
    monkeypatch.setattr(
        stq3_context.config,
        'BILLING_STQ_CONTRACTOR_BALANCE_UPDATE_MODE',
        data['BILLING_STQ_CONTRACTOR_BALANCE_UPDATE_MODE'],
    )

    task_meta_info = async_worker_ng.TaskInfo(
        id=751,
        exec_tries=0,
        reschedule_counter=0,
        queue='billing_functions_internal_balance_update',
    )
    stq_params = data['stq_params']
    await balance_update.task(
        stq3_context, **stq_params, task_meta_info=task_meta_info,
    )

    # Check requests in billing-reports
    assert billing_reports_requests == data['billing_reports_requests']
    # Check result stq call
    assert is_rescheduled == data['stq_rescheduled']
    if not is_rescheduled and patched_stq_queue.has_calls:
        stq_call_args = patched_stq_queue.next_call()
        stq_call_args = stq_call_args['request'].json
        stq_call_args.pop('task_id')
        assert stq_call_args == data['expected_stq_call']
