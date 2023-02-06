# pylint: disable=protected-access,unused-variable
import datetime

from generated.clients import psp

from test_transactions.psp import responses
from transactions.clients.psp import rest_client


async def test_psp_create_intent(mockserver, web_context):
    @mockserver.json_handler('/psp/intents')
    async def trust_intents_handler():
        return responses.INTENT_CREATED

    client = rest_client.PSPClient(web_context)

    intent_cost = psp.psp_module.IntentCost(
        cost_type='fixed',
        currency=psp.psp_module.Currency(symbolic_code='RUB'),
    )

    intent_params = psp.psp_module.IntentParams(
        request_id='123',
        params=psp.psp_module._IntentParamsParams(
            cost=intent_cost,
            service_id='test',
            external_id='External ID',
            due_date=datetime.datetime.now() + datetime.timedelta(days=1),
            payments=[],
            uid='456',
        ),
    )

    intent_id = await client.create_intent(
        intent_params=intent_params, uid='456',
    )

    assert intent_id == responses.INTENT_CREATED.get('response').get(
        'intent_id',
    )


async def test_psp_get_intent_events(mockserver, web_context):
    @mockserver.json_handler('/psp/events')
    async def trust_intents_handler():
        return responses.INTENT_EVENTS

    client = rest_client.PSPClient(web_context)
    response = await client.get_psp_events_for_intent(
        intent_id='intent_1234test', uid='456',
    )

    assert isinstance(response[0], psp.psp_module.EventIntentStatusChanged)
    assert isinstance(response[1], psp.psp_module.EventPaymentStatusChanged)
    assert isinstance(response[2], psp.psp_module.EventRefundCreated)
    assert isinstance(response[3], psp.psp_module.EventRefundStatusChanged)
    assert isinstance(
        response[4], psp.psp_module.EventUserInteractionRequested,
    )
