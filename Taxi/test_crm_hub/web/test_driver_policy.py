import pytest

from crm_hub.logic.bulk_sending import entity_settings


UUID = 'asdfasdf'
DBID = '12341234'
ENTITY_ID = DBID + '_' + UUID


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment8',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_driver_failed_communication_with_500(
        web_app_client, response_mock, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return mockserver.make_response(
            status=500, json={'code': 'internal error'},
        )

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000008',
            'event_id': '1qd123',
        },
    )
    assert response.status == 500
    assert patch_send.times_called
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(required_fields=required_fields, success='false')


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment8',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_driver_active_campaign_policy_forbidden(
        web_app_client, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': False})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000008',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert not patch_send.times_called
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(
        required_fields=required_fields,
        policy_resolution='forbidden',
        policy_reason='campaign_ttl',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment8',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.config(
    CRM_HUB_TRIGGER_SENDING_SETTINGS={'global_policy_allowed': False},
)
@pytest.mark.now('2019-12-20 10:00:00')
async def test_driver_active_campaign_ignore_policy_forbidden(
        web_app_client, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': False})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000008',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert patch_send.times_called == 1
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(required_fields=required_fields, policy_resolution='accepted')


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment9',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_active_campaign_delay_forbidden(
        web_app_client, response_mock, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000009',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert not patch_send.times_called
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(
        required_fields=required_fields,
        policy_resolution='forbidden',
        policy_reason='expired',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment8',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 21:00:00')
async def test_active_campaign_time_forbidden(
        web_app_client, response_mock, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 20:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000008',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert not patch_send.times_called
    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(
        required_fields=required_fields,
        policy_resolution='forbidden',
        policy_reason='timeofday',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment100',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_inactive_campaign(
        web_app_client, response_mock, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000100',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert not patch_send.times_called
    check_report(required_fields=[])


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment8',
    args=[{'name': 'entity_id', 'type': 'string', 'value': ENTITY_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_active_campaign_policy_allowed(
        web_app_client, response_mock, check_report, mockserver, load_json,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_send(request):
        return {'notification_id': 'notification_1'}

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-12-20 09:59:00',
            'entity_id': ENTITY_ID,
            'campaign_id': '00000000000000000000000000000008',
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


async def test_entity_id_for_policy(web_context):
    entity = {'user_id': '+7777777777'}
    entity_type = 'user'

    cls = entity_settings.ENTITY_SETTINGS[entity_type]
    settings: entity_settings.AbstractEntitySettings = cls(web_context)
    assert settings.format_policy_id(entity) == entity['user_id']
