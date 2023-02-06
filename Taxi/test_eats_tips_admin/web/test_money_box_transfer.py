from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest

USER_ID_1 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a8'
USER_ID_2 = '2590d5f8-bbc7-416b-ad11-99d1f2ace132'
PLACE_1 = {'id': 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e', 'title': 'заведение'}


@pytest.mark.parametrize(
    (
        'jwt',
        'body',
        'ext_result_partners_id',
        'ext_status_money_box',
        'ext_result_money_box',
        'ext_status_balance',
        'ext_result_balance',
        'ext_status_transfer',
        'ext_result_transfer',
        'expected_status',
        'expected_result',
    ),
    [
        pytest.param(
            conftest.JWT_USER_1,
            {
                'box_id': '00000000-0000-0000-0000-000000000001',
                'receivers': [{'partner_id': USER_ID_1, 'amount': '150'}],
            },
            {'id': USER_ID_1, 'alias': '1'},
            200,
            conftest.MONEY_BOX_1,
            200,
            {'balance': '250'},
            200,
            None,
            200,
            {'balance': {'price_value': '666'}},
            id='success',
        ),
    ],
)
async def test_money_box_transfer(
        taxi_eats_tips_admin_web,
        mock_eats_tips_payments,
        mock_eats_tips_partners,
        jwt,
        body,
        ext_result_partners_id,
        ext_status_money_box,
        ext_result_money_box,
        ext_status_balance,
        ext_result_balance,
        ext_status_transfer,
        ext_result_transfer,
        expected_status,
        expected_result,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response(ext_result_partners_id)

    @mock_eats_tips_partners('/v1/partner/list')
    async def _mock_partner_list(request: http.Request):
        assert dict(request.query) == {'places_ids': PLACE_1['id']}
        return web.json_response(
            {
                'has_more': False,
                'partners': [
                    {
                        'info': {
                            'id': USER_ID_1,
                            'display_name': '',
                            'full_name': 'Иван Иванов',
                            'b2p_id': '9',
                            'saving_up_for': '',
                            'phone_id': '',
                            'mysql_id': '8',
                            'registration_date': '2020-12-12T03:00:00+03:00',
                            'is_vip': False,
                            'best2pay_blocked': False,
                            'address': '',
                        },
                        'places': [
                            {
                                'alias': '8',
                                'place_id': PLACE_1['id'],
                                'confirmed': True,
                                'show_in_menu': False,
                                'address': '',
                                'title': '',
                                'roles': ['admin', 'recipient'],
                            },
                        ],
                    },
                    {
                        'info': {
                            'id': USER_ID_2,
                            'display_name': '',
                            'full_name': 'Петр Петров',
                            'b2p_id': '9',
                            'saving_up_for': '',
                            'phone_id': '',
                            'mysql_id': '9',
                            'registration_date': '2020-12-12T03:00:00+03:00',
                            'is_vip': False,
                            'best2pay_blocked': False,
                        },
                        'places': [
                            {
                                'alias': '9',
                                'place_id': PLACE_1['id'],
                                'confirmed': True,
                                'show_in_menu': False,
                                'address': '',
                                'title': '',
                                'roles': ['recipient'],
                            },
                        ],
                    },
                ],
            },
        )

    @mock_eats_tips_partners('/v1/money-box')
    async def _mock_box(request: http.Request):
        return web.json_response(
            ext_result_money_box, status=ext_status_money_box,
        )

    @mock_eats_tips_payments('/internal/v1/money-box/balance')
    async def _mock_balance(request: http.Request):
        return web.json_response(ext_result_balance, status=ext_status_balance)

    @mock_eats_tips_payments('/internal/v1/money-box/transfer')
    async def _mock_transfer(request: http.Request):
        return web.json_response(
            ext_result_transfer, status=ext_status_transfer,
        )

    response = await taxi_eats_tips_admin_web.post(
        '/v1/money-box/transfer',
        json=body,
        headers={'X-Chaevie-Token': jwt, 'X-Idempotency-Token': '42'},
    )
    assert response.status == expected_status
    if expected_result:
        content = await response.json()
        assert content == expected_result
