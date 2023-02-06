import aiohttp.web
import pytest

from fleet_support_chat.utils import solomon as solomon_util


@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic(
        web_app_client,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_support_chat,
        mock_sticker,
        mock_ya_cc,
        mock_personal_single_license,
        load_json,
        patch,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    driver_license = 'AB12345678'
    expected_driver_license_pd_id = 'driver_license_pd_id'
    mock_personal_single_license(driver_license, expected_driver_license_pd_id)

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
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [
                {'name': 'driver_license', 'value': driver_license},
                {'name': 'message', 'value': 'message\ntest'},
            ],
            'permission': 'me',
            'topic_id': 'base.topic.driver.simple.no_orders',
            'attachments': ['attachment_id'],
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']

    assert stq.support_chat_create_chatterbox_task.has_calls


@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic_with_array_input(
        web_app_client,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_support_chat,
        mock_sticker,
        mock_ya_cc,
        mock_personal_single_license,
        load_json,
        patch,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request_with_array_input']
        return aiohttp.web.json_response(stub['support_chat_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    driver_license = 'AB12345678'
    expected_driver_license_pd_id = 'driver_license_pd_id'
    mock_personal_single_license(driver_license, expected_driver_license_pd_id)

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
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [
                {'name': 'driver_license', 'value': driver_license},
                {'name': 'period', 'value': ['2021-08-23', '2021-08-27']},
                {'name': 'message', 'value': 'message\ntest'},
            ],
            'permission': 'me',
            'topic_id': 'topics.nested.orders_and_bonuses.nested.about_bonus.simple.driver_bonus',  # noqa: E501
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']

    assert stq.support_chat_create_chatterbox_task.has_calls


@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_callback(
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
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request_callback']
        return aiohttp.web.json_response(stub['support_chat_response'])

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
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [{'name': 'user_phone', 'value': '+71112223344'}],
            'permission': 'me',
            'topic_id': 'base.callback.topic.title',
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']

    assert stq.support_chat_create_chatterbox_task.has_calls


@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic_failed_send_email(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_personal_single_license,
        mock_support_chat,
        mock_sticker,
        load_json,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    @mock_support_chat('/v1/chat/new')
    async def _new(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(stub['support_chat_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    driver_license = 'AB12345678'
    expected_driver_license_pd_id = 'driver_license_pd_id'
    mock_personal_single_license(driver_license, expected_driver_license_pd_id)

    @mock_sticker('/send/')
    async def _send(request):
        assert request.json == stub['sticker_request']
        return aiohttp.web.json_response({}, status=503)

    response = await web_app_client.post(
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [
                {'name': 'driver_license', 'value': driver_license},
                {'name': 'message', 'value': 'message\ntest'},
            ],
            'permission': 'me',
            'topic_id': 'base.topic.driver.simple.no_orders',
            'attachments': ['attachment_id'],
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

    assert stq.support_chat_create_chatterbox_task.has_calls


@pytest.mark.translations(
    opteum_support_chat={
        'field_driver_license_not_valid': {'ru': 'Некорректное ВУ'},
    },
)
@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic_failed_validation_driver_license(
        web_app_client,
        web_app,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mockserver,
        mock_personal_email_store,
        load_json,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _personal_dl_find(request):
        return mockserver.make_response(status=404, json={})

    response = await web_app_client.post(
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [
                {'name': 'driver_license', 'value': 'AB12345678'},
                {'name': 'message', 'value': 'message'},
            ],
            'permission': 'me',
            'topic_id': 'base.topic.driver.simple.no_orders',
            'attachments': ['attachment_id'],
        },
    )

    assert response.status == 400
    data = await response.json()

    assert data['details']
    assert data['details']['driver_license']
    assert data['details']['driver_license'] == 'Некорректное ВУ'


@pytest.mark.translations(
    opteum_support_chat={
        'field_cannot_be_empty': {'ru': 'Поле не может быть пустым!'},
    },
)
@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic_failed_validation_not_empty(
        web_app_client,
        web_app,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_personal_single_license,
        load_json,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    driver_license = 'AB12345678'
    expected_driver_license_pd_id = 'driver_license_pd_id'
    mock_personal_single_license(driver_license, expected_driver_license_pd_id)

    response = await web_app_client.post(
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [
                {'name': 'driver_license', 'value': driver_license},
                {'name': 'message', 'value': '   '},
            ],
            'permission': 'me',
            'topic_id': 'base.topic.driver.simple.no_orders',
            'attachments': ['attachment_id'],
        },
    )

    assert response.status == 400
    data = await response.json()

    assert data['details']
    assert data['details']['message']
    assert data['details']['message'] == 'Поле не может быть пустым!'


@pytest.mark.translations(
    opteum_support_chat={
        'field_are_required': {'ru': 'Поле обязательно для заполнения!'},
    },
)
@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic_failed_validation_required(
        web_app_client,
        web_app,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_personal_single_license,
        load_json,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    driver_license = 'AB12345678'
    expected_driver_license_pd_id = 'driver_license_pd_id'
    mock_personal_single_license(driver_license, expected_driver_license_pd_id)

    response = await web_app_client.post(
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [{'name': 'driver_license', 'value': driver_license}],
            'permission': 'me',
            'topic_id': 'base.topic.driver.simple.no_orders',
            'attachments': ['attachment_id'],
        },
    )

    assert response.status == 400
    data = await response.json()

    assert data['details']
    assert data['details']['message']
    assert data['details']['message'] == 'Поле обязательно для заполнения!'


@pytest.mark.translations(
    opteum_support_chat={
        'field_are_required': {'ru': 'Поле обязательно для заполнения!'},
    },
)
@pytest.mark.now('2020-12-08T16:26:00+03:00')
async def test_success_simple_topic_failed_validation_required_attachments(
        web_app_client,
        web_app,
        headers,
        mock_parks,
        mock_dispatcher_access_control,
        mock_personal_email_store,
        mock_personal_single_license,
        load_json,
        stq,
):
    stub = load_json('success.json')

    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users_list(request):
        if request.json == stub['dac_common_request']:
            return aiohttp.web.json_response(stub['dac_common_response'])
        assert request.json == stub['dac_user_request']
        return aiohttp.web.json_response(stub['dac_user_response'])

    email = 'example@yandex.ru'
    email_pd_id = 'email_personal_id'
    mock_personal_email_store(email, email_pd_id)

    driver_license = 'AB12345678'
    expected_driver_license_pd_id = 'driver_license_pd_id'
    mock_personal_single_license(driver_license, expected_driver_license_pd_id)

    response = await web_app_client.post(
        '/support-chat-api/v2/new',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'email': email,
            'inputs': [
                {'name': 'driver_license', 'value': driver_license},
                {'name': 'message', 'value': 'message'},
            ],
            'permission': 'me',
            'topic_id': 'base.topic.driver.simple.no_orders',
        },
    )

    assert response.status == 400
    data = await response.json()

    assert data['details']
    assert data['details']['attachments']
    assert data['details']['attachments'] == 'Поле обязательно для заполнения!'
