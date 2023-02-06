from aiohttp import web
import pytest


ENTITY_ID = 'asdasdada'


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment10',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_lavkauser_sms(web_app_client, mockserver, load_json):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    async def handler(request):
        assert request.json == {
            'user_id': ENTITY_ID,
            'text': 'user sms text',
            'intent': 'user sms intent',
            'sender': 'sender',
            'meta': {
                'campaign_id': '00000000000000000000000000000010',
                'group_id': '1_testing',
            },
        }
        return web.json_response({'code': 'code', 'message': 'message'})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000010',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert handler.times_called == 1
