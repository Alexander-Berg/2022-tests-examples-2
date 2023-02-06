from aiohttp import web
import pytest

from billing_functions.stq.billing_netting import task as billing_netting


@pytest.mark.config(BILLING_FUNCTIONS_NETTING_SCHEDULER_ENABLED=True)
async def test_billing_netting(
        stq3_context, mock_processor_billing, mock_payout_billing,
):
    @mock_processor_billing('/v1/process')
    async def processor_handler(request):
        assert request.json == {
            'namespace': 'taxi',
            'endpoint': 'payout',
            'event': {
                'client_id': 4054,
                'event_time': '2021-03-19T14:00:00+00:00',
                'transaction_id': 'payout/taxi/4054/2021-03-19T14:00:00+00:00',
                'payload': {},
            },
        }
        return web.json_response({})

    @mock_payout_billing('/api/v1/payout-by-client')
    async def payout_handler(request):
        assert request.json == {
            'client_id': 4054,
            'external_id': '2021-03-19T14:00:00+00:00',
        }
        return web.json_response({})

    await billing_netting.task(
        stq3_context,
        task_id='task',
        billing_client_id='4054',
        netting_date='2021-03-19T14:00:00+00:00',
        transaction_id=4636373,
    )

    assert processor_handler.times_called == 1
    assert payout_handler.times_called == 1


@pytest.mark.config(BILLING_FUNCTIONS_NETTING_SCHEDULER_ENABLED=True)
async def test_netting_in_the_past(
        stq3_context, mock_processor_billing, mock_payout_billing, mockserver,
):
    @mock_processor_billing('/v1/process')
    async def processor_handler(request):
        response = {
            'status': 400,
            'json': {
                'status': 'error',
                'code': 400,
                'data': {
                    'message': 'NETTING_IN_THE_PAST',
                    'params': {
                        'cutoff_dt': '2021-09-22T12:00:00+00:00',
                        'desired_netting_dt': '2021-09-22T15:00:00+03:00',
                    },
                },
            },
        }
        return mockserver.make_response(**response)

    await billing_netting.task(
        stq3_context,
        task_id='task',
        billing_client_id='4054',
        netting_date='2021-03-19T14:00:00+00:00',
        transaction_id=4636373,
    )

    @mock_payout_billing('/api/v1/payout-by-client')
    async def payout_handler(request):
        assert request.json == {
            'client_id': 4054,
            'external_id': '2021-03-19T14:00:00+00:00',
        }
        return web.json_response({})

    assert processor_handler.times_called == 1
    # just finish netting task
    assert payout_handler.times_called == 0
