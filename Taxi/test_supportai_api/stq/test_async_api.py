import datetime

from aiohttp import web
import pytest

from taxi.stq import async_worker_ng

from supportai_api.stq import runner
from supportai_api.utils import postgres


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_api_tokens', files=['test_async.sql']),
]


@pytest.mark.now('2021-01-01 15:00:00')
@pytest.mark.parametrize('chat_id', ['1234', '4321'])
async def test_task_smoke(stq3_context, mockserver, chat_id):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(data={'reply': {'text': 'hello'}})

    @mockserver.json_handler('/supportai-context/v1/context/dialog')
    async def _(request):
        return web.json_response(
            data={
                'created_at': '2021-04-01 10:00:00+03',
                'chat_id': '1234',
                'dialog': {
                    'messages': [
                        {'text': '1', 'author': 'ai'},
                        {'text': '1', 'author': 'ai'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/supportai-context/v1/context/last')
    # pylint: disable=unused-variable
    async def context_record_handler(request):
        return web.json_response(data={})

    @mockserver.json_handler('/detmir-webim/api/bot/v2/send_message')
    async def _(request):
        return web.json_response(data={})

    await runner.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id=1,
            exec_tries=10,
            reschedule_counter=0,
            queue='supportai_async_api',
        ),
        integrator_id='webim',
        project_id='detmir_dialog',
        chat_id=chat_id,
        action_id='viber',
        request_body={
            'event': 'new_message',
            'chat_id': 12345,
            'message': {'kind': 'visitor', 'text': 'hello'},
        },
    )

    async with stq3_context.pg.master_pool.acquire(log_extra={}) as conn:
        query, args = stq3_context.sqlt.get_async_task_by_project_and_chat(
            project_id='detmir_dialog', chat_id=chat_id,
        )
        rows = await postgres.fetch(conn, query, args)

    if chat_id == '1234':
        assert rows
    else:
        assert not rows


@pytest.mark.config(
    SUPPORTAI_API_ASYNC_SETTINGS={
        'projects': [{'project_id': 'detmir_dialog', 'delay': 3}],
    },
)
async def test_delay(
        stq3_context, mockserver, web_app_client, stq_runner, monkeypatch,
):
    def get_request(text):
        return {
            'event': 'new_message',
            'chat_id': 9999,
            'message': {'kind': 'visitor', 'text': text},
        }

    @mockserver.json_handler('/supportai-context/v1/context/dialog')
    async def _(request):
        return web.json_response(
            data={
                'created_at': '2021-04-01 10:00:00+03',
                'chat_id': '1234',
                'dialog': {
                    'messages': [
                        {'text': '1', 'author': 'ai'},
                        {'text': '1', 'author': 'ai'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/supportai-context/v1/context/last')
    # pylint: disable=unused-variable
    async def context_record_handler(request):
        return web.json_response(data={})

    @mockserver.json_handler('/supportai/supportai/v1/support')
    async def _(request):
        return web.json_response(data={'reply': {'text': 'hello'}})

    @mockserver.json_handler('/detmir-webim/api/bot/v2/send_message')
    async def _(request):
        return web.json_response(data={})

    await web_app_client.post(
        '/supportai-api/v1/external/webim/viber/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json=get_request('hello'),
    )

    async with stq3_context.pg.master_pool.acquire(log_extra={}) as conn:
        query, args = stq3_context.sqlt.get_async_task_by_project_and_chat(
            project_id='detmir_dialog', chat_id='9999',
        )
        rows = await postgres.fetch(conn, query, args)

    assert rows
    assert rows[0]['id'] == 3

    await runner.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id=1,
            exec_tries=10,
            reschedule_counter=0,
            queue='supportai_async_api',
        ),
        integrator_id='webim',
        project_id='detmir_dialog',
        chat_id='9999',
        action_id='viber',
        request_body=get_request('hello'),
    )

    await web_app_client.post(
        '/supportai-api/v1/external/webim/viber/detmir_dialog',
        headers={'X-Real-IP': '185.39.80.146'},
        json=get_request('bye'),
    )

    async with stq3_context.pg.master_pool.acquire(log_extra={}) as conn:
        query, args = stq3_context.sqlt.get_async_task_by_project_and_chat(
            project_id='detmir_dialog', chat_id='9999',
        )
        rows = await postgres.fetch(conn, query, args)
    assert rows
    assert rows[0]['id'] == 3

    now = datetime.datetime.utcnow()
    monkeypatch.setattr(
        'datetime.datetime.utcnow',
        lambda: now + datetime.timedelta(seconds=10),
    )
    await runner.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id=1,
            exec_tries=10,
            reschedule_counter=0,
            queue='supportai_async_api',
        ),
        integrator_id='webim',
        project_id='detmir_dialog',
        chat_id='9999',
        action_id='viber',
        request_body=get_request('hello'),
    )

    async with stq3_context.pg.master_pool.acquire(log_extra={}) as conn:
        query, args = stq3_context.sqlt.get_async_task_by_project_and_chat(
            project_id='detmir_dialog', chat_id='9999',
        )
        rows = await postgres.fetch(conn, query, args)

    assert not rows
