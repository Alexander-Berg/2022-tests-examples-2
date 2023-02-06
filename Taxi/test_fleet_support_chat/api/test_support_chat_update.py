import aiohttp.web
import pytest


@pytest.mark.now('2020-09-30T15:07:30+00:00')
async def test_success(
        web_app_client,
        headers,
        mock_dac_users,
        mock_support_chat,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_support_chat('/v1/chat/chat_id')
    async def _info(request):
        return aiohttp.web.json_response(stub['support_chat_info_response'])

    @mock_support_chat('/v1/chat/chat_id/add_update')
    async def _add_update(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(
            stub['support_chat_response'], status=201,
        )

    @patch('fleet_support_chat.api.support_chat_update._run_stq_task')
    async def _run_stq_task(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/support-chat-api/v1/update',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'chat_id': 'chat_id',
            'text': 'new message',
            'attachments': None,
            'csat_value': None,
            'csat_reasons': None,
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.now('2020-09-30T15:07:30+00:00')
async def test_success_csat(
        web_app_client,
        headers,
        mock_dac_users,
        mock_support_chat,
        load_json,
        patch,
):
    stub = load_json('success_csat.json')

    @mock_support_chat('/v1/chat/chat_id')
    async def _info(request):
        return aiohttp.web.json_response(stub['support_chat_info_response'])

    @mock_support_chat('/v1/chat/chat_id/add_update')
    async def _add_update(request):
        assert request.json == stub['support_chat_request']
        return aiohttp.web.json_response(
            stub['support_chat_response'], status=201,
        )

    @patch('fleet_support_chat.api.support_chat_update._run_stq_task')
    async def _run_stq_task(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/support-chat-api/v1/update',
        headers={'X-Idempotency-Token': '1', **headers},
        json={
            'chat_id': 'chat_id',
            'text': '',
            'attachments': None,
            'csat_value': 3,
            'csat_reasons': ['template_answer'],
        },
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.now('2020-09-30T15:07:30+00:00')
async def test_closed(
        web_app_client,
        headers,
        mock_dac_users,
        mock_support_chat,
        load_json,
        patch,
):
    stub = load_json('closed.json')

    @mock_support_chat('/v1/chat/chat_id')
    async def _info(request):
        return aiohttp.web.json_response(stub['support_chat_info_response'])

    response = await web_app_client.post(
        '/support-chat-api/v1/update',
        headers={'X-Idempotency-Token': '1', **headers},
        json={
            'chat_id': 'chat_id',
            'text': 'new message',
            'attachments': None,
            'csat_value': None,
            'csat_reasons': None,
        },
    )

    assert response.status == 400
