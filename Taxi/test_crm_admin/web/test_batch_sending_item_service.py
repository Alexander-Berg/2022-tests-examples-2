import pytest


DRIVER_WALL_GET_RESPONSE = {
    'id': '1d4d9b90b61d4d228894c3c590488e71',
    'service': 'driver_wall',
    'name': 'name',
    'status': 'created',
    'payload': {
        'type': 'newsletter',
        'title': 'message_title',
        'text': 'message_text',
        'url': 'message_url',
        'dom_storage': True,
        'important': True,
        'alert': False,
        'notification_mode': 'normal',
        'format': 'Raw',
        'url_open_mode': 'webview',
        'image_id': 'message_image_id',
        'teaser': 'message_link_title',
    },
    'settings': {'application': 'taximeter'},
    'recipients': {'type': 'yql', 'yql_link': '123'},
    'author': 'message_author',
    'created': '2100-01-01T15:00:00+0300',
    'updated': '2100-01-01T15:00:00+0300',
    'run_history': [],
    'ticket': 'TAXI-1',
}

CRM_ADMIN_DRIVER_WALL_SETTINGS = {
    'trend_to_service': [{'trend': 'trend_1', 'service': 'service_1'}],
}
CRM_ADMIN_DRIVER_WALL_SETTINGS_KIND = {
    'trend_to_service': [
        {'trend': 'trend_2', 'service': 'service_3'},
        {'trend': 'trend_2', 'kind': 'kind_2', 'service': 'service_2'},
    ],
}
CRM_ADMIN_DRIVER_WALL_SETTINGS_SUBKIND = {
    'trend_to_service': [
        {
            'trend': 'trend_2',
            'kind': 'kind_3',
            'subkind': 'subkind_3',
            'service': 'service_3',
        },
        {'trend': 'trend_2', 'kind': 'kind_3', 'service': 'service_4'},
    ],
}


@pytest.mark.config(CRM_ADMIN_DRIVER_WALL_SETTINGS_V2={})
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_chat_mapping_empty(web_app_client, mockserver):
    campaign_id = 1
    group_id = 1

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    response = await web_app_client.get(
        '/v1/batch-sending/item',
        params={'campaign_id': campaign_id, 'group_id': group_id},
    )

    assert response.status == 200
    response_data = await response.json()
    assert 'service' not in response_data['channel_info']


@pytest.mark.parametrize(
    'ids, service', [((1, 1), 'service_1'), ((2, 2), None)],
)
@pytest.mark.config(
    CRM_ADMIN_DRIVER_WALL_SETTINGS_V2=CRM_ADMIN_DRIVER_WALL_SETTINGS,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_chat_mapping_by_trend(web_app_client, mockserver, ids, service):
    campaign_id, group_id = ids

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    response = await web_app_client.get(
        '/v1/batch-sending/item',
        params={'campaign_id': campaign_id, 'group_id': group_id},
    )

    assert response.status == 200
    response_data = await response.json()
    assert response_data['channel_info'].get('service') == service


@pytest.mark.parametrize(
    'ids, service',
    [
        ((2, 2), 'service_2'),  # mapped by kind
        ((3, 3), 'service_3'),  # mapped by trend
        ((1, 1), None),  # not mapped
    ],
)
@pytest.mark.config(
    CRM_ADMIN_DRIVER_WALL_SETTINGS_V2=CRM_ADMIN_DRIVER_WALL_SETTINGS_KIND,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_chat_mapping_by_kind(web_app_client, mockserver, ids, service):
    campaign_id, group_id = ids

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    response = await web_app_client.get(
        '/v1/batch-sending/item',
        params={'campaign_id': campaign_id, 'group_id': group_id},
    )

    assert response.status == 200
    response_data = await response.json()
    assert response_data['channel_info'].get('service') == service


@pytest.mark.parametrize(
    'ids, service',
    [
        ((3, 3), 'service_3'),  # mapped by subkind
        ((4, 4), 'service_4'),  # mapped by kind
        ((1, 1), None),  # not mapped
        ((2, 2), None),  # not mapped
    ],
)
@pytest.mark.config(
    CRM_ADMIN_DRIVER_WALL_SETTINGS_V2=CRM_ADMIN_DRIVER_WALL_SETTINGS_SUBKIND,
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_chat_mapping_by_subkind(
        web_app_client, mockserver, ids, service,
):
    campaign_id, group_id = ids

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    response = await web_app_client.get(
        '/v1/batch-sending/item',
        params={'campaign_id': campaign_id, 'group_id': group_id},
    )

    assert response.status == 200
    response_data = await response.json()
    assert response_data['channel_info'].get('service') == service
