import datetime
import decimal
import uuid

from aiohttp import web
import pytest

from eats_tips_withdrawal.generated.cron import run_cron
from test_eats_tips_withdrawal import conftest

FULLNAME_MAP = {
    'Петр Петрович Пупкин': 'LONG_FULLNAME_ID',
    'test fio': 'SHORT_FULLNAME_ID',
}
PARTNER_IDS_BY_ALIAS = {
    1: '00000000-0000-0000-0000-000000000001',
    2: '00000000-0000-0000-0000-000000000002',
}

ALIAS_TO_PARTNER = {
    '1': conftest.PARTNER_1['id'],
    '2': conftest.PARTNER_2['id'],
}
REQUEST_PAYS_FROM_MYSQL = """
    select
        id,
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
    order by id"""
REQUEST_WITHDRAWALS_FROM_MYSQL = """
    select
        id,
        user_id,
        fullname,
        sum,
        date_time,
        admin_id,
        transaction_date,
        pay_id,
        pay_method,
        cancel_admin_id,
        cancel_date,
        cancel_reason,
        cancel_reason_description,
        idempotency_key
    from modx_web_users_withdrawal
    order by idempotency_key, id"""
REQUEST_WITHDRAWALS_FROM_PG = """
    select
        id,
        partner_id,
        b2p_user_id,
        bp2_order_id,
        bp2_order_reference,
        fullname_id,
        amount,
        fee,
        create_date,
        finish_date,
        admin,
        last_update,
        withdrawal_method,
        comment,
        b2p_description,
        status,
        card_pan,
        legacy,
        idempotency_key
    from eats_tips_withdrawal.withdrawals
    order by id"""

NEW_PG_WITHDRAWALS = [
    {
        'id': 22,
        'partner_id': uuid.UUID('00000000-0000-0000-0000-000000000001'),
        'b2p_user_id': '1',
        'bp2_order_id': 'None',
        'bp2_order_reference': '41',
        'fullname_id': 'SHORT_FULLNAME_ID',
        'amount': decimal.Decimal('0.00'),
        'fee': decimal.Decimal('0.00'),
        'create_date': datetime.datetime(
            2021, 6, 22, 16, 10, 25, tzinfo=datetime.timezone.utc,
        ),
        'finish_date': datetime.datetime(
            2021, 6, 22, 16, 10, 26, tzinfo=datetime.timezone.utc,
        ),
        'admin': '1',
        'last_update': datetime.datetime(
            2021, 6, 22, 16, 10, 26, tzinfo=datetime.timezone.utc,
        ),
        'withdrawal_method': 'best2pay',
        'comment': 'why not',
        'b2p_description': 'b2p message',
        'status': 'manual rejected',
        'card_pan': '',
        'legacy': True,
    },
    {
        'id': 23,
        'partner_id': uuid.UUID('00000000-0000-0000-0000-000000000001'),
        'b2p_user_id': '1',
        'bp2_order_id': '2',
        'bp2_order_reference': '50',
        'fullname_id': 'SHORT_FULLNAME_ID',
        'amount': decimal.Decimal('21.00'),
        'fee': decimal.Decimal('0.00'),
        'create_date': datetime.datetime(
            2021, 6, 22, 16, 10, 25, tzinfo=datetime.timezone.utc,
        ),
        'finish_date': datetime.datetime(
            2021, 6, 22, 16, 10, 26, tzinfo=datetime.timezone.utc,
        ),
        'admin': '-1',
        'last_update': datetime.datetime(
            2021, 6, 22, 16, 10, 26, tzinfo=datetime.timezone.utc,
        ),
        'withdrawal_method': 'best2pay',
        'comment': '',
        'b2p_description': '',
        'status': 'success',
        'card_pan': '',
        'legacy': True,
    },
]

NEW_MYSQL_WITHDRAWALS = [
    {
        'admin_id': 0,
        'cancel_admin_id': 1,
        'cancel_date': 1624378226,
        'cancel_reason': '',
        'cancel_reason_description': '',
        'date_time': 1624378225,
        'fullname': 'test fio',
        'id': 27,
        'idempotency_key': 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6',
        'pay_id': 57,
        'pay_method': 'best2pay',
        'sum': 21,
        'transaction_date': 0,
        'user_id': 1,
    },
    {
        'admin_id': -1,
        'cancel_admin_id': 0,
        'cancel_date': 0,
        'cancel_reason': '',
        'cancel_reason_description': '',
        'date_time': 1624378225,
        'fullname': 'test fio',
        'id': 28,
        'idempotency_key': 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7',
        'pay_id': 58,
        'pay_method': 'best2pay',
        'sum': 21,
        'transaction_date': 1624378226,
        'user_id': 1,
    },
]

NEW_MYSQL_PAYS = [
    {
        'amount': decimal.Decimal('0'),
        'amount_trans': decimal.Decimal('0.00'),
        'best2pay_fee': decimal.Decimal('0.00'),
        'comment': '',
        'date_created': 1624378225,
        'email': '',
        'id': 57,
        'idempotenceKey': 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6',
        'is_apple': 0,
        'is_b2p_fail': 0,
        'is_best2pay': 1,
        'is_google': 0,
        'is_yandex': 0,
        'message': '',
        'pan': '',
        'parent_id': 0,
        'procent': 5,
        'to_user_id': 1,
        'transaction_id': '26',
        'transaction_pay_date': 1624378226,
        'transaction_status': 'succeeded',
        'transaction_status_date': 0,
        'type': 1,
    },
    {
        'amount': -(decimal.Decimal('21.00')),
        'amount_trans': decimal.Decimal('0.00'),
        'best2pay_fee': decimal.Decimal('0.00'),
        'comment': '',
        'date_created': 1624378225,
        'email': '',
        'id': 58,
        'idempotenceKey': 'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7',
        'is_apple': 0,
        'is_b2p_fail': 0,
        'is_best2pay': 1,
        'is_google': 0,
        'is_yandex': 0,
        'message': '',
        'pan': 'some_pan',
        'parent_id': 0,
        'procent': 5,
        'to_user_id': 1,
        'transaction_id': '27',
        'transaction_pay_date': 1624378226,
        'transaction_status': 'succeeded',
        'transaction_status_date': 0,
        'type': 1,
    },
    {
        'amount': decimal.Decimal('0'),
        'amount_trans': decimal.Decimal('0.00'),
        'best2pay_fee': decimal.Decimal('0.00'),
        'comment': 'Комиссия за вывод средств',
        'date_created': 1624378225,
        'email': '',
        'id': 59,
        'idempotenceKey': '',
        'is_apple': 0,
        'is_b2p_fail': 0,
        'is_best2pay': 1,
        'is_google': 0,
        'is_yandex': 0,
        'message': '',
        'pan': '',
        'parent_id': 57,
        'procent': 2,
        'to_user_id': 1,
        'transaction_id': None,
        'transaction_pay_date': 1624378226,
        'transaction_status': 'succeeded',
        'transaction_status_date': 0,
        'type': 1,
    },
    {
        'amount': -(decimal.Decimal('20.00')),
        'amount_trans': decimal.Decimal('0.00'),
        'best2pay_fee': decimal.Decimal('0.00'),
        'comment': 'Комиссия за вывод средств',
        'date_created': 1624378225,
        'email': '',
        'id': 60,
        'idempotenceKey': '',
        'is_apple': 0,
        'is_b2p_fail': 0,
        'is_best2pay': 1,
        'is_google': 0,
        'is_yandex': 0,
        'message': '',
        'pan': '',
        'parent_id': 58,
        'procent': 2,
        'to_user_id': 1,
        'transaction_id': None,
        'transaction_pay_date': 1624378226,
        'transaction_status': 'succeeded',
        'transaction_status_date': 0,
        'type': 1,
    },
]


@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.now('2021-06-22 19:10:28')
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-withdrawal', 'dst': 'personal'}],
)
async def test_sync_dbs_requests_short(
        pgsql, mysql, mock_eats_tips_partners, mockserver, cron_context,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {
                'id': ALIAS_TO_PARTNER[request.query['alias']],
                'alias': request.query['alias'],
            },
        )

    @mockserver.json_handler('/personal/v1/identifications/store')
    def _mock_identifications_store(request):
        return {
            'value': request.json['value'],
            'id': FULLNAME_MAP[request.json['value']],
        }

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_identifications_retrieve(request):
        fullname = ''
        for fullname, fullname_id in FULLNAME_MAP.items():
            if fullname_id == request.json['id']:
                break
        return {'value': fullname, 'id': request.json['id']}

    async with cron_context.pg.master_pool.acquire() as conn:
        pg_initial_rows = list(await conn.fetch(REQUEST_WITHDRAWALS_FROM_PG))

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(REQUEST_PAYS_FROM_MYSQL)
        mysql_pays_initial_rows = list(await cursor.fetchall())

        await cursor.execute(REQUEST_WITHDRAWALS_FROM_MYSQL)
        mysql_withdrawal_initial_rows = list(await cursor.fetchall())

    await run_cron.main(
        ['eats_tips_withdrawal.crontasks.sync_dbs_requests_short', '-t', '0'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        pg_result_rows = list(await conn.fetch(REQUEST_WITHDRAWALS_FROM_PG))
        for i in [-2, -1]:
            pg_result_rows[i] = dict(pg_result_rows[i])
            pg_result_rows[i].pop('idempotency_key')

    async with cron_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(REQUEST_PAYS_FROM_MYSQL)
        mysql_pays_result_rows = list(await cursor.fetchall())

        await cursor.execute(REQUEST_WITHDRAWALS_FROM_MYSQL)
        mysql_withdrawal_result_rows = list(await cursor.fetchall())

    assert pg_initial_rows + NEW_PG_WITHDRAWALS == pg_result_rows
    assert (
        mysql_withdrawal_initial_rows + NEW_MYSQL_WITHDRAWALS
        == mysql_withdrawal_result_rows
    )
    assert mysql_pays_initial_rows + NEW_MYSQL_PAYS == mysql_pays_result_rows
