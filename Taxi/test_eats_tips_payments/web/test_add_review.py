import contextlib
import uuid

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_payments import conftest

ALIAS_TO_PARTNER = {
    '0000010': conftest.PARTNER_ID_1,
    '0000060': conftest.PARTNER_ID_2,
}


@pytest.mark.parametrize(
    (
        'input_data',
        'ext_api_status',
        'ext_api_response',
        'expected_status',
        'expected_result',
        'expected_order_id_mysql',
        'expected_reviews_pg',
    ),
    [
        (
            {'user_id': '000010', 'rating': 5},
            400,
            {'error': ['need some params']},
            400,
            {'code': 'invalid_input', 'message': 'need some params'},
            None,
            [],
        ),
        (
            {'user_id': '000010', 'rating': 5},
            401,
            {'error': ['чет нехватает']},
            401,
            {'code': 'not_authorized', 'message': 'чет нехватает'},
            None,
            [],
        ),
        (
            {
                'user_id': '000010',
                'rating': 5,
                'review': 'comment text',
                'quick_choices': ['quality'],
            },
            200,
            {'id': '1'},
            200,
            {'id': '1'},
            None,
            [
                {
                    'order_id': None,
                    'place_id': None,
                    'quick_choices': ['quality'],
                    'recipient_id': uuid.UUID(conftest.PARTNER_ID_1),
                    'recipient_type': 'partner',
                    'review': 'comment text',
                    'review_id': '1',
                    'star': 5,
                },
            ],
        ),
        (
            # order + review
            {
                'user_id': '000010',
                'rating': 5,
                'review': 'comment text',
                'quick_choices': ['quality'],
                'order_id': '333',
            },
            200,
            {'id': '1'},
            200,
            {'id': '1'},
            333,
            [
                {
                    'order_id': None,
                    'place_id': None,
                    'quick_choices': ['quality'],
                    'recipient_id': uuid.UUID(conftest.PARTNER_ID_1),
                    'recipient_type': 'partner',
                    'review': 'comment text',
                    'review_id': '1',
                    'star': 5,
                },
            ],
        ),
        (
            # order + review with already existing order
            {
                'user_id': '000010',
                'rating': 5,
                'review': 'comment text',
                'quick_choices': ['quality'],
                'order_id': '100500',
            },
            200,
            {'id': '1'},
            200,
            {'id': '1'},
            None,
            [
                {
                    'order_id': None,
                    'place_id': None,
                    'quick_choices': ['quality'],
                    'recipient_id': uuid.UUID(conftest.PARTNER_ID_1),
                    'recipient_type': 'partner',
                    'review': 'comment text',
                    'review_id': '1',
                    'star': 5,
                },
            ],
        ),
        (
            # order + review with already existing order mysql
            {
                'user_id': '000010',
                'recipient_id': conftest.PARTNER_ID_2,
                'place_id': conftest.PLACE_ID_1,
                'rating': 5,
                'review': 'comment text',
                'quick_choices': ['quality'],
                'order_id': 'order000-0000-0000-0000-000000000042',
            },
            200,
            {'id': '42'},
            200,
            {'id': '42'},
            None,
            [
                {
                    'order_id': 'order000-0000-0000-0000-000000000042',
                    'place_id': uuid.UUID(conftest.PLACE_ID_1),
                    'quick_choices': ['quality'],
                    'recipient_id': uuid.UUID(conftest.PARTNER_ID_2),
                    'recipient_type': 'partner',
                    'review': 'comment text',
                    'review_id': '42',
                    'star': 5,
                },
            ],
        ),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_add_review(
        web_context,
        taxi_eats_tips_payments_web,
        mock_chaevieprosto,
        mock_eats_tips_partners,
        mysql,
        input_data,
        ext_api_status,
        ext_api_response,
        expected_status,
        expected_result,
        expected_order_id_mysql,
        expected_reviews_pg,
):
    @mock_chaevieprosto('/dhdghfier.html')
    async def _mock_waiter(request: http.Request):
        assert request.form['action'] == 'add-only-review'
        return web.json_response(ext_api_response, status=ext_api_status)

    @mock_eats_tips_partners('/v1/alias-to-object')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {
                'partner': {
                    'id': ALIAS_TO_PARTNER[request.query['alias']],
                    'display_name': '',
                    'full_name': '',
                    'phone_id': '',
                    'saving_up_for': '',
                    'registration_date': '2020-01-01 00:00:00Z',
                    'is_vip': False,
                    'best2pay_blocked': False,
                },
            },
        )

    async with check_new_reviews(web_context, expected_reviews_pg):
        response = await taxi_eats_tips_payments_web.post(
            '/v1/users/waiters/review', json=input_data,
        )
        assert response.status == expected_status
        content = await response.json()
        assert content == expected_result
        if expected_order_id_mysql:
            with mysql['chaevieprosto'].cursor() as cursor:
                cursor.execute(
                    f"""
                    select order_id
                    from modx_web_users_reviews
                    where id={ext_api_response['id']}
                    """,
                )
                rows = cursor.fetchone()
            assert rows[0] == expected_order_id_mysql


async def _get_reviews_pg(web_context) -> list:
    async with web_context.pg.replica_pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT
              reviews.review_id
              , reviews.recipient_id
              , reviews.recipient_type
              , reviews.place_id
              , reviews.review
              , reviews.star
              , reviews.quick_choices
              , orders_reviews.order_id
            FROM eats_tips_payments.reviews AS reviews
            LEFT JOIN eats_tips_payments.orders_reviews AS orders_reviews
              ON reviews.review_id = orders_reviews.review_id
            ORDER BY review_id
            """,
        )
    return [dict(row) for row in rows]


@contextlib.asynccontextmanager
async def check_new_reviews(context, expected_reviews):
    start_reviews = await _get_reviews_pg(context)
    start_reviews_ids = {review['review_id'] for review in start_reviews}
    yield
    finish_reviews = await _get_reviews_pg(context)
    new_reviews = [
        review
        for review in finish_reviews
        if review['review_id'] not in start_reviews_ids
    ]
    assert new_reviews == expected_reviews


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_idempotency(
        taxi_eats_tips_payments_web,
        mock_chaevieprosto,
        mock_eats_tips_partners,
):
    @mock_chaevieprosto('/dhdghfier.html')
    async def _mock_waiter(request: http.Request):
        assert request.form['action'] == 'add-only-review'
        return web.json_response(
            {'id': str(42 + _mock_waiter.times_called)}, status=200,
        )

    @mock_eats_tips_partners('/v1/alias-to-object')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {
                'partner': {
                    'id': ALIAS_TO_PARTNER[request.query['alias']],
                    'display_name': '',
                    'full_name': '',
                    'phone_id': '',
                    'saving_up_for': '',
                    'registration_date': '2020-01-01 00:00:00Z',
                    'is_vip': False,
                    'best2pay_blocked': False,
                },
            },
        )

    input_data = {
        'user_id': '000010',
        'recipient_id': conftest.PARTNER_ID_2,
        'place_id': conftest.PLACE_ID_1,
        'rating': 5,
        'review': 'comment text',
        'quick_choices': ['quality'],
        'order_id': 'order000-0000-0000-0000-000000000042',
    }
    idempotency_token = 'idempotency_token'

    response = await taxi_eats_tips_payments_web.post(
        '/v1/users/waiters/review',
        headers={'X-Idempotency-Token': idempotency_token},
        json=input_data,
    )
    assert response.status == 200
    first_response = await response.json()

    response = await taxi_eats_tips_payments_web.post(
        '/v1/users/waiters/review',
        headers={'X-Idempotency-Token': idempotency_token},
        json=input_data,
    )
    assert response.status == 200
    assert first_response == await response.json()
