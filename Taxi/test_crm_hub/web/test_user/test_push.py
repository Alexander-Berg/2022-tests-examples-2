from aiohttp import web
import pytest

PUSH_ID = 'pushid'

PUSH_BODY = {
    'user_push': {
        'repack': {
            'wns': {'toast': {'text1': 'user push text'}},
            'apns': {
                'aps': {
                    'content-available': 1,
                    'mutable-content': 1,
                    'alert': {
                        'body': 'user push text',
                        'title': 'user push title',
                    },
                },
                'repack_payload': ['msg', 'show_in_foreground', 'category'],
            },
            'fcm': {
                'notification': {
                    'body': 'user push text',
                    'title': 'user push title',
                },
                'repack_payload': ['msg', 'show_in_foreground', 'category'],
            },
            'hms': {
                'notification_body': 'user push text',
                'notification_title': 'user push title',
                'repack_payload': ['msg', 'show_in_foreground', 'category'],
            },
            'mpns': {'toast': {'text1': 'user push text'}},
        },
        'payload': {
            'msg': 'user push text',
            'show_in_foreground': True,
            'category': 'QR',
        },
    },
    'silent_push': {
        'repack': {
            'wns': {},
            'apns': {'aps': {'content-available': 1, 'mutable-content': 1}},
            'fcm': {},
            'hms': {},
            'mpns': {},
        },
        'payload': {},
    },
}


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment4',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_active_campaign_policy_allowed(
        web_app_client, mockserver, check_report, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def handler(request):
        push = PUSH_BODY['user_push']
        assert request.json == {
            'user': 'usrid1',
            'intent': 'crm',
            'ttl': 50,
            'data': push,
            'locale': '',
            'meta': {
                'campaign_id': '00000000000000000000000000000003',
                'group_id': '1_testing',
            },
        }
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000003',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert handler.times_called == 1
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(required_fields=required_fields, policy_resolution='accepted')


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment7',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_silent_push(
        web_app_client, mockserver, check_report, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def handler(request):
        assert request.json['data'] == PUSH_BODY['silent_push']
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000006',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert handler.times_called == 1
    check_report(required_fields=[], exp3_group='1_testing')


@pytest.mark.parametrize(
    'campaign_id, order_id, deeplink',
    [
        ('00000000000000000000000000000007', '11', 't1.ru/a/?order=11'),
        ('00000000000000000000000000000008', '22', 't2.ru/b/?v=1&order=22'),
        ('00000000000000000000000000000009', '33', 't3.ru/c/?order=33'),
        ('00000000000000000000000000000010', '44', 't4.ru/d/e/?order=44'),
    ],
)
@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment4',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_deeplink(
        web_app_client, mockserver, load_json, campaign_id, order_id, deeplink,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def handler(request):
        assert request.json['data']['payload']['deeplink'] == deeplink
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': campaign_id,
            'event_id': '1qd123',
            'extra_data': {'order_id': order_id},
        },
    )
    assert response.status == 200
    assert handler.times_called == 1
