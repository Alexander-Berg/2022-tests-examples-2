import decimal

from aiohttp import web
import pytest

from eats_tips_withdrawal.common import models
from eats_tips_withdrawal.common import withdrawal as withdrawal_lib
from eats_tips_withdrawal.common import withdrawal_sbp
from test_eats_tips_withdrawal import conftest


PHONE_MAP = {'71122334455': 'SHORT_PHONE_ID', '79110000000': 'LONG_PHONE_ID'}
FULLNAME_MAP = {
    'Петр Петрович Пупкин': 'LONG_FULLNAME_ID',
    'test fio': 'SHORT_FULLNAME_ID',
}
PARTNER_IDS_BY_ALIAS = {
    1: '00000000-0000-0000-0000-000000000001',
    2: '00000000-0000-0000-0000-000000000002',
}
NEW_REQUEST = (
    1,
    conftest.JWT_USER_1,
    '71122334455',
    '100000000001',
    decimal.Decimal('10.01'),
    'e357cc5ad1764033be158b32d3ea96bf',
    """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <PayOutSBPPrecheck>
                <order_id>123456</order_id>
                <precheck_id>1234567</precheck_id>
                <pam>Петр Петрович Пупкин</pam>
            <signature>ZDg2M2NmMWNjNTRlYzI0MzNjZWJiZWY2NWNlNDg4MGE=</signature>
            </PayOutSBPPrecheck>""",
    'ZThmNzkzN2I5YjY3NGNkMGY3ZTVlYzZlMGRhM2VmYjI=',
    200,
    {
        'unique_precheck_key': 'e357cc5ad1764033be158b32d3ea96bf',
        'receiver_full_name': 'Петр Петрович Пупкин',
    },
    1,
    1,
    '123456',
    1234567,
    'Петр Петрович Пупкин',
)
EXISTED_REQUEST = (
    2,
    conftest.JWT_USER_2,
    '79110000000',
    '100000000001',
    decimal.Decimal('10.01'),
    'D12345YyYWUwODk4ZDYwMTNiYTYwNzlh',
    """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <PayOutSBPPrecheck>
                <order_id>25</order_id>
                <precheck_id>22</precheck_id>
                <pam>test fio</pam>
            <signature>ZDg2M2NmMWNjNTRlYzI0MzNjZWJiZWY2NWNlNDg4MGE=</signature>
            </PayOutSBPPrecheck>""",
    'dont_check_here',
    200,
    {
        'unique_precheck_key': 'D12345YyYWUwODk4ZDYwMTNiYTYwNzlh',
        'receiver_full_name': 'test fio',
    },
    0,
    0,
    25,
    22,
    'test fio',
)


@pytest.mark.parametrize(
    'client_id, jwt, phone, bank_id, amount, idempotency_token,b2p_answer, '
    'expected_signature, expected_status, expected_result, '
    'expected_new_pay_row_count, expected_new_withdrawal_row_count, '
    'expected_order_id, expected_precheck_id, expected_fullname, use_pg',
    [
        pytest.param(
            *NEW_REQUEST,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg new request',
        ),
        pytest.param(
            *EXISTED_REQUEST,
            True,
            marks=conftest.get_db_usage_exp(2, True),
            id='pg existed request',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 1}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 2}],
    value={'enabled': True},
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-withdrawal', 'dst': 'personal'}],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
@pytest.mark.now('2021-05-04T12:12:44.477345+03:00')
async def test_sbp_create_precheck(
        mock_best2pay,
        mock_eats_tips_partners,
        web_context,
        taxi_eats_tips_withdrawal_web,
        mockserver,
        mysql,
        client_id,
        jwt,
        phone,
        bank_id,
        amount,
        idempotency_token,
        b2p_answer,
        expected_signature,
        expected_status,
        expected_result,
        expected_new_pay_row_count,
        expected_new_withdrawal_row_count,
        expected_order_id,
        expected_precheck_id,
        expected_fullname,
        use_pg,
):
    await make_precheck_mocks(
        mock_best2pay,
        mock_eats_tips_partners,
        mockserver,
        expected_signature,
        b2p_answer,
        expected_fullname,
        phone,
        client_id,
    )

    old_count_withdrawal_rows = await get_old_counts(use_pg, web_context)

    response = await taxi_eats_tips_withdrawal_web.post(
        '/v1/withdrawal/sbp/create-precheck',
        params={'phone': phone, 'bank_id': bank_id, 'amount': amount},
        headers={
            'X-Idempotency-Token': idempotency_token,
            'X-Chaevie-Token': jwt,
        },
    )

    content = await response.json()
    assert content == expected_result
    assert response.status == expected_status
    if use_pg:
        async with web_context.pg.master_pool.acquire() as conn:
            withdrawal_rows = await conn.fetch(
                'select * from eats_tips_withdrawal.withdrawals',
            )
        assert (
            len(withdrawal_rows) - old_count_withdrawal_rows
        ) == expected_new_withdrawal_row_count
        if not expected_new_withdrawal_row_count:
            return
        new_withdrawal_row = {}
        for row in withdrawal_rows:
            if row['idempotency_key'] == idempotency_token:
                new_withdrawal_row = row
                break
        else:
            assert not 'new row'
        assert new_withdrawal_row['amount'] == decimal.Decimal(amount)
        assert new_withdrawal_row['precheck_id'] == expected_precheck_id
        assert new_withdrawal_row['bank_id'] == bank_id
        assert new_withdrawal_row['b2p_user_id'] == str(client_id)
        assert new_withdrawal_row['bp2_order_id'] == str(expected_order_id)
        assert (
            new_withdrawal_row['bp2_order_reference']
            == withdrawal_lib.WITHDRAWAL_REFERENCE_PREFIX + idempotency_token
        )
        assert (
            new_withdrawal_row['withdrawal_method']
            == withdrawal_sbp.PAY_METHOD
        )
        assert new_withdrawal_row['target_phone_id'] == PHONE_MAP[phone]
        assert (
            new_withdrawal_row['fullname_id']
            == FULLNAME_MAP[expected_fullname]
        )
        assert (
            new_withdrawal_row['status']
            == models.WithdrawalRequestStatus.PRECHECK.value
        )
        return


async def get_old_counts(use_pg, web_context):
    async with web_context.pg.master_pool.acquire() as conn:
        old_count_withdrawal_rows = await conn.fetchval(
            'select count(id) from eats_tips_withdrawal.withdrawals',
        )
    return old_count_withdrawal_rows


async def make_precheck_mocks(
        mock_best2pay,
        mock_eats_tips_partners,
        mockserver,
        expected_signature,
        b2p_answer,
        expected_fullname,
        phone,
        client_id,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': PARTNER_IDS_BY_ALIAS[client_id], 'alias': str(client_id)},
        )

    @mock_best2pay('/webapi/b2puser/PayOutSBPPrecheck')
    async def _mock_sbp_create_precheck(request):
        assert request.query['signature'] == expected_signature
        return web.Response(
            body=b2p_answer,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    @mockserver.json_handler('/personal/v1/identifications/store')
    def _mock_identifications_store(request):
        assert request.json == {'value': expected_fullname, 'validate': True}
        return {
            'value': expected_fullname,
            'id': FULLNAME_MAP[expected_fullname],
        }

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        assert request.json == {'value': '+' + phone, 'validate': True}
        return {'value': '+' + phone, 'id': PHONE_MAP[phone]}

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_identifications_retrieve(request):
        assert request.json == {'id': FULLNAME_MAP[expected_fullname]}
        return {
            'value': expected_fullname,
            'id': FULLNAME_MAP[expected_fullname],
        }


@pytest.mark.parametrize(
    'jwt, expected_status, expected_code, expected_description',
    [
        (
            conftest.JWT_USER_2_EXPIRED,
            401,
            'unauthorized',
            'user is not authorized',
        ),
        ('', 401, 'unauthorized', 'user is not authorized'),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 1}],
    value={'enabled': False},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 2}],
    value={'enabled': True},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/sbp-enable',
    experiment_name='eats_tips_withdrawal_sbp_enable',
    args=[{'name': 'user_id', 'type': 'int', 'value': 3}],
    value={'enabled': True},
)
@pytest.mark.now('2021-05-04T00:12:44.477345+03:00')
async def test_sbp_create_precheck_tech_timeout_fail(
        taxi_eats_tips_withdrawal_web,
        mock_eats_tips_partners,
        web_app_client,
        jwt,
        expected_status,
        expected_code,
        expected_description,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8', 'alias': '1'},
        )

    idempotency_token = 'ZDc5MDYyYWUwODk4ZDYwMTNiYTYwNzlh'
    response = await web_app_client.post(
        '/v1/withdrawal/sbp/create-precheck',
        params={'phone': '79110000000', 'bank_id': '2', 'amount': 10},
        headers={
            'X-Idempotency-Token': idempotency_token,
            'X-Chaevie-Token': jwt,
        },
    )
    content = await response.json()
    assert content == {'code': expected_code, 'message': expected_description}
    assert response.status == expected_status
