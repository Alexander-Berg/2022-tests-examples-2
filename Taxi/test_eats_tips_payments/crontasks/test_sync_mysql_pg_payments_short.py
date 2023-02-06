import copy
import datetime
import decimal

from aiohttp import web
import pytest

from eats_tips_payments.generated.cron import run_cron
from test_eats_tips_payments import conftest

ALIAS_TO_PARTNER = {'1': conftest.PARTNER_ID_1, '2': conftest.PARTNER_ID_2}

REQUEST_FROM_PG = """
    select
        order_id,
        amount,
        plus_amount,
        order_id_b2p,
        recipient_id,
        recipient_id_b2p,
        is_guest_commission,
        commission,
        guest_amount,
        recipient_amount,
        payment_type,
        status,
        status_b2p,
        review_id,
        updated_at,
        fail_reason,
        card_pan,
        created_at,
        alias
    from eats_tips_payments.orders
    order by order_id_b2p"""

REQUEST_FROM_MYSQL = """
    select
        to_user_id,
        amount,
        amount_trans,
        transaction_id,
        transaction_status,
        transaction_pay_date,
        is_b2p_fail,
        is_apple,
        is_google,
        is_yandex,
        date_created,
        procent,
        type,
        is_best2pay,
        best2pay_fee,
        comment,
        parent_id,
        message,
        email,
        pan,
        transaction_status_date,
        idempotenceKey
    from modx_web_users_pays
    order by transaction_id"""


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.now('1970-01-31 03:04:01')
async def test_sync_mysql_pg_payments_short(
        patch, mock_eats_tips_partners, cron_context,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {
                'id': ALIAS_TO_PARTNER[request.query['alias']],
                'alias': request.query['alias'],
            },
        )

    async with cron_context.pg.master_pool.acquire() as conn:
        pg_initial_rows = list(await conn.fetch(REQUEST_FROM_PG))

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(REQUEST_FROM_MYSQL)
        mysql_initial_rows = list(await cursor.fetchall())

    await run_cron.main(
        [
            'eats_tips_payments.crontasks.sync_mysql_pg_payments_short',
            '-t',
            '0',
        ],
    )

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(
            """
            select id, order_id from modx_web_users_reviews
            where order_id is not null
            """,
        )
        reviews = {row['id'] for row in await cursor.fetchall()}
    assert reviews == {103, 104, 105, 106}

    # test for correct common sync
    async with cron_context.pg.master_pool.acquire() as conn:
        pg_result_rows = list(await conn.fetch(REQUEST_FROM_PG))
    pg_expected_rows = await fill_pg_expected_rows(pg_initial_rows)
    assert [dict(row) for row in pg_result_rows] == pg_expected_rows

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(REQUEST_FROM_MYSQL)
        mysql_rows_result = list(await cursor.fetchall())

    expected_mysql_rows = await fill_expected_mysql_rows(mysql_initial_rows)

    assert mysql_rows_result == expected_mysql_rows

    # test for correct sync after canceled order (amount set to 0)
    async with cron_context.pg.master_pool.acquire() as conn:
        await conn.execute(
            """
            update eats_tips_payments.orders
            set
                amount=0,
                commission=0,
                guest_amount=0,
                recipient_amount=0,
                is_guest_commission=false
            where order_id_b2p = '435'""",
        )

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(
            """
            update modx_web_users_pays
            set
                amount=0,
                amount_trans=0
            where transaction_id=4
            """,
        )

    await run_cron.main(
        [
            'eats_tips_payments.crontasks.sync_mysql_pg_payments_short',
            '-t',
            '0',
        ],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        pg_result_rows = list(await conn.fetch(REQUEST_FROM_PG))

    pg_expected_rows_patched = wipe_amount_pg_rows(
        pg_expected_rows, ['435', '4'],
    )
    assert [dict(row) for row in pg_result_rows] == pg_expected_rows_patched

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(REQUEST_FROM_MYSQL)
        mysql_rows_result = list(await cursor.fetchall())

    expected_mysql_rows_patched = wipe_amount_mysql_rows(
        mysql_rows_result, [435, 4],
    )

    assert mysql_rows_result == expected_mysql_rows_patched


def wipe_amount_mysql_rows(expected_mysql_rows, transaction_ids):
    mysql_expected_rows_patched = []
    for row in expected_mysql_rows:
        new_row = copy.deepcopy(row)
        if new_row['transaction_id'] in transaction_ids:
            new_row['amount'] = 0
            new_row['amount_trans'] = 0
        mysql_expected_rows_patched.append(new_row)
    return mysql_expected_rows_patched


def wipe_amount_pg_rows(pg_expected_rows, transaction_ids):
    pg_expected_rows_patched = []
    for row in pg_expected_rows:
        new_row = copy.deepcopy(row)
        if new_row['order_id_b2p'] in transaction_ids:
            new_row['amount'] = 0
            new_row['commission'] = 0
            new_row['guest_amount'] = 0
            new_row['recipient_amount'] = 0
            new_row['is_guest_commission'] = False
        pg_expected_rows_patched.append(new_row)
    return pg_expected_rows_patched


async def fill_expected_mysql_rows(mysql_initial_rows):
    expected_mysql_rows = copy.deepcopy(mysql_initial_rows)
    mysql_new_rows = [
        {
            'amount': decimal.Decimal('50.00'),
            'amount_trans': decimal.Decimal('0.00'),
            'best2pay_fee': decimal.Decimal('0.00'),
            'comment': '',
            'date_created': 2602980,
            'email': '',
            'idempotenceKey': 'idempotency_token_3',
            'is_apple': 1,
            'is_b2p_fail': 0,
            'is_best2pay': 1,
            'is_google': 0,
            'is_yandex': 0,
            'message': '',
            'pan': '',
            'parent_id': 0,
            'procent': 0,
            'to_user_id': 1,
            'transaction_id': '432',
            'transaction_pay_date': 2602981,
            'transaction_status': 'succeeded',
            'transaction_status_date': 0,
            'type': 0,
        },
        {
            'amount': decimal.Decimal('50.00'),
            'amount_trans': decimal.Decimal('3.00'),
            'best2pay_fee': decimal.Decimal('3.00'),
            'comment': '',
            'date_created': 2602980,
            'email': '',
            'idempotenceKey': 'idempotency_token_4',
            'is_apple': 0,
            'is_b2p_fail': 0,
            'is_best2pay': 1,
            'is_google': 1,
            'is_yandex': 0,
            'message': '',
            'pan': '',
            'parent_id': 0,
            'procent': 0,
            'to_user_id': 1,
            'transaction_id': '433',
            'transaction_pay_date': 2602981,
            'transaction_status': 'succeeded',
            'transaction_status_date': 0,
            'type': 0,
        },
        {
            'amount': decimal.Decimal('50.00'),
            'amount_trans': decimal.Decimal('3.00'),
            'best2pay_fee': decimal.Decimal('3.00'),
            'comment': '',
            'date_created': 2602980,
            'email': '',
            'idempotenceKey': 'idempotency_token_5',
            'is_apple': 0,
            'is_b2p_fail': 0,
            'is_best2pay': 1,
            'is_google': 0,
            'is_yandex': 1,
            'message': '',
            'pan': '',
            'parent_id': 0,
            'procent': 0,
            'to_user_id': 1,
            'transaction_id': '434',
            'transaction_pay_date': 2602981,
            'transaction_status': 'succeeded',
            'transaction_status_date': 0,
            'type': 0,
        },
        {
            'amount': decimal.Decimal('50.00'),
            'amount_trans': decimal.Decimal('3.00'),
            'best2pay_fee': decimal.Decimal('3.00'),
            'comment': '',
            'date_created': 2602980,
            'email': '',
            'idempotenceKey': 'idempotency_token_6',
            'is_apple': 0,
            'is_b2p_fail': 0,
            'is_best2pay': 1,
            'is_google': 0,
            'is_yandex': 0,
            'message': '',
            'pan': '',
            'parent_id': 0,
            'procent': 0,
            'to_user_id': 1,
            'transaction_id': '435',
            'transaction_pay_date': 2602981,
            'transaction_status': 'succeeded',
            'transaction_status_date': 0,
            'type': 0,
        },
    ]
    expected_mysql_rows = (
        expected_mysql_rows[:5] + mysql_new_rows + expected_mysql_rows[5:]
    )
    return expected_mysql_rows


async def fill_pg_expected_rows(pg_initial_rows):
    pg_expected_rows = copy.deepcopy([dict(row) for row in pg_initial_rows])
    pg_expected_rows.pop()  # drop changed row

    new_pg_rows = [
        {
            'alias': '2',
            'amount': 102,
            'card_pan': '',
            'commission': decimal.Decimal('2.75'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 4),
            'fail_reason': '',
            'guest_amount': decimal.Decimal('102.75'),
            'is_guest_commission': False,
            'order_id': 3,
            'order_id_b2p': '3',
            'payment_type': 'google_pay_b2p',
            'plus_amount': 0,
            'recipient_amount': decimal.Decimal('100.00'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4),
        },
        {
            'alias': '2',
            'amount': 105,
            'card_pan': '',
            'commission': decimal.Decimal('2.75'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 4),
            'fail_reason': 'some message',
            'guest_amount': decimal.Decimal('102.75'),
            'is_guest_commission': True,
            'order_id': 5,
            'order_id_b2p': '4',
            'payment_type': 'apple_pay_b2p',
            'plus_amount': 0,
            'recipient_amount': decimal.Decimal('102.75'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4),
        },
        {
            'alias': '2',
            'amount': 105,
            'card_pan': '',
            'commission': decimal.Decimal('2.75'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 4),
            'fail_reason': 'some message',
            'guest_amount': decimal.Decimal('102.75'),
            'is_guest_commission': True,
            'order_id': 6,
            'order_id_b2p': '5',
            'payment_type': 'yandex_pay_b2p',
            'plus_amount': 0,
            'recipient_amount': decimal.Decimal('102.75'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4, 1),
        },
        {
            'alias': '2',
            'amount': 105,
            'card_pan': '',
            'commission': decimal.Decimal('2.75'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 4),
            'fail_reason': 'some message',
            'guest_amount': decimal.Decimal('102.75'),
            'is_guest_commission': True,
            'order_id': 7,
            'order_id_b2p': '6',
            'payment_type': 'yandex_pay_b2p',
            'plus_amount': 0,
            'recipient_amount': decimal.Decimal('102.75'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4, 1),
        },
        {
            'alias': '2',
            'amount': 105,
            'card_pan': 'some pan',
            'commission': decimal.Decimal('2.75'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 4),
            'fail_reason': 'some message',
            'guest_amount': decimal.Decimal('102.75'),
            'is_guest_commission': True,
            'order_id': 8,
            'order_id_b2p': '7',
            'payment_type': 'b2p',
            'plus_amount': 0,
            'recipient_amount': decimal.Decimal('102.75'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4, 2),
        },
        {
            'alias': '2',
            'amount': 0,
            'card_pan': '',
            'commission': decimal.Decimal('0'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 4),
            'fail_reason': 'some message 2',
            'guest_amount': decimal.Decimal('0.00'),
            'is_guest_commission': False,
            'order_id': 9,
            'order_id_b2p': '8',
            'payment_type': 'google_pay_b2p',
            'plus_amount': 0,
            'recipient_amount': decimal.Decimal('0.00'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4),
        },
        # actually, this is changed row with new data - not a new row
        {
            'alias': '2',
            'amount': 105,
            'card_pan': '',
            'commission': decimal.Decimal('2.50'),
            'created_at': datetime.datetime(1970, 1, 31, 0, 3),
            'fail_reason': 'some message 3',
            'guest_amount': decimal.Decimal('102.50'),
            'is_guest_commission': True,
            'order_id': 100,
            'order_id_b2p': '9',
            'payment_type': 'google_pay_b2p',
            'plus_amount': 10,
            'recipient_amount': decimal.Decimal('102.50'),
            'recipient_id': 'f907a11d-e1aa-4b2e-8253-069c58801722',
            'recipient_id_b2p': '2',
            'review_id': None,
            'status': 'COMPLETED',
            'status_b2p': 'COMPLETED',
            'updated_at': datetime.datetime(1970, 1, 31, 0, 4),
        },
    ]

    return new_pg_rows[:2] + pg_expected_rows + new_pg_rows[2:]
