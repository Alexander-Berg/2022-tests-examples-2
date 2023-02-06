from aiohttp import web
import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_calls', files=['data.sql']),
]


@pytest.mark.parametrize('call_id, status', [('1', 200), ('2', 403)])
async def test_auth_project_access(
        web_app_client, mockserver, call_id, status,
):
    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={
                'contexts': [
                    {
                        'created_at': '2021-04-01 10:00:00+03',
                        'chat_id': '1',
                        'records': [
                            {
                                'id': '1',
                                'created_at': '2021-04-01 10:00:00+03',
                                'request': {
                                    'dialog': {
                                        'messages': [
                                            {'text': '', 'author': 'ai'},
                                        ],
                                    },
                                    'features': [
                                        {'key': 'event_type', 'value': 'dial'},
                                    ],
                                },
                                'response': {
                                    'reply': {'text': '1', 'texts': ['1']},
                                },
                            },
                        ],
                    },
                ],
                'total': 1,
            },
        )

    response_get_call_record = await web_app_client.get(
        f'/v1/calls/{call_id}/result?user_id=34&project_slug=test_ignore',
    )
    assert response_get_call_record.status == status
