from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


@pytest.mark.parametrize(
    (
        'jwt',
        'ext_result_partners_id',
        'ext_result_partners_places',
        'expected_status',
        'expected_result',
    ),
    [
        (
            conftest.JWT_USER_1,
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
            200,
            {
                'places': [
                    {
                        'alias': '0000090',
                        'id': conftest.PLACE_1['id'],
                        'roles': ['admin', 'recipient'],
                        'name': 'заведение',
                        'show_in_menu': False,
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
        ext_result_partners_id,
        ext_result_partners_places,
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

    response = await taxi_eats_tips_admin_web.get(
        '/v1/places/suggest', headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
