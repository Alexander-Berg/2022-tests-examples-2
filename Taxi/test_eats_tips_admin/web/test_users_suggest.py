from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


@pytest.mark.parametrize(
    (
        'jwt',
        'places',
        'ext_result_partners_id',
        'ext_result_partners_places',
        'ext_result_partners_users',
        'ext_result_partners_boxes',
        'expected_status',
        'expected_result',
    ),
    [
        (
            conftest.JWT_USER_1,
            conftest.PLACE_1['id'],
            {'id': conftest.USER_ID_1, 'alias': '8'},
            {
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
                ],
            },
            {
                'has_more': False,
                'partners': [
                    {
                        'info': {
                            'id': conftest.USER_ID_1,
                            'display_name': 'ванька-встанька',
                            'full_name': 'Иван Иванов',
                            'saving_up_for': '',
                            'phone_id': '',
                            'mysql_id': '8',
                            'registration_date': '2020-12-12T03:00:00+03:00',
                            'is_vip': False,
                            'best2pay_blocked': False,
                        },
                        'places': [
                            {
                                'alias': '000080',
                                'place_id': conftest.PLACE_1['id'],
                                'confirmed': True,
                                'show_in_menu': False,
                                'roles': ['admin', 'recipient'],
                                'address': '',
                                'title': '',
                            },
                        ],
                    },
                    {
                        'info': {
                            'id': conftest.USER_ID_2,
                            'display_name': '',
                            'full_name': 'Петр Петров',
                            'saving_up_for': '',
                            'phone_id': '',
                            'mysql_id': '9',
                            'registration_date': '2020-12-12T03:00:00+03:00',
                            'is_vip': False,
                            'best2pay_blocked': False,
                        },
                        'places': [
                            {
                                'alias': '000090',
                                'place_id': conftest.PLACE_1['id'],
                                'confirmed': True,
                                'show_in_menu': False,
                                'roles': ['recipient'],
                                'address': '',
                                'title': '',
                            },
                        ],
                    },
                ],
            },
            {'boxes': [conftest.MONEY_BOX_1]},
            200,
            {
                'users': [
                    {
                        'id': conftest.USER_ID_1,
                        'code': '000080',
                        'alias': '000080',
                        'first_name': 'Иван Иванов',
                        'display_name': 'ванька-встанька',
                        'type': 'partner',
                        'is_admin': True,
                        'is_recipient': True,
                    },
                    {
                        'id': conftest.USER_ID_2,
                        'code': '000090',
                        'alias': '000090',
                        'first_name': 'Петр Петров',
                        'display_name': '',
                        'type': 'partner',
                        'is_admin': False,
                        'is_recipient': True,
                    },
                    {
                        'id': conftest.MONEY_BOX_1['id'],
                        'code': '42',
                        'alias': '42',
                        'first_name': 'копилка',
                        'display_name': 'копилка',
                        'type': 'money_box',
                    },
                ],
            },
        ),
    ],
)
async def test_user_suggest(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        jwt,
        places,
        ext_result_partners_id,
        ext_result_partners_places,
        ext_result_partners_users,
        ext_result_partners_boxes,
        expected_status,
        expected_result,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response(ext_result_partners_id)

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        assert dict(request.query) == {
            'partners_ids': ext_result_partners_id['id'],
        }
        return web.json_response(ext_result_partners_places)

    @mock_eats_tips_partners('/v1/partner/list')
    async def _mock_partner_list(request: http.Request):
        assert dict(request.query) == {'places_ids': places}
        return web.json_response(ext_result_partners_users)

    @mock_eats_tips_partners('/v1/money-box/list')
    async def _mock_list(request: http.Request):
        assert dict(request.query) == {'places_ids': places}
        return web.json_response(ext_result_partners_boxes)

    response = await taxi_eats_tips_admin_web.get(
        '/v1/users/suggest',
        params={'places': places},
        headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
