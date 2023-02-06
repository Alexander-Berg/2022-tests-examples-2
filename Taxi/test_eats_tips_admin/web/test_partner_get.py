import http

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as http_utils

from test_eats_tips_admin import conftest


def _create_partner(user_id):
    return {
        'id': user_id,
        'alias': '0000100',
        'b2p_id': '10',
        'mysql_id': '10',
        'display_name': 'Василий',
        'full_name': 'Василий Иванович Чапаев',
        'phone_id': '123456',
        'saving_up_for': 'лодку',
        'is_vip': False,
        'registration_date': '1970-01-01T06:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token1',
        'best2pay_blocked': False,
    }


def _create_place(place_id, confirmed, show_in_menu, roles, title):
    return {
        'address': '',
        'confirmed': confirmed,
        'place_id': place_id,
        'roles': roles,
        'show_in_menu': show_in_menu,
        'title': title,
    }


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
                    'roles': ['recipient'],
                    'show_in_menu': False,
                    'confirmed': True,
                },
            ],
        },
    ],
}

DEFAULT_PARTNER_RESPONSE = {
    'info': _create_partner(conftest.USER_ID_1),
    'places': [
        _create_place(
            conftest.PLACE_1_ID,
            True,
            False,
            ['recipient', 'unknown'],
            'Заведение 1',
        ),
        _create_place(
            conftest.PLACE_3_ID, True, True, ['admin'], 'Заведение 2',
        ),
    ],
}

ANOTHER_PARTNER_RESPONSE = {
    'info': _create_partner(conftest.USER_ID_3),
    'places': [
        _create_place(
            conftest.PLACE_3_ID, True, True, ['admin'], 'Заведение 2',
        ),
    ],
}

PARTNER = {
    'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8',
    'display_name': 'Василий',
    'first_name': 'Василий Иванович Чапаев',
    'last_name': '',
    'phone': '+79123456789',
    'email': '',
    'saving_up_for': 'лодку',
}
PLACE_1 = {
    'id': 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e',
    'roles': ['recipient'],
    'show_in_menu': False,
    'name': 'Заведение 1',
    'address': '',
}
PLACE_2 = {
    'id': 'd5e6929e-c92a-4282-9d2e-3a8b233bb510',
    'roles': ['admin'],
    'show_in_menu': True,
    'name': 'Заведение 2',
    'address': '',
}


@pytest.mark.parametrize(
    (
        'params',
        'jwt_token',
        'place_list_response',
        'partner_response',
        'expected_code',
        'expected_response',
    ),
    (
        pytest.param(
            None,
            conftest.JWT_USER_1,
            DEFAULT_PLACE_LIST,
            {'status': http.HTTPStatus.OK, 'data': DEFAULT_PARTNER_RESPONSE},
            http.HTTPStatus.OK,
            {
                'info': PARTNER,
                'places': [PLACE_1, PLACE_2],
                'is_admin': True,
                'is_recipient': True,
            },
            id='OK',
        ),
        pytest.param(
            {'partner_id': conftest.USER_ID_2},
            conftest.JWT_USER_1,
            DEFAULT_PLACE_LIST,
            {'status': http.HTTPStatus.OK, 'data': DEFAULT_PARTNER_RESPONSE},
            http.HTTPStatus.OK,
            {
                'info': PARTNER,
                'places': [PLACE_1],
                'is_admin': False,
                'is_recipient': True,
            },
            id='by-admin',
        ),
        pytest.param(
            {'partner_id': conftest.USER_ID_3},
            conftest.JWT_USER_1,
            DEFAULT_PLACE_LIST,
            {'status': http.HTTPStatus.OK, 'data': ANOTHER_PARTNER_RESPONSE},
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': 'user has no permissions for this action',
            },
            id='not-owned-places',
        ),
        pytest.param(
            {'partner_id': conftest.USER_ID_3},
            conftest.JWT_USER_1,
            {
                'places': [
                    {
                        'info': conftest.PLACE_2,
                        'partners': [
                            {
                                'partner_id': conftest.USER_ID_3,
                                'roles': ['recipient'],
                                'show_in_menu': False,
                                'confirmed': True,
                            },
                        ],
                    },
                ],
            },
            None,
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': 'user has no permissions for this action',
            },
            id='no-admin-places',
        ),
        pytest.param(
            {'partner_id': 'not-uuid'},
            conftest.JWT_USER_1,
            DEFAULT_PLACE_LIST,
            {'status': http.HTTPStatus.OK, 'data': DEFAULT_PARTNER_RESPONSE},
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'partner_id must be UUID'},
            id='not-uuid',
        ),
        pytest.param(
            None,
            conftest.JWT_USER_1,
            DEFAULT_PLACE_LIST,
            {
                'status': http.HTTPStatus.BAD_REQUEST,
                'data': {'code': 'bad_request', 'message': 'some error'},
            },
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'some error'},
            id='partners-400',
        ),
        pytest.param(
            None,
            conftest.JWT_USER_1,
            DEFAULT_PLACE_LIST,
            {
                'status': http.HTTPStatus.NOT_FOUND,
                'data': {
                    'code': 'not_found',
                    'message': 'something not found',
                },
            },
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'something not found'},
            id='partners-404',
        ),
    ),
)
@pytest.mark.config(TVM_RULES=[{'src': 'eats-tips-admin', 'dst': 'personal'}])
async def test_partners_get(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mockserver,
        params,
        jwt_token,
        place_list_response,
        partner_response,
        expected_code,
        expected_response,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http_utils.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '8'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http_utils.Request):
        return web.json_response(place_list_response)

    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v2_partner_get(request: http_utils.Request):
        return web.json_response(**partner_response)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _mock_phones_retrieve(request):
        return {'value': '+79123456789', 'id': request.json['id']}

    response = await taxi_eats_tips_admin_web.get(
        '/v1/partners', headers={'X-Chaevie-Token': jwt_token}, params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
