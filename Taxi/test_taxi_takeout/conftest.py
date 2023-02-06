# pylint: disable=redefined-outer-name, unused-variable
import pytest

from taxi import discovery

import taxi_takeout.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_takeout.generated.service.pytest_plugins']

UID_NOT_FOUND = 'uid_not_found'


@pytest.fixture
def mock_archive_api(mockserver, load_json):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    def _mock_select_rows(request):
        return load_json('archive_response.json')


@pytest.fixture
def mock_taximeter_api(patch_aiohttp_session, response_mock, load_json):
    host_url = discovery.find_service('taximeter_xservice').url

    @patch_aiohttp_session(host_url, 'POST')
    def _mock_api(method, url, **kwargs):
        assert url == host_url + '/v1/users/list'
        uids = kwargs['json']['query']['user']['passport_uids']
        assert uids
        if UID_NOT_FOUND in uids:
            return response_mock(json={'users': []})
        return response_mock(json=load_json('taximeter_response.json'))


@pytest.fixture
def mock_support_api(patch_aiohttp_session, response_mock, load_json):
    host_url = discovery.find_service('support_info').url

    @patch_aiohttp_session(host_url, 'POST')
    def _mock_api(method, url, **kwargs):
        assert url == host_url + '/v1/takeout'
        assert kwargs['json'].get('user_phone_id')
        return response_mock(json=load_json('support_response.json'))


@pytest.fixture
def mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_user_phones(request):
        return load_json('user_phones_response.json')

    @mockserver.json_handler('/user-api/user_emails/get')
    def _mock_user_emails(request):
        assert request.json['phone_ids']
        return load_json('user_emails_response.json')

    @mockserver.json_handler('/user-api/users/search')
    def _mock_users(request):
        users = load_json('users_response.json')
        phone_id = request.json['phone_ids'][0]
        yandex_uid = request.json['yandex_uids'][0]
        result = []
        for user in users:
            if (
                    user['yandex_uid'] == yandex_uid
                    and user['phone_id'] == phone_id
            ):
                result.append(user)
        return {'items': result}


@pytest.fixture
def mock_chatterbox_api(
        request, patch_aiohttp_session, response_mock, load_json,
):
    host_url = discovery.find_service('chatterbox').url

    @patch_aiohttp_session(host_url, 'POST')
    def _mock_api(method, url, *args, **kwargs):
        assert url == host_url + '/v33/takeout'
        if kwargs['json']['yandex_uid'] == UID_NOT_FOUND:
            return response_mock(json={'status': 'no_data'})
        return response_mock(
            json=request.param
            if request is not None and request.param is not None
            else {'status': 'ok', 'data': {'key': 'value'}},
        )


@pytest.fixture
def mock_personal_api(mockserver, response_mock, load_json):
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _personal_retrieve_emails(request):
        assert request.json == {
            'items': [{'id': '8acf3a0383de4fd9a6d8866e6c218284'}],
            'primary_replica': False,
        }
        return {
            'items': [
                {
                    'id': '8acf3a0383de4fd9a6d8866e6c218284',
                    'value': 'test@yandex.ru',
                },
            ],
        }
