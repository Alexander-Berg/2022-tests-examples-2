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
        'boxes_status',
        'boxes_response',
        'places',
        'expected_places',
        'expected_status',
        'expected_response',
    ),
    (
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            200,
            {'boxes': [conftest.MONEY_BOX_1]},
            ','.join((conftest.PLACE_1['id'], conftest.PLACE_2['id'])),
            conftest.PLACE_1['id'],
            200,
            {'boxes': [conftest.MONEY_BOX_1_RESPONSE]},
            id='with-wrong-place',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            404,
            None,
            ','.join((conftest.PLACE_1['id'], conftest.PLACE_2['id'])),
            conftest.PLACE_1['id'],
            200,
            {'boxes': []},
            id='partners-404',
        ),
    ),
)
async def test_money_box_list_get(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        web_context,
        jwt,
        alias_to_id_response,
        places_status,
        places_response,
        boxes_status,
        boxes_response,
        places,
        expected_places,
        expected_status,
        expected_response,
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

    @mock_eats_tips_partners('/v1/money-box/list')
    async def _mock_list(request: http.Request):
        assert dict(request.query) == {'places_ids': expected_places}
        return web.json_response(boxes_response, status=boxes_status)

    response = await taxi_eats_tips_admin_web.get(
        '/v1/money-box/list',
        params={'places_ids': places},
        headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    if expected_response:
        content = await response.json()
        assert content == expected_response
