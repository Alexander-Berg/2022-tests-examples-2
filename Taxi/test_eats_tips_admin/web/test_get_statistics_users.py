from aiohttp import web
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


async def test_get_statistics_users(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_eats_tips_payments,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '8'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        return web.json_response(
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
        )

    @mock_eats_tips_partners('/v1/partner/list')
    async def _mock_partner_list(request: http.Request):
        return web.json_response(
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
                                'alias': '8',
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
                                'alias': '9',
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
        )

    @mock_eats_tips_payments('/internal/v1/payments/total/list')
    async def _mock_get_payments_total_list(request: http.Request):
        return web.json_response(
            {
                'payments': [
                    {
                        'recipient_id': conftest.USER_ID_1,
                        'money_total': 100.0,
                        'count': 1,
                    },
                ],
            },
        )

    @mock_eats_tips_payments('/internal/v1/reviews/total/list')
    async def _mock_get_reviews_total_list(request: http.Request):
        return web.json_response(
            {'values': [{'user_id': 8, 'stars': [0, 0, 0, 0, 1]}]},
        )

    response = await taxi_eats_tips_admin_web.get(
        '/v1/statistics/users',
        params={
            'date_from': '2020-01-01 00:00:00',
            'date_to': '2020-01-01 00:00:00',
            'users': ','.join([conftest.USER_ID_1]),
        },
        headers={'X-Chaevie-Token': conftest.JWT_USER_1},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'users_statistics': [
            {
                'user': {
                    'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8',
                    'first_name': 'Иван Иванов',
                },
                'money_total': 100.0,
                'count': 1,
                'positive_rating': 1,
                'negative_rating': 0,
                'positive_rating_percent': 100.0,
                'negative_rating_percent': 0.0,
            },
        ],
        'has_more': False,
    }
