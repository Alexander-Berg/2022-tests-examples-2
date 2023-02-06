import json

import aiohttp.web
import pytest


@pytest.fixture
def taxi_admin_users_info_mocks(mockserver, load_json):
    """Put your mocks here"""

    @mockserver.json_handler('/user_api-api/users/get')
    async def _get_user(request):
        request_json = json.loads(request.get_data())
        user_id = request_json['id']
        try:
            return load_json(f'responses/user-api_users_get_{user_id}.json')
        except FileNotFoundError:
            return aiohttp.web.Response(
                status=404,
                content_type='application/json',
                body=f'{{"code": "404",'
                f' "message": "No user with id {user_id}"}}',
            )

    @mockserver.json_handler('/user_api-api/user_phones/get')
    async def _get_user_phone(request):
        request_json = json.loads(request.get_data())
        phone_id = request_json['id']
        try:
            return load_json(
                f'responses/user-api_user_phones_get_{phone_id}.json',
            )
        except FileNotFoundError:
            return aiohttp.web.Response(
                status=404,
                content_type='application/json',
                body=f'{{"code": "404",'
                f' "message": "No phone with id {phone_id}"}}',
            )


@pytest.mark.parametrize(
    'request_path, expected_status, expected_filename',
    [
        (
            '/v1/raw_objects/user/?user_id=ae96ca7786b44c2a9924c965e314b4b0',
            200,
            'admin-users-info-v1_raw_objects_user.json',
        ),
        (
            '/v1/raw_objects/user/?user_id=no_user_id',
            404,
            'admin-users-info_v1_raw_objects_user_error_404.json',
        ),
        (
            '/v1/raw_objects/user_phone/?phone_id=5c80ff00030553e658087bfe',
            200,
            'admin-users-info-v1_raw_objects_phone.json',
        ),
        (
            '/v1/raw_objects/user_phone/?phone_id=5c80ff00030553e65808ffff',
            404,
            'admin-users-info_v1_raw_objects_phone_error_404.json',
        ),
        (
            '/v1/raw_objects/user_phone/?phone_id=some_bad_phone_id',
            400,
            'admin-users-info_v1_raw_objects_phone_error_400.json',
        ),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.usefixtures('taxi_admin_users_info_mocks')
async def test_get_raw_objects(
        taxi_admin_users_info_web,
        load,
        request_path,
        expected_status,
        expected_filename,
):
    expected_response = json.loads(load(f'responses/{expected_filename}'))

    response = await taxi_admin_users_info_web.get(
        request_path,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    content = await response.json()
    assert response.status == expected_status
    assert content == expected_response
