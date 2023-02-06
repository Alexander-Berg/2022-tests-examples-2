import http

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as http_utils

from test_eats_tips_admin import conftest

DEFAULT_PLACE_LIST = {
    'places': [
        {
            'info': conftest.PLACE_1,
            'partners': [
                {
                    'partner_id': conftest.USER_ID_1,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'confirmed': True,
                },
            ],
        },
        {
            'info': conftest.PLACE_2,
            'partners': [
                {
                    'partner_id': conftest.USER_ID_1,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'confirmed': True,
                },
            ],
        },
    ],
}


DEFAULT_PARTNER_LIST = {
    'has_more': False,
    'partners': [
        {
            'info': {
                'id': conftest.USER_ID_1,
                'display_name': '',
                'full_name': 'Иван Иванов',
                'saving_up_for': '',
                'phone_id': 'phone_id_14',
                'mysql_id': '8',
                'registration_date': '2020-12-12T03:00:00+03:00',
                'is_vip': False,
                'best2pay_blocked': False,
            },
            'places': [
                {
                    'alias': '8',
                    'place_id': conftest.PLACE_1_ID,
                    'confirmed': True,
                    'show_in_menu': False,
                    'roles': ['admin', 'recipient'],
                    'address': '',
                    'title': '',
                },
                {
                    'alias': '9',
                    'place_id': conftest.PLACE_2_ID,
                    'confirmed': True,
                    'show_in_menu': False,
                    'roles': ['admin', 'recipient'],
                    'address': '',
                    'title': '',
                },
            ],
        },
    ],
}


DEFAULT_RESPONSE = {
    'partners': [
        {
            'info': {
                'id': conftest.USER_ID_1,
                'display_name': '',
                'first_name': 'Иван Иванов',
                'last_name': '',
                'phone': '+79000000000',
                'email': '',
                'saving_up_for': '',
            },
            'places': [
                {
                    'id': conftest.PLACE_1_ID,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'name': '',
                    'address': '',
                    'alias': '8',
                },
                {
                    'id': conftest.PLACE_2_ID,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'name': '',
                    'address': '',
                    'alias': '9',
                },
            ],
            'is_admin': True,
            'is_recipient': True,
        },
    ],
    'has_more': False,
}


@pytest.mark.parametrize(
    (
        'params',
        'place_list',
        'partner_list_response',
        'expected_code',
        'expected_response',
    ),
    (
        pytest.param(
            None,
            DEFAULT_PLACE_LIST,
            {'data': DEFAULT_PARTNER_LIST},
            http.HTTPStatus.OK,
            DEFAULT_RESPONSE,
            id='ok',
        ),
        pytest.param(
            {'places': conftest.PLACE_1_ID},
            DEFAULT_PLACE_LIST,
            {'data': DEFAULT_PARTNER_LIST},
            http.HTTPStatus.OK,
            DEFAULT_RESPONSE,
            id='ok-with-query',
        ),
        pytest.param(
            {'places': conftest.PLACE_3_ID},
            DEFAULT_PLACE_LIST,
            None,
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': (
                    f'user has no admin role in place {conftest.PLACE_3_ID}'
                ),
            },
            id='no-owned-place-query',
        ),
        pytest.param(
            {'places': 'not-uuid'},
            DEFAULT_PLACE_LIST,
            None,
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'place_id is not UUID'},
            id='not-uuid',
        ),
        pytest.param(
            None,
            {'places': []},
            None,
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'not found related places'},
            id='no-owned-places',
        ),
        pytest.param(
            None,
            DEFAULT_PLACE_LIST,
            {
                'status': http.HTTPStatus.BAD_REQUEST,
                'data': {'code': 'bad_request', 'message': 'something wrong'},
            },
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'something wrong'},
            id='partner-list-400',
        ),
        pytest.param(
            None,
            DEFAULT_PLACE_LIST,
            {
                'status': http.HTTPStatus.NOT_FOUND,
                'data': {'code': 'not_found', 'message': 'not found!'},
            },
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'not found!'},
            id='partner-list-404',
        ),
    ),
)
@pytest.mark.config(TVM_RULES=[{'src': 'eats-tips-admin', 'dst': 'personal'}])
async def test_partners_list(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mockserver,
        params,
        place_list,
        partner_list_response,
        expected_code,
        expected_response,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http_utils.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '8'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http_utils.Request):
        return web.json_response(place_list)

    @mock_eats_tips_partners('/v1/partner/list')
    async def _mock_partner_list(request: http_utils.Request):
        return web.json_response(**partner_list_response)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _mock_phones_retrieve(request):
        return {
            'items': [
                {'id': item['id'], 'value': f'+79000000000'}
                for item in request.json['items']
            ],
        }

    response = await taxi_eats_tips_admin_web.get(
        '/v1/partners/list',
        headers={'X-Chaevie-Token': conftest.JWT_USER_1},
        params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
