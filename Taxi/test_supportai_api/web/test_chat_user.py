import datetime
import typing as tp
import uuid

from aiohttp import web
import pytest

from supportai_api.integrations import handle as handle_module


def get_body(chat_user: tp.Union[str, int]) -> tp.Dict:
    return {
        'dialog': {'messages': [{'text': 'I need help', 'author': 'user'}]},
        'features': [
            {'key': 'user_name', 'value': chat_user},
            {'key': 'ticket_id', 'value': '1234'},
        ],
        'chat_id': '1',
    }


@pytest.mark.config(
    SUPPORTAI_API_CONTEXT={
        'projects': 'all',
        'projects_settings': [
            {
                'project_id': 'detmir_dialog',
                'chat_user_feature': 'user_name',
                'split_by': 'chat_user',
                'chat_duration': 12,
            },
        ],
    },
)
async def test_merging_by_chat_user(web_context, mockserver, monkeypatch):
    @mockserver.json_handler('/supportai-context/v1/context/last')
    # pylint: disable=unused-variable
    async def last_handler(request):
        if request.query['chat_user'] == 'user_1':
            return web.json_response(
                data={
                    'chat_id': '2',
                    'created_at': '2010-03-01 09:00:00',
                    'records': [],
                },
            )
        return web.json_response(
            data={
                'chat_id': '2',
                'created_at': str(datetime.datetime.now()),
                'records': [],
            },
        )

    @mockserver.json_handler('/supportai-context/v1/context/dialog')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(
            data={
                'chat_id': '999',
                'created_at': '2021-03-01 09:00:00',
                'dialog': {
                    'messages': [
                        {'text': 'else', 'author': 'user'},
                        {'text': 'else', 'author': 'ai'},
                    ],
                },
            },
        )

    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def support_handler(request):
        chat_id = request.json.get('chat_id')
        return web.json_response(
            data={'reply': {'text': chat_id, 'texts': [chat_id]}},
        )

    @mockserver.json_handler('/supportai-context/v1/context/record')
    # pylint: disable=unused-variable
    async def post_context_handler(request):
        return web.json_response(status=200)

    counter = 0

    @mockserver.json_handler('/helpdeskeddy-detmir/api/v2/tickets/1234/posts/')
    async def _(request):
        nonlocal counter
        counter += 1

        if counter == 1:
            assert request.json['text'] == 'b421800b29124fc79175a41263808430'
        else:
            assert request.json['text'] == '2'
        return web.json_response(status=200)

    monkeypatch.setattr(
        'uuid.uuid4',
        lambda: uuid.UUID('b421800b-2912-4fc7-9175-a41263808430'),
    )

    response = await handle_module.handle_abstract_request(
        context=web_context,
        log_extra={},
        integrator_id='helpdeskeddy',
        action_id='whatsapp',
        project_id='detmir_dialog',
        request_body=get_body('user_1'),
        original_request=None,
    )

    assert response == {}

    response = await handle_module.handle_abstract_request(
        context=web_context,
        log_extra={},
        integrator_id='helpdeskeddy',
        action_id='whatsapp',
        project_id='detmir_dialog',
        request_body=get_body(2),
        original_request=None,
    )

    assert response == {}
