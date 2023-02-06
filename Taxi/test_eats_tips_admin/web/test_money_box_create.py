from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest

REQUEST_BODY = {
    'place_id': conftest.PLACE_1['id'],
    'display_name': 'копилочка 1',
}


@pytest.mark.parametrize(
    (
        'jwt',
        'alias_to_id_response',
        'places_status',
        'places_response',
        'create_status',
        'create_response',
        'request_body',
        'expected_status',
    ),
    (
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            201,
            {'alias': '1', 'box_id': '1'},
            REQUEST_BODY,
            201,
            id='minimal-create',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_UNCONFIRMED,
            '',
            '',
            REQUEST_BODY,
            403,
            id='not-confirmed',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_RECIPIENT,
            '',
            '',
            REQUEST_BODY,
            403,
            id='not-admin',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_2_USER_1_BOTH,
            '',
            '',
            REQUEST_BODY,
            403,
            id='not-related',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            400,
            {'code': 'come_code', 'message': 'some message'},
            REQUEST_BODY,
            400,
            id='partners-error-400',
        ),
    ),
)
async def test_money_box_create(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        web_context,
        jwt,
        alias_to_id_response,
        places_status,
        places_response,
        create_status,
        create_response,
        request_body,
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
    async def _mock_create(request: http.Request):
        assert dict(request.json) == request_body
        return web.json_response(create_response, status=create_status)

    response = await taxi_eats_tips_admin_web.post(
        '/v1/money-box', json=request_body, headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    if create_response:
        content = await response.json()
        assert content == create_response
