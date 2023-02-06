from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest

USER_ID_1 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a8'
USER_ID_2 = '2590d5f8-bbc7-416b-ad11-99d1f2ace132'

PLACE_1 = {'id': 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e', 'title': 'заведение'}

TRANSACTION_1 = {
    'user_id': 8,
    'datetime': '2021-09-16T18:53:04+03:00',
    'rating': 3,
    'review': 'отзыв о пользователе 4 со частью быстрых ответов',
    'quick_choices': [
        'Сервис',
        'Чистота',
        'Атмосфера',
        'Вкусная еда и напитки',
    ],
}
TRANSACTION_1_WITH_USER = TRANSACTION_1.copy()
TRANSACTION_1_WITH_USER.pop('user_id')
TRANSACTION_1_WITH_USER['user'] = {
    'id': USER_ID_1,
    'recipient_type': 'partner',
    'first_name': 'Иван Иванов',
}
TRANSACTION_2 = {
    'user_id': 8,
    'datetime': '2021-09-16T18:53:03+03:00',
    'rating': 5,
    'review': 'отзыв о пользователе 4 со всеми быстрыми ответами',
    'quick_choices': [
        'Сервис',
        'Еда и качество напитков',
        'Чистота',
        'Атмосфера',
        'Скорость обслуживания',
        'Прекрасная атмосфера',
        'Вкусная еда и напитки',
        'Душевный сервис',
        'Быстрое обслуживание',
        'Мастер - золотые руки',
    ],
}
TRANSACTION_2_WITH_USER = TRANSACTION_2.copy()
TRANSACTION_2_WITH_USER.pop('user_id')
TRANSACTION_2_WITH_USER['user'] = {
    'id': USER_ID_1,
    'recipient_type': 'partner',
    'first_name': 'Иван Иванов',
}
TRANSACTION_3 = {
    'user_id': 9,
    'amount': 4000.0,
    'datetime': '2021-09-15T10:01:40+03:00',
    'quick_choices': [],
}
TRANSACTION_3_WITH_USER = TRANSACTION_3.copy()
TRANSACTION_3_WITH_USER.pop('user_id')
TRANSACTION_3_WITH_USER['user'] = {
    'id': USER_ID_2,
    'recipient_type': 'partner',
    'first_name': 'Петр Петров',
}
TRANSACTION_4 = {
    'user_id': 9,
    'amount': 42.0,
    'datetime': '1970-01-01T03:01:40+03:00',
    'quick_choices': [],
}

AGGREGATE_1 = {'date': '2021-09-16', 'count': 2, 'money_total': 0}
AGGREGATE_2 = {'date': '2021-09-15', 'count': 1, 'money_total': 4000.0}


@pytest.mark.parametrize(
    (
        'jwt',
        'params',
        'users_aliases',
        'ext_result_partners_id',
        'ext_status_transactions',
        'ext_result_transactions',
        'ext_status_aggregate',
        'ext_result_aggregate',
        'expected_date_to_param',
        'expected_date_from_param',
        'expected_limit_param',
        'expected_status',
        'expected_result',
    ),
    [
        (
            conftest.JWT_USER_1,
            {
                'tz': '+04:30',
                'aggregate': 'date',
                'users': f'{USER_ID_1},{USER_ID_2}',
                'date_to': '2021-11-16T00:00:00+03:00',
                'limit': '3',
            },
            '8,9',
            {'id': USER_ID_1, 'alias': '1'},
            200,
            {
                'transactions': [
                    TRANSACTION_1,
                    TRANSACTION_2,
                    TRANSACTION_3,
                    TRANSACTION_4,
                ],
            },
            200,
            {'aggregate': [AGGREGATE_1, AGGREGATE_2]},
            '2021-09-17T18:53:04+03:00',
            '2021-09-14T10:01:40+03:00',
            '4',
            200,
            {
                'transactions': [
                    TRANSACTION_1_WITH_USER,
                    TRANSACTION_2_WITH_USER,
                    TRANSACTION_3_WITH_USER,
                ],
                'aggregate': [AGGREGATE_1, AGGREGATE_2],
                'has_more': True,
            },
        ),
        (
            conftest.JWT_USER_1,
            {
                'tz': '+04:30',
                'aggregate': 'date',
                'users': f'{USER_ID_1},{USER_ID_2}',
                'date_to': '2021-11-16T00:00:00+03:00',
            },
            '8,9',
            {'id': USER_ID_1, 'alias': '1'},
            200,
            {'transactions': [TRANSACTION_1]},
            200,
            {'aggregate': [AGGREGATE_1]},
            '2021-09-17T18:53:04+03:00',
            '2021-09-15T18:53:04+03:00',
            '21',
            200,
            {
                'transactions': [TRANSACTION_1_WITH_USER],
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
        users_aliases,
        ext_result_partners_id,
        ext_status_transactions,
        ext_result_transactions,
        ext_status_aggregate,
        ext_result_aggregate,
        expected_date_to_param,
        expected_date_from_param,
        expected_limit_param,
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
                                'roles': ['admin'],
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
                                'roles': ['admin', 'recipient'],
                                'address': '',
                                'title': '',
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
                                'roles': ['recipient'],
                                'address': '',
                                'title': '',
                            },
                        ],
                    },
                ],
            },
        )

    @mock_eats_tips_payments('/internal/v1/payments')
    async def _mock_transactions(request: http.Request):
        assert dict(request.query) == {
            'users': users_aliases,
            'date_to': params['date_to'],
            'limit': expected_limit_param,
            'offset': '0',
        }
        return web.json_response(
            ext_result_transactions, status=ext_status_transactions,
        )

    @mock_eats_tips_payments('/internal/v1/payments/total/by-dates')
    async def _mock_aggregate(request: http.Request):
        assert dict(request.query) == {
            'users': users_aliases,
            'date_from': expected_date_from_param,
            'date_to': expected_date_to_param,
            'tz': params['tz'],
        }
        return web.json_response(
            ext_result_aggregate, status=ext_status_aggregate,
        )

    response = await taxi_eats_tips_admin_web.get(
        '/v1/transactions', params=params, headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result


@pytest.mark.parametrize(
    (
        'params',
        'response_payments_and_reviews',
        'response_payments_and_reviews_total_by_dates',
        'expected_status',
        'expected_result',
    ),
    [
        pytest.param(
            {
                'tz': '+04:30',
                'aggregate': 'date',
                'users': f'{USER_ID_1},{USER_ID_2}',
                'date_to': '2021-10-11T00:00:00+03:00',
                'limit': '3',
            },
            {'data': {'transactions': []}, 'status': 200},
            {'data': {'aggregate': []}, 'status': 200},
            200,
            {'aggregate': [], 'has_more': False, 'transactions': []},
            id='void_response',
        ),
        pytest.param(
            {
                'tz': '+4:30',
                'aggregate': 'date',
                'users': f'{USER_ID_1},{USER_ID_2}',
                'date_to': '2021-11-16T00:00:00+03:00',
                'limit': '3',
            },
            {
                'data': {
                    'transactions': [
                        {
                            'recipient_id': USER_ID_1,
                            'recipient_type': 'partner',
                            'datetime': '2021-10-10T09:00:00+03:00',
                            'place_id': PLACE_1['id'],
                            'amount': 100.0,
                            'rating': 5,
                            'review': 'Text review',
                            'quick_choices': [],
                        },
                        {
                            'recipient_id': USER_ID_1,
                            'recipient_type': 'partner',
                            'datetime': '2021-10-10T08:00:00+03:00',
                            'place_id': PLACE_1['id'],
                            'amount': 100.0,
                        },
                        {
                            'recipient_id': USER_ID_2,
                            'recipient_type': 'partner',
                            'datetime': '2021-10-10T07:30:00+03:00',
                            'place_id': PLACE_1['id'],
                            'rating': 4,
                            'review': 'Text review',
                            'quick_choices': ['Сервис'],
                        },
                    ],
                },
                'status': 200,
            },
            {
                'data': {
                    'aggregate': [
                        {
                            'date_from': '2021-10-10',
                            'date_to': '2021-10-10',
                            'total_count': 3,
                            'reviews_count': 2,
                            'payments_count': 2,
                            'payments_sum': 200.0,
                        },
                    ],
                },
                'status': 200,
            },
            200,
            {
                'transactions': [
                    {
                        'user': {
                            'id': USER_ID_1,
                            'recipient_type': 'partner',
                            'first_name': 'Иван Иванов',
                        },
                        'datetime': '2021-10-10T09:00:00+03:00',
                        'amount': 100.0,
                        'rating': 5,
                        'review': 'Text review',
                        'quick_choices': [],
                    },
                    {
                        'user': {
                            'id': USER_ID_1,
                            'recipient_type': 'partner',
                            'first_name': 'Иван Иванов',
                        },
                        'datetime': '2021-10-10T08:00:00+03:00',
                        'amount': 100.0,
                    },
                    {
                        'user': {
                            'id': USER_ID_2,
                            'recipient_type': 'partner',
                            'first_name': 'Петр Петров',
                        },
                        'datetime': '2021-10-10T07:30:00+03:00',
                        'rating': 4,
                        'review': 'Text review',
                        'quick_choices': ['Сервис'],
                    },
                ],
                'aggregate': [
                    {'date': '2021-10-10', 'money_total': 200.0, 'count': 3},
                ],
                'has_more': False,
            },
            id='ok',
        ),
    ],
)
@pytest.mark.config(EATS_TIPS_ADMIN_TRANSACTIONS_DATA_SOURCE='pg')
async def test_get_transactions_pg(
        taxi_eats_tips_admin_web,
        mock_eats_tips_payments,
        mock_eats_tips_partners,
        params,
        response_payments_and_reviews,
        response_payments_and_reviews_total_by_dates,
        expected_status,
        expected_result,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        assert dict(request.query) == {'alias': '1'}
        return web.json_response({'id': USER_ID_1, 'alias': '1'})

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_place_list(request: http.Request):
        assert dict(request.query) == {'partners_ids': USER_ID_1}
        return web.json_response(
            {
                'places': [
                    {
                        'info': PLACE_1,
                        'partners': [
                            {
                                'partner_id': USER_ID_1,
                                'roles': ['admin'],
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
                                'roles': ['admin', 'recipient'],
                                'address': '',
                                'title': '',
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
                                'roles': ['recipient'],
                                'address': '',
                                'title': '',
                            },
                        ],
                    },
                ],
            },
        )

    @mock_eats_tips_partners('/v1/money-box/list')
    def _mock_v1_money_box_list(request: http.Request):
        return {'boxes': []}

    @mock_eats_tips_payments('/internal/v1/payments-and-reviews')
    async def _mock_transactions(request: http.Request):
        return web.json_response(**response_payments_and_reviews)

    @mock_eats_tips_payments(
        '/internal/v1/payments-and-reviews/total/by-dates',
    )
    async def _mock_aggregate(request: http.Request):
        return web.json_response(
            **response_payments_and_reviews_total_by_dates,
        )

    response = await taxi_eats_tips_admin_web.get(
        '/v1/transactions',
        params=params,
        headers={'X-Chaevie-Token': conftest.JWT_USER_1},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
