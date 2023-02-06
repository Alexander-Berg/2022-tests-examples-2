# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import re

import pytest

from eats_partners_plugins import *  # noqa: F403 F401


DATA_PERSONAL_BULK = {
    '111': 'partner1@partner.com',
    '222': 'partner2@partner.com',
    '333': 'partner3@partner.com',
    '444': 'partner4@partner.com',
    '555': 'partner5@partner.com',
    '666': 'partner6@partner.com',
    '777': 'partner7@partner.com',
    '888': 'partner8@partner.com',
    '999': 'partner9@partner.com',
    '000': 'partner10@partner.com',
}


@pytest.fixture
def mock_communications_sender(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)


@pytest.fixture
def mock_vendor_users_create(mockserver, request):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users')
    def _mock_vendor_users_create(req):
        return mockserver.make_response(
            status=200, json={'isSuccess': True, 'payload': {'id': 42}},
        )


@pytest.fixture
def mock_personal_retrieve(mockserver, request):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _email_retrieve(request):
        return {
            'id': request.json['id'],
            'value': request.json['id'].replace('_id', ''),
        }


@pytest.fixture
def mock_personal_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _emails_bulk_retrieve(request):
        data = []
        for email_id in request.json['items']:
            assert email_id['id'] != ''
            data.append(
                {
                    'id': email_id['id'],
                    'value': DATA_PERSONAL_BULK[email_id['id']],
                },
            )
        return {'items': data}


@pytest.fixture
def mock_personal_store(mockserver, request):
    @mockserver.json_handler('/personal/v1/emails/store')
    def _email_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }


@pytest.fixture
def mock_personal_find(mockserver, request):
    @mockserver.json_handler('/personal/v1/emails/find')
    def _email_find(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }


@pytest.fixture
def mock_vendor_users_create_error(mockserver, request):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users')
    def _mock_vendor_users_create_error(req):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'errors': [{'code': 420, 'message': 'some vendor error'}],
            },
        )


@pytest.fixture
def mock_vendor_users_update(mockserver, request):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users/1')
    def _mock_vendor_users_create_error(req):
        return mockserver.make_response(
            status=200,
            json={
                'isSuccess': True,
                'payload': {
                    'id': 1,
                    'name': 'nananuna',
                    'email': 'nananina@na.na',
                    'restaurants': [343, 454],
                    'isFastFood': True,
                    'timezone': 'utc',
                    'roles': [
                        {
                            'id': 1,
                            'title': 'operator',
                            'role': 'ROLE_OPERATOR',
                        },
                    ],
                },
            },
        )


@pytest.fixture
def mock_vendor_users_update_error(mockserver, request):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users/1')
    def _mock_vendor_users_create_error(req):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'errors': [{'code': 420, 'message': 'some vendor error'}],
            },
        )


@pytest.fixture
def mock_vendor_users_empty_search(mockserver, request):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users/search')
    def _mock_vendor_users_empty_search(req):
        return mockserver.make_response(
            status=200,
            json={'isSuccess': True, 'payload': [], 'meta': {'count': 0}},
        )


def mock_sender_success(mockserver, slug, **kwargs):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/{}/send'.format(slug),
    )
    def _mock_sender_success(req):
        for param, matcher in kwargs.items():
            assert matcher(
                req.json.get('args', {}).get(param),
            ), '"{}" does not match'.format(param)
        return mockserver.make_response(
            status=200,
            json={
                'result': {
                    'status': 'OK',
                    'task_id': '2258a15b-6209-44f9-841b-53ac1f47fa52',
                    'message_id': (
                        '<20200507080804@api-10.production.ysendercloud>'
                    ),
                },
            },
        )

    return _mock_sender_success


@pytest.fixture
def mock_sender_request_reset(mockserver, request):
    return mock_sender_success(
        mockserver,
        slug='8Y2IS654-4J2',
        link=lambda x: re.match(r'localhost\/reset\?token\=.+\&email\=.+', x)
        is not None,
        locale=lambda x: x == 'ru',
    )


@pytest.fixture
def mock_sender_password_reset(mockserver, request):
    return mock_sender_success(
        mockserver,
        slug='GO9NS654-NQ31',
        password=bool,
        locale=lambda x: x == 'ru',
    )


@pytest.fixture
def mock_sender_partnerish_register(mockserver, request):
    return mock_sender_success(
        mockserver, slug='8UQ5MY64-1E32', locale=lambda x: x == 'ru',
    )
