import typing

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


def _format_headers(jwt=conftest.JWT_USER_1):
    return {'X-Chaevie-Token': jwt}


def _format_expected_response(amount):
    return {'amount': {'price_value': amount}}


def make_pytest_param(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        request_headers: typing.Any = conftest.SENTINEL,
        expected_status: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(request_headers, _format_headers()),
        conftest.value_or_default(expected_status, 200),
        conftest.value_or_default(
            expected_response, _format_expected_response(amount='300.00'),
        ),
        id=id,
    )


@pytest.mark.parametrize(
    ('request_headers', 'expected_status', 'expected_response'),
    [make_pytest_param(id='success')],
)
async def test_get_transactions(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_best2pay,
        load,
        # params:
        request_headers,
        expected_status,
        expected_response,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '1'})

    @mock_eats_tips_partners('/v1/partner')
    async def _mock_v1_partner(request: http.Request):
        partner_id = request.query['partner_id']
        assert partner_id == conftest.USER_ID_1
        return web.json_response(
            {
                'id': partner_id,
                'b2p_id': 'partner_b2p_id_1',
                'display_name': '',
                'full_name': '',
                'phone_id': 'phone_id_1',
                'saving_up_for': '',
                'best2pay_blocked': False,
                'registration_date': '1970-01-01T03:00:00+03:00',
                'is_vip': False,
                'blocked': False,
            },
            status=200,
        )

    @mock_best2pay('/webapi/b2puser/GetBalance')
    async def _mock_b2p_user_statement(request: http.Request):
        assert request.query['client_ref'] == 'partner_b2p_id_1'
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load('b2p_response.xml'),
        )

    response = await taxi_eats_tips_admin_web.get(
        '/v1/recipient/balance', headers=request_headers,
    )
    assert response.status == expected_status
    assert await response.json() == expected_response
