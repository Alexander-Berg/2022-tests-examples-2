from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest

REQUEST_BODY = {
    'display_name': 'новое имя',
    'caption': 'новая подпись',
    'avatar': 'новый аватар',
}


@pytest.mark.parametrize(
    (
        'jwt',
        'alias_to_id_response',
        'places_status',
        'places_response',
        'box_status',
        'box_response',
        'edit_status',
        'edit_response',
        'request_body',
        'expected_status',
    ),
    (
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            200,
            conftest.MONEY_BOX_1,
            200,
            None,
            REQUEST_BODY,
            200,
            id='normal-edit',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_UNCONFIRMED,
            200,
            conftest.MONEY_BOX_1,
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
            200,
            conftest.MONEY_BOX_1,
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
            200,
            conftest.MONEY_BOX_1,
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
            200,
            conftest.MONEY_BOX_1,
            404,
            None,
            REQUEST_BODY,
            404,
            id='partners-error-404',
        ),
        pytest.param(
            *conftest.USER_1,
            200,
            conftest.PLACE_1_USER_1_BOTH,
            200,
            conftest.MONEY_BOX_1,
            400,
            {'code': 'some_code', 'message': 'some message'},
            REQUEST_BODY,
            400,
            id='partners-error-400',
        ),
    ),
)
async def test_money_box_edit(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        web_context,
        jwt,
        alias_to_id_response,
        places_status,
        places_response,
        box_status,
        box_response,
        edit_status,
        edit_response,
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
    async def _mock_edit(request: http.Request):
        assert dict(request.query) == {'id': box_response['id']}
        if request.method == 'PUT':
            assert dict(request.json) == request_body
            return web.json_response(edit_response, status=edit_status)
        return web.json_response(box_response, status=box_status)

    response = await taxi_eats_tips_admin_web.put(
        '/v1/money-box',
        params={'id': box_response['id']},
        json=request_body,
        headers={'X-Chaevie-Token': jwt},
    )

    assert response.status == expected_status
    if edit_response:
        content = await response.json()
        assert content == edit_response
