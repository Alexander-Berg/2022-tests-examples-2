from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as test_http

from eats_tips_withdrawal.common import models
from eats_tips_withdrawal.common import withdrawal_sbp
from eats_tips_withdrawal.generated.web import web_context as context
from test_eats_tips_withdrawal import conftest


ERROR_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS['error'][0]
MANUAL_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS['manual'][
    0
]
SUCCESS_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS[
    'success'
][0]
PARTNERS_INFO = {
    '00000000-0000-0000-0000-000000000001': conftest.PARTNER_1,
    '00000000-0000-0000-0000-000000000002': conftest.PARTNER_2,
    '00000000-0000-0000-0000-000000000004': conftest.PARTNER_4,
    '00000000-0000-0000-0000-000000000005': conftest.PARTNER_5,
    '00000000-0000-0000-0000-000000000006': conftest.PARTNER_6,
    '00000000-0000-0000-0000-000000000011': conftest.PARTNER_11,
}
BIG_BALANCE = """<?xml version="1.0" encoding="UTF-8"?>
                <b2p_user>
                    <sector>666</sector>
                    <available_balance>10000000</available_balance>
                </b2p_user>"""
COMPLETE_OPERATION = """<?xml version="1.0" encoding="UTF-8"?>
                <operation>
                <order_state>COMPLETED</order_state>
                <order_id>%s</order_id>
                </operation>"""
ERROR_102 = """<?xml version="1.0" encoding="UTF-8"?>
                <error>
                <description>Incorrect Sector ID</description>
                <code>102</code>
                </error>"""
ERROR_142 = """<?xml version="1.0" encoding="UTF-8"?>
                <error>
                <description>Incorrect Sector ID</description>
                <code>142</code>
                </error>"""
ERROR_194 = """<?xml version="1.0" encoding="UTF-8"?>
                <error>
                <description>Incorrect Sector ID</description>
                <code>194</code>
                </error>"""
SENT_TO_MANUAL_CHECK = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNzl3',
    '',
    '',
    '',
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    0,
    2,
    '',
    '',
    0,
)
MANUAL_REJECTED = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNzl6',
    '',
    '',
    '',
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': (
            'Your request was rejected, please, '
            'try later or contact support for details'
        ),
    },
    models.WithdrawalRequestStatus.MANUAL_REJECTED.value,
    0,
    2,
    '',
    '',
    0,
)
ALREADY_SUCCESS_SENT = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNzl7',
    '',
    '',
    '',
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    2,
    '',
    '',
    0,
)
NO_PRECHECK = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz99',
    '',
    '',
    '',
    '',
    400,
    {'code': 'no_request', 'message': 'No such request'},
    None,
    None,
    None,
    '',
    '',
    0,
)
SUCCESS_ORDER_INFO = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz41',
    """
            <order>
                <id>25</id>
                <state>COMPLETED</state>
                <signature>ZWI0MTE1ZmNhMDI0YTlmYWNkMTEyZGViZDNkOTdmZTM=</signature>
            </order>
            """,
    '',
    ERROR_102,
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    2,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
REGISTERED_ORDER_INFO = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz41',
    """
            <order>
                <id>25</id>
                <state>REGISTERED</state>
                <signature>ZWI0MTE1ZmNhMDI0YTlmYWNkMTEyZGViZDNkOTdmZTM=</signature>
            </order>
            """,
    '',
    ERROR_102,
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.CAN_RETRY.value,
        'message': 'Error bank connection, try again later',
    },
    models.WithdrawalRequestStatus.AUTO_APPROVED.value,
    0,
    2,
    '',
    '',
    0,
)
MANUAL_CHECK_ERROR = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz41',
    """
            <order>
                <id>25</id>
                <state>REGISTERED</state>
                <signature>ZWI0MTE1ZmNhMDI0YTlmYWNkMTEyZGViZDNkOTdmZTM=</signature>
            </order>
            """,
    '',
    ERROR_142,
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': (
            'Произошла ошибка виртуальной карты 142, пожалуйста, '
            'обратитесь в поддержку.'
        ),
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    0,
    2,
    '',
    '',
    0,
)
DEFAULT_MANUAL_CHECK_ERROR = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz41',
    """
            <order>
                <id>25</id>
                <state>REGISTERED</state>
                <signature>ZWI0MTE1ZmNhMDI0YTlmYWNkMTEyZGViZDNkOTdmZTM=</signature>
            </order>
            """,
    '',
    ERROR_194,
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Произошла ошибка 194. Пожалуйста, обратитесь в поддержку.',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    0,
    2,
    '',
    '',
    0,
)
EXPIRED_ORDER_INFO = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz41',
    """
            <order>
                <id>25</id>
                <order_state>EXPIRED</order_state>
                <signature>ZWI0MTE1ZmNhMDI0YTlmYWNkMTEyZGViZDNkOTdmZTM=</signature>
            </order>
            """,
    '',
    ERROR_102,
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': 'Произошла ошибка 102. Пожалуйста, обратитесь в поддержку.',
    },
    models.WithdrawalRequestStatus.B2P_REJECTED.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
EXPIRED_CHECKOUT_ANSWER = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz41',
    """
        <order>
            <id>30</id>
            <order_state>EXPIRED</order_state>
            <signature>ZWI0MTE1ZmNhMDI0YTlmYWNkMTEyZGViZDNkOTdmZTM=</signature>
        </order>
    """,
    '',
    """<?xml version="1.0" encoding="UTF-8"?>
                <operation>
                <order_state>EXPIRED</order_state>
                <order_id>30</order_id>
                <reason_code>111</reason_code>
                </operation>""",
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': 'Произошла ошибка 111. Пожалуйста, обратитесь в поддержку.',
    },
    models.WithdrawalRequestStatus.B2P_REJECTED.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
CAN_NOT_GET_USER_BALANCE = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz21',
    '',
    '',
    '',
    ERROR_102,
    400,
    {'code': '102', 'message': 'Internal error'},
    models.WithdrawalRequestStatus.ERROR.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
TOO_MUCH_MONEY_REQUEST = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_1,
    conftest.PARTNER_1,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz22',
    '',
    '',
    '',
    """<?xml version="1.0" encoding="UTF-8"?>
                <b2p_user>
                    <sector>666</sector>
                    <available_balance>10000</available_balance>
                </b2p_user>""",
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': (
            'Requested amount(including fee) should be less or equal ' '100'
        ),
    },
    models.WithdrawalRequestStatus.ERROR.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
TOO_MUCH_REQUESTS = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_4,
    conftest.PARTNER_4,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz25',
    '',
    '',
    '',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANY_REQUESTS.value,
        'message': 'You already have 2 withdrawal requests, please, wait them',
    },
    models.WithdrawalRequestStatus.ERROR.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
SENT_TO_MANUAL_AND_BLOCK = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_5,
    conftest.PARTNER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz26',
    '',
    """<?xml version="1.0" encoding="UTF-8"?><response>
                   <code>1</code>
                   <description>Successful financial transaction</description>
               </response>""",
    '',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    1,
    2,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    1,
)
SENT_TO_MANUAL_AND_NOT_BLOCK = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_5,
    conftest.PARTNER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz26',
    '',
    """<?xml version="1.0" encoding="UTF-8"?><error>
                <description>Ошибка: неверная цифровая подпись.</description>
                <code>109</code>
                </error>""",
    '',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    1,
    2,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    0,
)
SUCCESS_AFTER_PRECHECK = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_5,
    conftest.PARTNER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz61',
    '',
    '',
    COMPLETE_OPERATION % '20',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    2,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
SUCCESS_AFTER_AUTO_APPROVED = (
    models.WithdrawalAntifraudCheckStatus.ALLOW.value,
    conftest.JWT_USER_6,
    conftest.PARTNER_6,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz62',
    '',
    '',
    COMPLETE_OPERATION % '21',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    2,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
SENT_TO_MANUAL_CHECK_YA_ANTIFRAUD = (
    models.WithdrawalAntifraudCheckStatus.MANUAL_ACCEPT.value,
    conftest.JWT_USER_5,
    conftest.PARTNER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz61',
    '',
    '',
    COMPLETE_OPERATION % '20',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    0,
    2,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    0,
)
SENT_TO_MANUAL_CHECK_YA_ANTIFRAUD_BLOCK = (
    models.WithdrawalAntifraudCheckStatus.BLOCK_WITHDRAWAL.value,
    conftest.JWT_USER_5,
    conftest.PARTNER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwNz61',
    '',
    '',
    COMPLETE_OPERATION % '20',
    BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    0,
    2,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    1,
)


@pytest.mark.parametrize(
    'ya_antifraud_result, jwt, partners_response, unique_precheck_key, '
    'order_info_response, set_restricted_response, b2p_checkout_answer, '
    'b2p_user_info_answer, expected_status, expected_result, '
    'expected_withdrawal_status, expected_manual_status, expected_pay_rows, '
    'expected_push_text, expected_push_title, expected_b2p_block_mcc, use_pg',
    [
        pytest.param(
            *SENT_TO_MANUAL_CHECK,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg sent to manual check already',
        ),
        pytest.param(
            *MANUAL_REJECTED,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg rejected already',
        ),
        pytest.param(
            *ALREADY_SUCCESS_SENT,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg sent to s2p(success) already',
        ),
        pytest.param(
            *NO_PRECHECK,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg no precheck',
        ),
        pytest.param(
            *SUCCESS_ORDER_INFO,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg success after get order info',
        ),
        pytest.param(
            *REGISTERED_ORDER_INFO,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg only registered in order info',
        ),
        pytest.param(
            *MANUAL_CHECK_ERROR,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg got the error and send to manual check with custom error',
        ),
        pytest.param(
            *DEFAULT_MANUAL_CHECK_ERROR,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg got the error and send to manual check with default error',
        ),
        pytest.param(
            *EXPIRED_ORDER_INFO,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg precheck expired in order info',
        ),
        pytest.param(
            *EXPIRED_CHECKOUT_ANSWER,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg precheck expired',
        ),
        pytest.param(
            *CAN_NOT_GET_USER_BALANCE,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg can not get balance',
        ),
        pytest.param(
            *TOO_MUCH_MONEY_REQUEST,
            True,
            marks=conftest.get_db_usage_exp(1, True),
            id='pg try withdraw more than have',
        ),
        pytest.param(
            *TOO_MUCH_REQUESTS,
            True,
            marks=conftest.get_db_usage_exp(4, True),
            id='pg too many withdrawal request on manual check',
        ),
        pytest.param(
            *SENT_TO_MANUAL_AND_BLOCK,
            True,
            marks=conftest.get_db_usage_exp(5, True),
            id='pg sent to manual check and block mcc',
        ),
        pytest.param(
            *SENT_TO_MANUAL_AND_NOT_BLOCK,
            True,
            marks=conftest.get_db_usage_exp(5, True),
            id='pg sent to manual check and not mcc block',
        ),
        pytest.param(
            *SUCCESS_AFTER_PRECHECK,
            True,
            marks=conftest.get_db_usage_exp(6, True),
            id='pg success after precheck created',
        ),
        pytest.param(
            *SUCCESS_AFTER_AUTO_APPROVED,
            True,
            marks=conftest.get_db_usage_exp(6, True),
            id='pg success after auto approved',
        ),
        pytest.param(
            *SENT_TO_MANUAL_CHECK_YA_ANTIFRAUD,
            True,
            marks=conftest.get_db_usage_exp(6, True),
            id='pg manual check ya antifraud',
        ),
        pytest.param(
            *SENT_TO_MANUAL_CHECK_YA_ANTIFRAUD_BLOCK,
            True,
            marks=conftest.get_db_usage_exp(6, True),
            id='pg manual check ya antifraud block withdrawal',
        ),
    ],
)
@pytest.mark.config(
    EATS_TIPS_WITHDRAWAL_ANTIFRAUD={
        'max_requests': 2,
        'one_card_pays': 3,
        'once_income_threshold': 3000,
        'safe_threshold': 10000,
        'safe_threshold_fresh': 1000,
    },
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-withdrawal', 'dst': 'personal'}],
)
@pytest.mark.now('2021-05-04T12:12:44.477345+03:00')
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_sbp_checkout(
        taxi_eats_tips_withdrawal_web,
        web_app_client,
        web_context,
        mock_best2pay,
        mock_eats_tips_partners,
        mock_eats_tips_payments,
        mockserver,
        mock_uantifraud,
        stq,
        ya_antifraud_result,
        jwt,
        partners_response,
        unique_precheck_key,
        order_info_response,
        set_restricted_response,
        b2p_checkout_answer,
        b2p_user_info_answer,
        expected_status,
        expected_result,
        expected_withdrawal_status,
        expected_manual_status,
        expected_pay_rows,
        expected_push_text,
        expected_push_title,
        expected_b2p_block_mcc,
        use_pg,
):
    await make_mocks(
        mock_best2pay,
        mock_eats_tips_partners,
        mock_eats_tips_payments,
        expected_manual_status,
        b2p_checkout_answer,
        b2p_user_info_answer,
        set_restricted_response,
        order_info_response,
        partners_response,
        mockserver,
        mock_uantifraud,
        ya_antifraud_result,
    )

    response = await web_app_client.get(
        '/v1/sbp/checkout',
        params={'unique_precheck_key': unique_precheck_key},
        headers={'X-Chaevie-Token': jwt},
    )
    content = await response.json()
    assert content == expected_result
    assert response.status == expected_status
    if expected_withdrawal_status is None:
        return
    async with web_context.pg.master_pool.acquire() as conn:
        withdrawal_row = await conn.fetchrow(
            f'select * from eats_tips_withdrawal.withdrawals where '
            f'idempotency_key=\'{unique_precheck_key}\'',
        )
        assert withdrawal_row['withdrawal_method'] == withdrawal_sbp.PAY_METHOD
        partner_id = str(withdrawal_row['partner_id'])
        amount = withdrawal_row['amount']

    assert withdrawal_row['status'] == expected_withdrawal_status
    if expected_manual_status:
        assert withdrawal_row['is_blacklist'] == 1
        assert withdrawal_row['is_one_card'] == 1
        assert withdrawal_row['exceeded_threshold'] == 1
        assert withdrawal_row['exceeded_threshold_fresh'] == 1
        assert withdrawal_row['is_from_3k_pay'] == 1

    await conftest.check_pushes(
        expected_push_text,
        expected_push_title,
        expected_withdrawal_status,
        amount,
        stq,
        partner_id,
        models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    )


async def make_mocks(
        mock_best2pay,
        mock_eats_tips_partners,
        mock_eats_tips_payments,
        expected_manual_status,
        b2p_checkout_answer,
        b2p_user_info_answer,
        set_restricted_response,
        order_info_response,
        partners_response,
        mockserver,
        mock_uantifraud,
        ya_antifraud_result,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8', 'alias': '1'},
        )

    @mock_eats_tips_partners('/v1/partner/block')
    async def _mock_block_user(request):
        return web.json_response()

    @mock_eats_tips_partners('/v1/alias-to-object')
    async def _mock_alias_to_object(request):
        return web.json_response(
            {'type': 'partner', 'partner': partners_response},
        )

    @mock_eats_tips_payments('/internal/v1/payments/from-blacklisted-cards')
    def _mock_blacklisted(request):
        return web.json_response({'count': int(expected_manual_status)})

    @mock_eats_tips_payments('/internal/v1/payments/max-pays-from-one-card')
    def _mock_one_card(request):
        return web.json_response({'count': 4 if expected_manual_status else 1})

    @mock_eats_tips_payments('/internal/v1/payments/max-income-amount')
    def _mock_max_amount(request):
        return web.json_response(
            {'amount': '4000.00' if expected_manual_status else '10'},
        )

    @mock_best2pay('/webapi/b2puser/PayOutSBP')
    async def _mock_sbp_checkout(request):
        return web.Response(
            body=b2p_checkout_answer,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    @mock_best2pay('/webapi/b2puser/Info')
    async def _mock_get_user_info(request):
        return web.Response(
            body=b2p_user_info_answer,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    @mock_best2pay('/webapi/Order')
    async def _mock_get_order_info(request):
        return web.Response(
            body=order_info_response,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_phones_retrieve(request):
        return {'id': request.json['id'], 'value': '+79998887766'}

    @mock_uantifraud('/v1/tips/withdrawal')
    async def _mock_tips_check(request: test_http.Request):
        return web.json_response({'status': ya_antifraud_result}, status=200)

    @mock_eats_tips_partners('/v1/partner')
    async def _mock_get_partner(request):
        partner_id = str(request.query['partner_id'])
        return web.json_response(
            {
                'id': PARTNERS_INFO[partner_id]['id'],
                'mysql_id': PARTNERS_INFO[partner_id]['mysql_id'],
                'display_name': '',
                'full_name': '',
                'phone_id': '',
                'saving_up_for': '',
                'registration_date': '2000-01-22T22:22:00+00:00',
                'is_vip': PARTNERS_INFO[partner_id]['is_vip'],
                'best2pay_blocked': False,
                'b2p_block_mcc': False,
                'b2p_block_full': False,
            },
        )
