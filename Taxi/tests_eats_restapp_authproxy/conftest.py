# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_restapp_authproxy_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_eats_restapp_authorizer(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/session/current')
    def _mock_sessions(req):
        if req.json['token'] == 'wrong_token':
            return mockserver.make_response(status=404)
        return mockserver.make_response(
            status=200,
            json={'partner_id': 41, 'email': 'vkoorits@yandex-team.ru'},
        )


@pytest.fixture
def mock_error_restapp_authorizer(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/session/current')
    def _mock_sessions(req):
        return mockserver.make_response(status=400)


@pytest.fixture
def mock_access_control(mockserver, request):
    @mockserver.json_handler('/access-control/v1/get-user-access-info/')
    def _mock_access_control(request):
        return mockserver.make_response(
            status=200,
            json={
                'permissions': [
                    'orders_cancel',
                    'orders_common',
                    'orders_history',
                ],
                'evaluated_permissions': [],
                'restrictions': [],
                'roles': [
                    {
                        'role': 'orders_cancel',
                        'permissions': ['orders_cancel'],
                        'evaluated_permissions': [],
                        'restrictions': [],
                    },
                    {
                        'role': 'orders_common',
                        'permissions': ['orders_common'],
                        'evaluated_permissions': [],
                        'restrictions': [],
                    },
                    {
                        'role': 'orders_history',
                        'permissions': ['orders_history'],
                        'evaluated_permissions': [],
                        'restrictions': [],
                    },
                ],
            },
        )


@pytest.fixture
def mock_return_partner_info_200(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_200(request):
        payload = {
            'country_code': 'RU',
            'email': 'partner1@partner.com',
            'personal_email_id': '999',
            'id': 1,
            'is_blocked': False,
            'is_fast_food': False,
            'name': 'Партнер1',
            'partner_id': '1b9d70ef-d667-4c9c-9b20-c61209ea6332',
            'places': [123, 234, 343],
            'roles': [
                {'id': 1, 'slug': 'ROLE_ADMIN', 'title': 'admin'},
                {'id': 2, 'slug': 'ROLE_LOL', 'title': 'lol'},
            ],
            'timezone': 'Europe/Moscow',
        }
        return mockserver.make_response(status=200, json={'payload': payload})


@pytest.fixture
def mock_return_partner_info_400(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_400(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Bad request'},
        )


@pytest.fixture
def mock_return_partner_info_404(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_400(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Partner not found'},
        )


@pytest.fixture
def mock_return_partner_info_500(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_response_400(request):
        return mockserver.make_response(
            status=500,
            json={'code': '500', 'message': 'Internal server error'},
        )
