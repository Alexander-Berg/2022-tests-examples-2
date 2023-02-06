from aiohttp import web
import pytest

from supportai_tasks import models as db_models


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql']),
]


async def test_sign_up_success(web_context, web_app_client):
    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200

    response_json = await response.json()
    assert 'token' in response_json
    assert 'user_id' in response_json

    async with web_context.pg.slave_pool.acquire() as conn:
        user = await db_models.User.select_by_provider_id(
            web_context, conn, provider_id=response_json['user_id'],
        )
        assert user is not None
        assert user.login == 'totalchest'


async def test_sign_up_fail(web_app_client):
    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'ya_user_1', 'password': '12345'},
    )
    assert response.status == 400


async def test_sign_in_success(web_app_client):
    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/authentication/plain/signin',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200

    response_json = await response.json()
    assert 'token' in response_json
    assert 'user_id' in response_json


@pytest.mark.parametrize(
    ['login', 'password'],
    [('totalchest', '54321'), ('totalchest12345', '12345'), ('ya_user_1', '')],
)
async def test_sign_in_fail(web_app_client, login, password):
    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/authentication/plain/signin',
        json={'login': login, 'password': password},
    )
    assert response.status == 400


async def test_token_authorization_success(
        web_context, web_app_client, mockserver,
):
    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def context_handler(request):
        return web.json_response(
            data={
                'contexts': [
                    {
                        'created_at': '2021-04-01 10:00:00',
                        'chat_id': '123',
                        'records': [
                            {
                                'id': '1',
                                'request': {
                                    'chat_id': '123',
                                    'dialog': {'messages': []},
                                    'features': [],
                                },
                                'response': {
                                    'features': {
                                        'most_probable_topic': 'topic1',
                                        'sure_topic': 'topic1',
                                        'probabilities': [],
                                    },
                                },
                            },
                        ],
                    },
                ],
                'total': 1,
            },
        )

    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200
    response_json = await response.json()

    token = response_json['token']
    user_id = response_json['user_id']

    async with web_context.pg.master_pool.acquire() as conn:
        await db_models.User.insert_role(
            web_context, conn, user_id=1000, role_id=1,
        )

    response = await web_app_client.get(
        f'/v1/dialogs/history?project_id=1&user_id={user_id}',
        headers={'Authorization': f'Bearer {token}', 'provider': 'supportai'},
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'token_template', ['Bearer{token}', 'Bearer {token}aaa'],
)
async def test_token_authorization_fail(
        web_context, web_app_client, token_template,
):
    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200
    response_json = await response.json()

    token = response_json['token']
    user_id = response_json['user_id']

    async with web_context.pg.master_pool.acquire() as conn:
        await db_models.User.insert_role(
            web_context, conn, user_id=1000, role_id=1,
        )

    response = await web_app_client.get(
        f'/v1/dialogs/history?project_id=1&user_id={user_id}',
        headers={
            'Authorization': token_template.format(token=token),
            'provider': 'supportai',
        },
    )
    assert response.status == 403


async def test_check_token(web_app_client):
    response = await web_app_client.post(
        '/v1/authentication/plain/signup',
        json={'login': 'totalchest', 'password': '12345'},
    )
    assert response.status == 200
    response_json = await response.json()

    token = response_json['token']
    user_id = response_json['user_id']

    response = await web_app_client.post(
        f'/v1/authentication/token/check?user_id={user_id}',
        headers={'authorization': f'Bearer {token}', 'provider': 'supportai'},
    )
    assert response.status == 200

    response = await web_app_client.post(
        f'/v1/authentication/token/check?user_id={user_id}',
        headers={
            'authorization': f'Bearer {token}123',
            'provider': 'supportai',
        },
    )
    assert response.status == 403
