import json

from aiohttp import web
import pytest

from test_admin_users_info import utils

PERMISSIONS = ['view_deleted_users']


@pytest.fixture
def mock_admin_user_info_services(mockserver, load_json):
    @mockserver.json_handler('/user_api-api/users/get')
    def _get_users(request):
        request_data = json.loads(request.get_data())
        user_id = request_data.get('id')
        user_docs = load_json('user_docs.json')
        for user_doc in user_docs:
            if user_id == user_doc['requested_user_id']:
                return user_doc['response']
        return web.json_response({}, status=404)

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

    @mockserver.json_handler('/archive-api/archive/order')
    def _get_order(request):
        request_data = json.loads(request.get_data())
        order_id = request_data.get('id')
        order_docs = load_json('order_docs.json')
        for order_doc in order_docs:
            if order_id == order_doc['requested_order_id']:
                return order_doc['response']
        return web.json_response({}, status=404)


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'query, expected_status, expected_response',
    [
        (
            {'user_id': '00000001'},
            200,
            {
                'user_id': '00000001',
                'vip_user': True,
                'has_ya_plus': True,
                'yandex_staff': True,
                'taxi_staff': True,
                'is_phone_deleted': False,
                'application': 'android',
                'application_version': '3.80.6288',
                'personal_phone_id': 'personal_phone_id_1',
                'personal_email_id': 'personal_email_id_1',
                'last_block': {},
                'yandex_uuid': '0000000001',
                'yandex_uid': '0000000002',
                'phone_type': 'yandex',
                'phone_id': '5887a4e1bdc41c2bce7fe001',
            },
        ),
        (
            {'user_id': '00000002'},
            200,
            {
                'user_id': '00000002',
                'vip_user': False,
                'has_ya_plus': False,
                'last_block': {},
                'phone_id': '5887a4e1bdc41c2bce7fe002',
            },
        ),
        (
            {'user_id': '00000003'},
            200,
            {
                'user_id': '00000003',
                'vip_user': True,
                'yandex_staff': True,
                'taxi_staff': True,
                'last_block': {},
                'personal_phone_id': 'personal_phone_id_3',
                'phone_type': 'any_type_for_deleted',
                'phone_id': '5887a4e1bdc41c2bce7fe003',
                'is_phone_deleted': True,
            },
        ),
        ({'user_id': 'not_found_user'}, 404, {'message': 'user not found'}),
        # проверка user с отсутсвующим телефоном, т.е. нет phone_doc
        (
            {'user_id': '00000005'},
            200,
            {
                'user_id': '00000005',
                'vip_user': False,
                'has_ya_plus': True,
                'yandex_staff': True,
                'taxi_staff': True,
                'application': 'android',
                'application_version': '3.80.6288',
                'last_block': {},
                'yandex_uuid': '0000000005',
                'yandex_uid': '0000000006',
                'phone_id': '5887a4e1bdc41c2bce7fe005',
            },
        ),
    ],
)
# pylint: disable=W0621
async def test_get_user_card(
        web_app_client,
        query,
        expected_status,
        expected_response,
        mock_admin_user_info_services,
        mock_passenger_profile,
        mock_zalogin,
):
    @mock_passenger_profile('/v1/admin/profile/')
    def _mock_admin_profile(request):
        return web.json_response({'profiles': []}, status=200)

    @mock_zalogin('/v1/internal/uid-info')
    def _mock_uid_info(request):
        response_body = {'code': '409', 'message': 'UID not found'}
        return web.json_response(response_body, status=409)

    with utils.has_permissions(PERMISSIONS):
        response = await utils.make_get_request(
            web_app_client, '/v1/user_card', params=query,
        )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_response


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.parametrize(
    'query, expected_type, expected_bound_uids, expected_profiles',
    [
        # user without yandex_uid
        ({'user_id': '00000002'}, '', [], []),
        # no such uid-info in zalogin
        ({'user_id': '1002'}, '', [], []),
        # no such passenger-profiles
        ({'user_id': '1003'}, 'portal', [], []),
        # phonish without bound portal
        (
            {'user_id': '1004'},
            'phonish',
            [],
            [
                {
                    'first_name': 'Alex',
                    'rating': '4.4',
                    'yandex_uid': '1004',
                    'brand': 'yataxi',
                },
            ],
        ),
        # phonish with bound portal
        (
            {'user_id': '1005'},
            'phonish',
            ['1006'],
            [
                {
                    'first_name': 'Alex',
                    'rating': '4.5',
                    'yandex_uid': '1005',
                    'brand': 'yataxi',
                },
            ],
        ),
        # portal without bound phonishes
        (
            {'user_id': '1006'},
            'portal',
            [],
            [
                {
                    'first_name': 'Bob',
                    'rating': '4.6',
                    'yandex_uid': '1006',
                    'brand': 'yauber',
                },
            ],
        ),
        # portal with bound phonishes
        (
            {'user_id': '1007'},
            'portal',
            ['1004', '1005'],
            [
                {
                    'first_name': 'Bob',
                    'rating': '4.7',
                    'yandex_uid': '1007',
                    'brand': 'yauber',
                },
                {
                    'first_name': 'Alex',
                    'rating': '4.4',
                    'yandex_uid': '1004',
                    'brand': 'yataxi',
                },
                {
                    'first_name': 'Alex',
                    'rating': '4.5',
                    'yandex_uid': '1005',
                    'brand': 'yataxi',
                },
            ],
        ),
    ],
)
# pylint: disable=W0621
async def test_user_card_profiles(
        web_app_client,
        query,
        expected_type,
        expected_bound_uids,
        expected_profiles,
        mock_admin_user_info_services,
        mock_zalogin,
        mock_passenger_profile,
        load_json,
):
    @mock_passenger_profile('/v1/admin/profile/')
    def _mock_admin_profile(request):
        profile_docs = load_json('passenger_profile_docs.json')
        for profile in profile_docs:
            if profile['requested_uids'] == request.query['yandex_uids']:
                return web.json_response(profile['response'], status=200)
        return web.json_response({'profiles': []}, status=200)

    @mock_zalogin('/v1/internal/uid-info')
    def _mock_uid_info(request):
        uid_docs = load_json('zalogin_docs.json')
        for uid in uid_docs:
            if uid['requested_uid'] == request.query['yandex_uid']:
                return web.json_response(uid['response'], status=200)
        return web.json_response(
            {'code': '409', 'message': 'Conflict'}, status=409,
        )

    with utils.has_permissions(PERMISSIONS):
        response = await utils.make_get_request(
            web_app_client, '/v1/user_card', params=query,
        )

    assert response.status == 200
    content = await response.json()

    assert (not expected_type and 'uid_type' not in content) or content[
        'uid_type'
    ] == expected_type
    assert (
        not expected_bound_uids and 'bound_uids' not in content
    ) or content['bound_uids'] == expected_bound_uids
    assert (
        not expected_profiles and 'user_profiles' not in content
    ) or content['user_profiles']['profiles'] == expected_profiles
