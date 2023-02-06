from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


@pytest.mark.parametrize(
    (
        'jwt',
        'alias_to_id_response',
        'places_status',
        'places_response',
        'box_status',
        'box_response',
        'delete_status',
        'delete_response',
        'box_id',
        'expected_status',
    ),
    (
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            200,
            conftest.MONEY_BOX_1,
            204,
            None,
            conftest.MONEY_BOX_1['id'],
            204,
            id='normal-delete',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_UNCONFIRMED,
            200,
            conftest.MONEY_BOX_1,
            '',
            '',
            conftest.MONEY_BOX_1['id'],
            403,
            id='not-confirmed',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_RECIPIENT,
            200,
            conftest.MONEY_BOX_1,
            '',
            '',
            conftest.MONEY_BOX_1['id'],
            403,
            id='not-admin',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_2_USER_1_BOTH,
            200,
            conftest.MONEY_BOX_1,
            '',
            '',
            conftest.MONEY_BOX_1['id'],
            403,
            id='not-related',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            200,
            conftest.MONEY_BOX_1,
            404,
            None,
            conftest.MONEY_BOX_1['id'],
            404,
            id='partners-error-404',
        ),
    ),
)
async def test_money_box_delete(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        web_context,
        jwt,
        alias_to_id_response,
        places_status,
        places_response,
        box_status,
        box_response,
        delete_status,
        delete_response,
        box_id,
        expected_status,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response(alias_to_id_response)

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        assert dict(request.query) == {
            'partners_ids': alias_to_id_response['id'],
        }
        return web.json_response(places_response, status=places_status)

    @mock_eats_tips_partners('/v1/money-box')
    async def _mock_delete(request: http.Request):
        assert dict(request.query) == {'id': box_id}
        if request.method == 'DELETE':
            return web.json_response(delete_response, status=delete_status)
        return web.json_response(box_response, status=box_status)

    response = await taxi_eats_tips_admin_web.delete(
        '/v1/money-box',
        params={'id': box_id},
        headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    if delete_response:
        content = await response.json()
        assert content == delete_response
