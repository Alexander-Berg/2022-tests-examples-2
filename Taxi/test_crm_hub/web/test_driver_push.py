import uuid

import pytest


UUID = 'asdfasdf'
DBID = '12341234'
ENTITY_ID = DBID + '_' + UUID

PUSH_BODY = {
    'driver_push': {
        'collapse_key': 'MessageNew',
        'action': 'MessageNew',
        'code': 100,
        'dbid': DBID,
        'uuid': UUID,
        'ttl': 30,
        'data': {
            'id': '11112222-3333-4444-5555-666677778888',
            'message': 'driver push',
            'name': 'same as name',
            'format': 1,
            'flags': ['voice_over', 'fullscreen'],
        },
    },
}


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment12',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_push_code100(
        web_app_client,
        web_context,
        patch,
        check_report,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @patch('uuid.uuid4')
    def _gen_uuid():
        return uuid.UUID('11112222333344445555666677778888')

    @mockserver.json_handler('/client-notify/v2/push')
    async def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000012',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert patch_send.times_called
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(required_fields=required_fields, policy_resolution='accepted')


@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_push_client_notify(
        web_app_client,
        web_context,
        patch,
        check_report,
        mockserver,
        load_json,
        client_experiments3,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @patch('uuid.uuid4')
    def _gen_uuid():
        return uuid.UUID('11112222333344445555666677778888')

    @mockserver.json_handler('/client-notify/v2/push')
    async def patch_send(request):
        assert request.json == {
            'intent': 'MessageNew',
            'service': 'taximeter',
            'client_id': '{}-{}'.format(DBID, UUID),
            'collapse_key': 'MessageNew',
            'ttl': 30,
            'notification': {'title': 'same as name', 'text': 'driver push'},
            'data': {
                'id': '11112222-3333-4444-5555-666677778888',
                'format': 1,
                'flags': ['voice_over', 'fullscreen'],
            },
        }
        assert (
            request.headers['X-Idempotency-Token']
            == '11112222-3333-4444-5555-666677778888'
        )

        return {'notification_id': 'notification_1'}

    client_experiments3.add_record(
        consumer='crm_hub/communications',
        experiment_name='experiment12',
        args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
        value={'group_id': '1_testing'},
    )
    client_experiments3.add_record(
        consumer='crm_hub/communications',
        experiment_name='crm_hub_use_client_notify',
        args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
        value=True,
    )

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000012',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert patch_send.times_called
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(required_fields=required_fields, policy_resolution='accepted')
