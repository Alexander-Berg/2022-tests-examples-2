from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest

USER_ID_1 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a8'
USER_ID_2 = '2590d5f8-bbc7-416b-ad11-99d1f2ace132'

PLACE_1 = {
    'id': 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e',
    'title': 'заведение',
    'address': '',
}

TRANSACTION_1 = {
    'datetime': '2021-01-27T16:45:00+03:00',
    'amount': '100',
    'direction': 'outgoing',
    'partner': USER_ID_1,
    'status': 'success',
}
TRANSACTION_1_WITH_USER: dict = TRANSACTION_1.copy()
TRANSACTION_1_WITH_USER['recipient'] = {
    'id': TRANSACTION_1_WITH_USER.pop('partner'),
    'first_name': 'Иван Иванов',
}
TRANSACTION_2 = {
    'datetime': '2021-01-27T16:35:00+03:00',
    'amount': '150',
    'direction': 'incoming',
    'status': 'success',
}
TRANSACTION_2_WITH_USER = TRANSACTION_2.copy()
TRANSACTION_3 = {
    'datetime': '2021-01-27T16:30:00+03:00',
    'amount': '100',
    'direction': 'outgoing',
    'partner': USER_ID_2,
    'status': 'in-progress',
}
TRANSACTION_3_WITH_USER: dict = TRANSACTION_3.copy()
TRANSACTION_3_WITH_USER['recipient'] = {
    'id': TRANSACTION_3_WITH_USER.pop('partner'),
    'first_name': 'Петр Петров',
}

AGGREGATE_1 = {'date': '2022-01-27', 'money_total': '50'}


@pytest.mark.parametrize(
    (
        'jwt',
        'params',
        'ext_result_partners_id',
        'ext_status_money_box',
        'ext_result_money_box',
        'ext_status_transactions',
        'ext_result_transactions',
        'ext_status_aggregate',
        'ext_result_aggregate',
        'expected_status',
        'expected_result',
    ),
    [
        (
            conftest.JWT_USER_1,
            {
                'tz': '+4:30',
                'id': conftest.MONEY_BOX_1['id'],
                'date_to': AGGREGATE_1['date'],
            },
            {'id': USER_ID_1, 'alias': '1'},
            200,
            conftest.MONEY_BOX_1,
            200,
            {'transactions': [TRANSACTION_1, TRANSACTION_2, TRANSACTION_3]},
            200,
            {'aggregate': [AGGREGATE_1]},
            200,
            {
                'transactions': [
                    TRANSACTION_1_WITH_USER,
                    TRANSACTION_2_WITH_USER,
                    TRANSACTION_3_WITH_USER,
                ],
                'aggregate': [AGGREGATE_1],
                'has_more': False,
            },
        ),
    ],
)
async def test_get_transactions(
        taxi_eats_tips_admin_web,
        mock_eats_tips_payments,
        mock_eats_tips_partners,
        jwt,
        params,
        ext_result_partners_id,
        ext_status_money_box,
        ext_result_money_box,
        ext_status_transactions,
        ext_result_transactions,
        ext_status_aggregate,
        ext_result_aggregate,
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
        return web.json_response(
            {
                'places': [
                    {
                        'info': PLACE_1,
                        'partners': [
                            {
                                'partner_id': ext_result_partners_id['id'],
                                'roles': ['admin', 'recipient'],
                                'show_in_menu': False,
                                'confirmed': True,
                            },
                        ],
                    },
                ],
            },
        )

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
                            'saving_up_for': '',
                            'phone_id': '',
                            'mysql_id': '8',
                            'registration_date': '2020-12-12T03:00:00+03:00',
                            'is_vip': False,
                            'best2pay_blocked': False,
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
    async def _mock_money_box(request: http.Request):
        return web.json_response(
            ext_result_money_box, status=ext_status_money_box,
        )

    @mock_eats_tips_payments('/internal/v1/money-box/transactions')
    async def _mock_transactions(request: http.Request):
        return web.json_response(
            ext_result_transactions, status=ext_status_transactions,
        )

    @mock_eats_tips_payments('/internal/v1/money-box/transactions/total')
    async def _mock_total(request: http.Request):
        return web.json_response(
            ext_result_aggregate, status=ext_status_aggregate,
        )

    response = await taxi_eats_tips_admin_web.get(
        '/v1/money-box/transactions',
        params=params,
        headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
