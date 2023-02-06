# pylint: disable=unused-variable
from aiohttp import web
import pytest


@pytest.mark.parametrize(
    ['params'],
    [
        ({'lines': ['first', 'second'], 'logins': ['user_1']},),
        ({'logins': ['user_2']},),
        ({'lines': ['first', 'new']},),
        ({},),
    ],
)
async def test_chatterbox_stats(web_app_client, params, mock_chatterbox_py3):
    @mock_chatterbox_py3('/v1/users/statuses', prefix=True)
    def handler(request):
        assert request.query.getall('lines', []) == params.get('lines', [])
        assert request.query.getall('logins', []) == params.get('logins', [])
        return web.json_response(
            {
                'users': [
                    {
                        'current_status': 'online',
                        'time_spent_in_status': 60,
                        'login': 'user_1',
                        'lines': ['first', 'second'],
                    },
                    {
                        'current_status': 'offline',
                        'time_spent_in_status': 120,
                        'login': 'user_2',
                        'lines': ['new'],
                    },
                ],
            },
        )

    params_to_send = {}
    for key, value in params.items():
        if isinstance(value, list):
            value = '|'.join(value)
        params_to_send[key] = value
    response = await web_app_client.get(
        '/v1/chatterbox/users/stat', params=params_to_send,
    )
    data = await response.json()

    assert data == {
        'users': [
            {
                'current_status': 'online',
                'time_spent_in_status': 60,
                'login': 'user_1',
                'lines': ['first', 'second'],
            },
            {
                'current_status': 'offline',
                'time_spent_in_status': 120,
                'login': 'user_2',
                'lines': ['new'],
            },
        ],
    }
