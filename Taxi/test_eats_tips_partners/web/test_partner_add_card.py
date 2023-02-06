import http

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as http_utils

from test_eats_tips_partners import conftest


@pytest.mark.parametrize(
    ('jwt_token', 'chaevie_response', 'expected_code', 'expected_response'),
    (
        pytest.param(
            conftest.create_jwt(15),
            {'data': {'status': 1}, 'status': 200},
            http.HTTPStatus.OK,
            {},
            id='OK',
        ),
        pytest.param(
            conftest.create_jwt(15),
            {'data': {'status': 0}, 'status': 200},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': 'request to tips failed: status 0',
            },
            id='chaevie-status-0',
        ),
        pytest.param(
            conftest.create_jwt(15),
            {'data': {'error': ['some error']}, 'status': 400},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'bad_request',
                'message': 'request to tips failed: some error',
            },
            id='chaevie-400',
        ),
        pytest.param(
            conftest.create_jwt(14),
            None,
            http.HTTPStatus.CONFLICT,
            {'code': 'conflict', 'message': 'partner already has card'},
            id='already-has-card',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_partner_add_card(
        taxi_eats_tips_partners_web,
        mock_chaevieprosto,
        jwt_token,
        chaevie_response,
        expected_code,
        expected_response,
):
    @mock_chaevieprosto('/api/v2/user/addCardSMS')
    async def _mock_waiter(request: http_utils.Request):
        return web.json_response(**chaevie_response)

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/card', headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    body = await response.json()
    assert response.status == expected_code

    assert body == expected_response
