import pytest


BATCH_CHANNEL_SETTINGS = {
    'driver_push': {
        'channel_name': 'driver_push',
        'code': 10,
        'collapse_key': 'collapse_key',
        'ttl': 200,
    },
    'driver_sms': {
        'channel_name': 'driver_sms',
        'intent': 'driver_sms_intent',
        'sender': 'driver_sms_sender',
    },
    'driver_wall': {'channel_name': 'driver_wall'},
    'user_promo': {'channel_name': 'user_promo'},
    'user_push': {
        'channel_name': 'user_push',
        'intent': 'user_push_intent',
        'ttl': 300,
    },
    'user_sms': {
        'channel_name': 'user_sms',
        'intent': 'user_sms_intent',
        'sender': 'user_sms_sender',
    },
    'zuser_push': {
        'channel_name': 'zuser_push',
        'intent': 'zuser_push_intent',
        'ttl': 300,
    },
    'eatsuser_push': {
        'channel_name': 'eatsuser_push',
        'intent': 'eatsuser_push_intent',
        'ttl': 150,
    },
    'eatsuser_sms': {
        'channel_name': 'eatsuser_sms',
        'intent': 'eatsuser_sms_intent',
        'sender': 'eatsuser_sms_sender',
    },
}

BATCH_CHANNEL_SETTINGS_NO_ANY_INTENT = {
    'user_push': {'channel_name': 'user_push', 'ttl': 300},
}

BATCH_CHANNEL_SETTINGS_OLD_INTENT = {
    'user_push': {
        'channel_name': 'user_push',
        'intent': 'old_intent',
        'ttl': 300,
    },
}

BATCH_CHANNEL_SETTINGS_NEW_INTENT = {
    'user_promo': {
        'channel_name': 'user_promo',
        # abnormal situation. UserPromoInfo has no attribute 'intent'
        'intents': {'intent': 'default_intent'},
    },
    'user_push': {
        'channel_name': 'user_push',
        'intent': 'old_intent',
        'ttl': 300,
        'intents': {
            'intent': 'default_intent',
            'by_trend': [
                {
                    'trend': 'trend_1',
                    'intent': 'by_trend_1',
                    'by_kind': [
                        {
                            'kind': 'kind_1_1',
                            'intent': 'by_kind_1_1',
                            'by_subkind': [
                                {
                                    'subkind': 'subkind_1_1_1',
                                    'intent': 'by_subkind_1_1_1',
                                },
                                {
                                    'subkind': 'subkind_1_1_2',
                                    'intent': 'by_subkind_1_1_2',
                                },
                            ],
                        },
                    ],
                },
                {'trend': 'trend_2', 'intent': 'by_trend_2'},
            ],
        },
    },
}

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


@pytest.mark.config(CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS)
@pytest.mark.parametrize(
    'campaign_id, group_id, result',
    [
        (1, 1, 200),
        (1, 2, 200),
        (1, 3, 200),
        (1, 4, 200),
        (1, 5, 200),
        (2, 6, 200),
        (2, 7, 200),
        (2, 8, 200),
        (6, 9, 200),
        (7, 10, 200),
        (7, 11, 200),
        (1, 100, 404),
        (100, 1, 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_retrieve_batch_campaign(
        patch,
        web_app_client,
        campaign_id,
        group_id,
        result,
        load_json,
        mockserver,
):
    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == result
    if response.status == 200:
        expected_values = load_json('batch_sending.json')
        response_data = await response.json()

        expected = expected_values[f'{campaign_id}_{group_id}']

        assert response_data == expected


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_NO_ANY_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_without_intent(patch, web_app_client, load_json, mockserver):
    campaign_id = 1
    group_id = 1

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert 'intent' not in response_data['channel_info']


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_OLD_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_simple_intent(patch, web_app_client, load_json, mockserver):
    campaign_id = 1
    group_id = 1

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['channel_info']['intent'] == 'old_intent'


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_NEW_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_default_intent_from_tree(
        patch, web_app_client, load_json, mockserver,
):
    campaign_id = 1
    group_id = 1

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()

    assert response_data['channel_info']['intent'] == 'default_intent'


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_NEW_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_intent_by_trend(patch, web_app_client, load_json, mockserver):
    campaign_id = 3
    group_id = 1

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()

    assert response_data['channel_info']['intent'] == 'by_trend_1'


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_NEW_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_intent_by_trend_kind(
        patch, web_app_client, load_json, mockserver,
):
    campaign_id = 4
    group_id = 1

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()

    assert response_data['channel_info']['intent'] == 'by_kind_1_1'


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_NEW_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_default_from_trend_kind_subkind(
        patch, web_app_client, load_json, mockserver,
):
    campaign_id = 5
    group_id = 1

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()

    assert response_data['channel_info']['intent'] == 'by_subkind_1_1_1'


@pytest.mark.config(
    CRM_ADMIN_BATCH_CHANNEL_SETTINGS=BATCH_CHANNEL_SETTINGS_NEW_INTENT,
)
@pytest.mark.pgsql('crm_admin', files=['init_batch_sending.sql'])
@pytest.mark.now('2020-02-20 10:00:00')
async def test_intent_tree_on_promo(
        patch, web_app_client, load_json, mockserver,
):
    campaign_id = 1
    group_id = 2

    plugin_path = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient'

    @patch(plugin_path + '.read_table')
    async def _read_table(*args, **kwargs):
        campaing_key = f'campaign_{campaign_id}'
        stat = load_json('stat.json')
        return stat[campaing_key]

    @mockserver.json_handler('feeds-admin/v1/driver-wall/get')
    async def _(request):
        return DRIVER_WALL_GET_RESPONSE

    params = {'campaign_id': campaign_id, 'group_id': group_id}
    response = await web_app_client.get(
        '/v1/batch-sending/item', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert 'intent' not in response_data['channel_info']
