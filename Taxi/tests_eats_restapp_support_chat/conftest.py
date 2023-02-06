# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_restapp_support_chat_plugins import *  # noqa: F403 F401

USERS = {
    '1': {
        'id': 1,
        'name': 'test1',
        'email': 'test1@yandex.ru',
        'is_blocked': False,
        'places': [111, 222],
        'is_fast_food': False,
        'country_code': '0',
        'roles': [
            {'id': 1, 'title': 'Оператор', 'slug': 'ROLE_OPERATOR'},
            {'id': 2, 'title': 'Управляющий', 'slug': 'ROLE_MANAGER'},
        ],
        'partner_id': '1',
        'timezone': 'UTC',
    },
    '2': {
        'id': 2,
        'name': 'test2',
        'email': 'test2@yandex.ru',
        'is_blocked': False,
        'places': [222, 333],
        'is_fast_food': False,
        'country_code': '0',
        'roles': [{'id': 1, 'title': 'Оператор', 'slug': 'ROLE_OPERATOR'}],
        'partner_id': '2',
        'timezone': 'UTC',
    },
    '3': {
        'id': 3,
        'name': 'test3',
        'is_blocked': False,
        'email': 'test3@yandex.ru',
        'country_code': '0',
        'places': [333, 444],
        'is_fast_food': False,
        'roles': [],
        'partner_id': '3',
        'timezone': 'UTC',
    },
}


@pytest.fixture(autouse=True)
def mock_eats_partners_search(mockserver):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/search')
    def _mock(request):
        place_id = int(request.json['places'][0])
        if place_id == 111:
            return {
                'payload': [USERS['1']],
                'meta': {'cursor': 1, 'can_fetch_next': False, 'count': 1},
            }
        if place_id == 222:
            return {
                'payload': [USERS['1'], USERS['2']],
                'meta': {'cursor': 1, 'can_fetch_next': False, 'count': 2},
            }
        if place_id == 333:
            return {
                'payload': [USERS['2'], USERS['3']],
                'meta': {'cursor': 1, 'can_fetch_next': False, 'count': 1},
            }
        return {'isSuccess': True, 'payload': [], 'meta': {'count': 0}}


@pytest.fixture(autouse=True)
def mock_eats_partners(mockserver):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock(request):
        partner_id = int(request.args['partner_id'])
        if partner_id == 1:
            return {'payload': USERS['1']}
        if partner_id == 2:
            return {'payload': USERS['2']}
        if partner_id == 3:
            return {'payload': USERS['3']}
        return {'payload': []}


@pytest.fixture(autouse=True)
def _mock_daas(mockserver, load_json):
    @mockserver.json_handler('/daas/v1/documents/load/eda-restaurants')
    def _mock(request):
        return load_json('daas_backend_response.json')


@pytest.fixture(autouse=True)
def _mock_yandex_calendar(mockserver, load_json):
    @mockserver.json_handler('/yandex-calendar/internal/get-holidays')
    def _mock(request):
        return load_json('yandex_calendar_response.json')
