from aiohttp import web
import pytest


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment1',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 23:59:59')
async def test_active_campaign_user_in_testing(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 23:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': 'eventid',
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
    check_report(
        required_fields=required_fields,
        exp3_group='1_testing',
        exp3_reason='matched',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment1',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '0_control'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 23:59:59')
async def test_active_campaign_user_in_control(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 23:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': 'eventid',
        },
    )
    assert response.status == 200
    assert not handler.times_called

    required_fields = [
        'event_id',
        'entity_id',
        'campaign_config',
        'new_communication_data',
    ]
    check_report(
        required_fields=required_fields,
        exp3_group='0_control',
        exp3_reason='matched',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment1',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_active_campaign_exp3_not_matched(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1111',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': '1qd123',
        },
    )

    assert response.status == 200
    assert not handler.times_called
    required_fields = ['event_id', 'entity_id', 'new_communication_data']
    check_report(
        required_fields=required_fields,
        exp3_group=None,
        exp3_reason='not_matched',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment1',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_active_campaign_empty_exp3_consumer(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': '1qd123',
        },
    )
    assert response.status == 500
    assert not handler.times_called
    check_report(required_fields=[], success='false')


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment1',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='asfasdfasfasdf')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_active_campaign_wrong_exp3_consumer(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': '1qd123',
        },
    )
    assert response.status == 500
    assert not handler.times_called

    check_report(required_fields=[], success='false')


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='wrong_experiment_name',
    args=[{'name': 'entity_id', 'type': 'string', 'value': 'usrid1'}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_active_campaign_wrong_exp3_name(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert not handler.times_called

    check_report(
        required_fields=[], exp3_group=None, exp3_reason='not_matched',
    )


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment1',
    args=[],
    value={},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_active_campaign_wrong_exp3_return(
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
        return web.json_response({})

    response = await web_app_client.post(
        '/v1/communication/new',
        json={
            'event_timestamp': '2019-11-20 09:59:00',
            'entity_id': 'usrid1',
            'campaign_id': '00000000000000000000000000000001',
            'event_id': '1qd123',
        },
    )
    assert response.status == 200
    assert not handler.times_called

    check_report(
        required_fields=[], exp3_reason='not_matched', exp3_group=None,
    )
