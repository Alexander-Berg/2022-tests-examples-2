import aiohttp.web
import pytest

from fleet_support_chat.utils import solomon as solomon_util


@pytest.mark.now('2020-12-08T16:26:00+03:00')
@pytest.mark.translations(
    opteum_support_chat_form={
        'base.driver.topic.title': {'ru': 'base_driver_topic_title'},
        'base.driver.subtopic.no_orders.title': {
            'ru': 'base_driver_subtopic_no_orders_title',
        },
        'base.driver.inputs.license.title': {
            'ru': 'base_driver_inputs_license_title',
        },
    },
)
async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_support_chat,
        mock_sticker,
        mock_ya_cc,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_request']
        return aiohttp.web.json_response(stub['dac_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    @patch('fleet_support_chat.api.support_chat_new._run_stq_task')
    async def _run_stq_task(*args, **kwargs):
        pass

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    @mock_sticker('/send/')
    async def _send(request):
        assert request.json == stub['sticker_request']
        return aiohttp.web.json_response({})

    @mock_dispatcher_access_control('/v1/parks/groups/list')
    async def _list(request):
        assert request.json == stub['dac_group_request']
        return aiohttp.web.json_response(stub['dac_group_response'])

    @mock_ya_cc('/--')
    async def _short_url(request):
        return aiohttp.web.Response(
            headers={'Content-Type': 'text/javascript; charset=utf-8'},
            text='short_link',
        )

    @patch('fleet_support_chat.services.support_chat_mailing._get_email_xml')
    async def _get_email_xml(*args, **kwargs):
        return 'email_template'

    response = await web_app_client.post(
        '/support-chat-api/v1/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'text': 'test',
            'inputs': [
                {
                    'title': 'base_driver_inputs_license_title',
                    'value': 'AB12345678',
                    'name': 'driver_license',
                },
            ],
            'permission': 'me',
            'subtopic': 'base_driver_subtopic_no_orders_title',
            'topic': 'base_driver_topic_title',
            'attachments': None,
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.now('2020-12-08T16:26:00+03:00')
@pytest.mark.translations(
    opteum_support_chat_form={
        'base.driver.topic.title': {'ru': 'base_driver_topic_title'},
        'base.driver.subtopic.no_orders.title': {
            'ru': 'base_driver_subtopic_no_orders_title',
        },
        'base.driver.inputs.license.title': {
            'ru': 'base_driver_inputs_license_title',
        },
    },
)
async def test_success_failed_send_email(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_support_chat,
        mock_sticker,
        mock_ya_cc,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_request']
        return aiohttp.web.json_response(stub['dac_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    @patch('fleet_support_chat.api.support_chat_new._run_stq_task')
    async def _run_stq_task(*args, **kwargs):
        pass

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    @mock_sticker('/send/')
    async def _send(request):
        return aiohttp.web.json_response({}, status=503)

    @mock_dispatcher_access_control('/v1/parks/groups/list')
    async def _list(request):
        assert request.json == stub['dac_group_request']
        return aiohttp.web.json_response(stub['dac_group_response'])

    @mock_ya_cc('/--')
    async def _short_url(request):
        return aiohttp.web.Response(
            headers={'Content-Type': 'text/javascript; charset=utf-8'},
            text='short_link',
        )

    @patch('fleet_support_chat.services.support_chat_mailing._get_email_xml')
    async def _get_email_xml(*args, **kwargs):
        return 'email_template'

    response = await web_app_client.post(
        '/support-chat-api/v1/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'text': 'test',
            'inputs': [
                {
                    'title': 'base_driver_inputs_license_title',
                    'value': 'AB12345678',
                    'name': 'driver_license',
                },
            ],
            'permission': 'me',
            'subtopic': 'base_driver_subtopic_no_orders_title',
            'topic': 'base_driver_topic_title',
            'attachments': None,
        },
    )

    assert response.status == 200
    data = await response.json()

    sensor = solomon_util.Solomon.SENSOR_NOTIFY_EMAIL_ERRORS
    event_type = solomon_util.Solomon.EVENT_TYPE_ON_CREATE
    stats = get_stats_by_label_values(web_app['context'], {'sensor': sensor})
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'event_type': event_type, 'sensor': sensor},
            'value': 1,
            'timestamp': None,
        },
    ]

    assert data == stub['service_response']


@pytest.mark.now('2020-12-08T16:26:00+03:00')
@pytest.mark.translations(
    opteum_support_chat_form={
        'base.driver.topic.title': {'ru': 'base_driver_topic_title'},
        'base.driver.subtopic.no_orders.title': {
            'ru': 'base_driver_subtopic_no_orders_title',
        },
        'base.driver.inputs.license.title': {
            'ru': 'base_driver_inputs_license_title',
        },
    },
)
async def test_success_failed_send_email_retry(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_support_chat,
        mock_sticker,
        mock_ya_cc,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_request']
        return aiohttp.web.json_response(stub['dac_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    @patch('fleet_support_chat.api.support_chat_new._run_stq_task')
    async def _run_stq_task(*args, **kwargs):
        pass

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    @mock_sticker('/send/')
    async def _send(request):
        return aiohttp.web.json_response({}, status=503)

    response = await web_app_client.post(
        '/support-chat-api/v1/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'text': 'test',
            'inputs': [
                {
                    'title': 'base_driver_inputs_license_title',
                    'value': 'AB12345678',
                    'name': 'driver_license',
                },
            ],
            'permission': 'me',
            'subtopic': 'base_driver_subtopic_no_orders_title',
            'topic': 'base_driver_topic_title',
            'attachments': None,
        },
    )

    assert response.status == 200
    data = await response.json()

    sensor = solomon_util.Solomon.SENSOR_NOTIFY_EMAIL_ERRORS
    event_type = solomon_util.Solomon.EVENT_TYPE_ON_CREATE
    stats = get_stats_by_label_values(web_app['context'], {'sensor': sensor})
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'event_type': event_type, 'sensor': sensor},
            'value': 1,
            'timestamp': None,
        },
    ]

    assert data == stub['service_response']
