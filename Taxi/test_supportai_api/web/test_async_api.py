import datetime

from aiohttp import web
import pytest

from supportai_api import common
from supportai_api.generated.service.swagger.models import api as api_models
from supportai_api.integrations import base
from supportai_api.integrations import handle
from supportai_api.utils import postgres


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_api_tokens', files=['test_async.sql']),
]


@pytest.mark.config(
    SUPPORTAI_API_ASYNC_SETTINGS={
        'projects': [{'project_id': 'detmir_dialog', 'delay': 10}],
    },
)
async def test_create_async_task_smoke(
        web_app_client, mockserver, monkeypatch,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(data={})

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234/posts/')
    async def _(request):
        return web.json_response(status=200)

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234')
    async def _(request):
        return web.json_response(status=200)

    call_count = 0

    def _get_ok_result():
        nonlocal call_count
        call_count += 1
        return {}

    monkeypatch.setattr(
        base.BaseIntegration, 'get_ok_result', lambda x: _get_ok_result(),
    )

    response = await web_app_client.post(
        '/supportai-api/v1/external/helpdeskeddy/whatsapp/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json={
            'chat_id': '6514612',
            'dialog': {
                'messages': [{'text': 'good morning!', 'author': 'user'}],
            },
            'features': [
                {'key': 'name', 'value': 'Александр'},
                {'key': 'ticket_id', 'value': '1234'},
            ],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {}

    assert call_count == 1


@pytest.mark.config(
    SUPPORTAI_API_ASYNC_SETTINGS={
        'projects': [{'project_id': 'detmir_dialog', 'delay': 10}],
    },
)
@pytest.mark.parametrize(
    ('project_id', 'is_async', 'is_delayed'),
    [
        ('detmir_dialog', False, False),
        ('detmir_dialog', True, True),
        ('other_project', False, False),
    ],
)
async def test_delay(
        web_context, mockserver, project_id, is_async, is_delayed,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(data={'close': {}})

    empty_request = api_models.SupportRequest(
        dialog=api_models.Dialog(messages=[]), features=[],
    )

    response, delay = await common.get_internal_support_response(
        body=empty_request,
        context=web_context,
        project_id=project_id,
        is_async=is_async,
    )
    if is_delayed:
        assert response.close is None
        assert delay == 10
    else:
        assert response.close
        assert delay is None


@pytest.mark.parametrize(
    ('project_id', 'chat_id', 'task_id'),
    [('detmir_dialog', '9876', 2), ('detmir_dialog', '4321', 1)],
)
async def test_start_async_task(web_context, project_id, chat_id, task_id):
    integrator_id = 'helpdeskeddy'
    action_id = 'whatsapp'
    request_body = {
        'chat_id': chat_id,
        'dialog': {'messages': [{'text': 'good morning!', 'author': 'user'}]},
        'features': [
            {'key': 'name', 'value': 'Александр'},
            {'key': 'ticket_id', 'value': '1234'},
        ],
    }

    await handle.start_async_task(
        context=web_context,
        log_extra={},
        delay=10,
        integrator_id=integrator_id,
        project_id=project_id,
        chat_id=chat_id,
        action_id=action_id,
        request_body=request_body,
        features=[],
    )

    async with web_context.pg.master_pool.acquire(log_extra={}) as conn:
        query, args = web_context.sqlt.get_async_task_by_project_and_chat(
            project_id=project_id, chat_id=chat_id,
        )
        rows = await postgres.fetch(conn, query, args)

    assert len(rows) == 1
    row = rows[0]
    assert row['id'] == task_id
    assert row['project_id'] == project_id
    assert row['chat_id'] == chat_id
    assert row['wait_until'] > datetime.datetime.utcnow()
    assert row['wait_until'] < datetime.datetime.utcnow() + datetime.timedelta(
        seconds=20,
    )
