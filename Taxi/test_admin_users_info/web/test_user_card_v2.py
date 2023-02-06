import json

from aiohttp import web
import pytest

from test_admin_users_info import utils


@pytest.fixture
def mock_admin_user_info_services(mockserver, load_json):
    @mockserver.json_handler('/user_api-api/users/search')
    def _search_users(request):
        request_data = json.loads(request.get_data())
        yandex_uid = request_data.get('yandex_uid')
        user_docs = load_json('user_docs.json')
        items = []
        for user_doc in user_docs:
            if yandex_uid == user_doc['requested_yandex_uid']:
                items.append(user_doc['response'])
        return web.json_response({'items': items}, status=200)

    @mockserver.json_handler('/user_api-api/user_phones/get')
    def _get_user_phone(request):
        request_data = json.loads(request.get_data())
        phone_id = request_data.get('id')
        phone_docs = load_json('phone_docs.json')
        for phone_doc in phone_docs:
            if phone_id == phone_doc['requested_phone_id']:
                return phone_doc['response']

        return web.json_response({}, status=404)

    @mockserver.json_handler('/user_api-api/user_emails/get')
    def _get_user_email(request):
        request_data = json.loads(request.get_data())
        phone_ids = request_data.get('phone_ids', [])
        email_docs = load_json('email_docs.json')
        items = []
        for email_doc in email_docs:
            if email_doc['phone_id'] in phone_ids:
                items.append(email_doc)
        return {'items': items}

    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    def _select_rows(request):
        request_data = json.loads(request.get_data())
        _, user_id = request_data.get('query', {}).get('query_params', [])
        archive_docs = load_json('archive_docs.json')
        for archive_doc in archive_docs:
            if user_id == archive_doc['requested_user_id']:
                return archive_doc['response']
        return web.json_response({}, status=404)


@pytest.fixture
def mock_zalogin(mockserver, load_json):
    @mockserver.json_handler('/zalogin/admin/uid-info')
    def _mock_uid_info(request):
        uid_docs = load_json('zalogin_docs.json')
        for uid in uid_docs:
            if uid['requested_uid'] == request.query['yandex_uid']:
                return web.json_response(uid['response'], status=200)
        return web.json_response(
            {'code': '409', 'message': 'Conflict'}, status=409,
        )


@pytest.fixture
def mock_passenger_profile(mockserver, load_json):
    @mockserver.json_handler('/passenger-profile/v1/admin/profile/')
    def _mock_admin_profile(request):
        profile_docs = load_json('passenger_profile_docs.json')
        profiles = []
        for profile in profile_docs:
            if profile['yandex_uid'] in request.query['yandex_uids']:
                profiles.append(profile)
        return web.json_response({'profiles': profiles}, status=200)


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'query, expected_status, expected_filename',
    [
        pytest.param(
            {'yandex_uid': 'unknown'},
            500,
            'response_unknown.json',
            id='non_existing_user',
        ),
        pytest.param(
            {'yandex_uid': '00000000'},
            200,
            'response_00000000.json',
            id='almost_empty_response',
        ),
        pytest.param(
            {'yandex_uid': '00000001'},
            200,
            'response_00000001.json',
            id='simple_test',
        ),
        pytest.param(
            {'yandex_uid': '00000002'},
            200,
            'response_00000002.json',
            id='extended_test',
        ),
    ],
)
@pytest.mark.usefixtures(
    'mock_admin_user_info_services', 'mock_zalogin', 'mock_passenger_profile',
)
async def test_get_user_card_v2(
        taxi_admin_users_info_web,
        web_app_client,
        load_json,
        query,
        expected_status,
        expected_filename,
):

    response = await utils.make_get_request(
        web_app_client, '/v2/user_card', params=query,
    )
    expected_response = load_json(f'responses/{expected_filename}')
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_response
