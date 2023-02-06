from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as test_http

from eats_tips_withdrawal.common import models
from eats_tips_withdrawal.common import withdrawal_card
from eats_tips_withdrawal.generated.web import web_context as context
from test_eats_tips_withdrawal import conftest


ERROR_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS['error'][0]
MANUAL_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS['manual'][
    0
]
SUCCESS_PUSH = context.config.Config.EATS_TIPS_WITHDRAWAL_PUSH_TEXTS[
    'success'
][0]
FULLNAME_MAP = {
    'заблоченный': 'FULLNAME_ID_2',
    'заблоченный юзер кафе': 'FULLNAME_ID_3',
    'официант': 'FULLNAME_ID_11',
}
PARTNERS_INFO = {
    '00000000-0000-0000-0000-000000000001': conftest.PARTNER_1,
    '00000000-0000-0000-0000-000000000002': conftest.PARTNER_2,
    '00000000-0000-0000-0000-000000000004': conftest.PARTNER_4,
    '00000000-0000-0000-0000-000000000005': conftest.PARTNER_5,
    '00000000-0000-0000-0000-000000000006': conftest.PARTNER_6,
    '00000000-0000-0000-0000-000000000011': conftest.PARTNER_11,
}
PARTNERS_INFO_BY_ALIAS = {
    '1': conftest.PARTNER_1,
    '2': conftest.PARTNER_2,
    '4': conftest.PARTNER_4,
    '5': conftest.PARTNER_5,
    '6': conftest.PARTNER_6,
    '11': conftest.PARTNER_11,
}
ENABLE_B2P_WITHDRAWAL_COMMISSION = pytest.mark.config(
    EATS_TIPS_WITHDRAWAL_COMMISSION_SETINGS={
        'withdrawal_type_settings': [
            {
                'withdrawal_type': 'best2pay',
                'max': 0,
                'min': 18,
                'percent': 0.01,
            },
            {'withdrawal_type': 'SBPb2p', 'max': 0, 'min': 0, 'percent': 0},
        ],
    },
)
RESPONSE_BIG_BALANCE = """<?xml version="1.0" encoding="UTF-8"?>
                <b2p_user>
                    <sector>666</sector>
                    <available_balance>10010000</available_balance>
                </b2p_user>"""
RESPONSE_SUCCESS_PAYOUT = """<?xml version="1.0" encoding="UTF-8"?><operation>
                <order_id>%s</order_id>
                <order_state>COMPLETED</order_state>
                <type>P2PTRANSFER</type>
                <state>APPROVED</state>
                <signature>MzEwMzM3NzgxYTM5NmE4NmZmOTk3YTk3NDAxYWViMDY=</signature>
                </operation>"""
RESPONSE_SUCCESS_REGISTER = """<?xml version="1.0" encoding="UTF-8"?><order>
                <id>%s</id>
                <state>REGISTERED</state>
                <amount>10000</amount>
                <currency>643</currency>
                <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
            </order>"""
SOME_B2P_ERROR_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?><error>
                <description>Ошибка: неверная цифровая подпись.</description>
                <code>109</code>
                </error>"""
FATAL_B2P_ERROR_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?><error>
                <description>Ошибка: неверная цифровая подпись.</description>
                <code>142</code>
                </error>"""
REQUEST_MORE_THEN_BALANCE = (
    conftest.JWT_USER_4,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    1000.3,
    conftest.PARTNER_4,
    '',
    '',
    '',
    '',
    """<?xml version="1.0" encoding="UTF-8"?>
                <b2p_user>
                    <sector>666</sector>
                    <available_balance>10010</available_balance>
                </b2p_user>""",
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': (
            'Requested amount(including fee) should be less or equal ' '100.1'
        ),
    },
    None,
    0,
    2,
    '',
    '',
    0,
)
REQUEST_PLUS_FEE_MORE_THEN_BALANCE = (
    conftest.JWT_USER_4,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    90,
    conftest.PARTNER_4,
    '',
    '',
    '',
    '',
    """<?xml version="1.0" encoding="UTF-8"?>
                <b2p_user>
                    <sector>666</sector>
                    <available_balance>10010</available_balance>
                </b2p_user>""",
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': (
            'Requested amount(including fee) should be less or equal ' '100.1'
        ),
    },
    None,
    0,
    2,
    '',
    '',
    0,
)
TOO_MUCH_REQUESTS = (
    conftest.JWT_USER_4,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    10.3,
    conftest.PARTNER_4,
    '',
    '',
    '',
    '',
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANY_REQUESTS.value,
        'message': 'You already have 2 withdrawal requests, please, wait them',
    },
    None,
    0,
    2,
    '',
    '',
    0,
)
USER_WITH_NO_CARD = (
    conftest.JWT_USER_6,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    10.3,
    conftest.PARTNER_6,
    '',
    '',
    '',
    '',
    RESPONSE_BIG_BALANCE,
    400,
    {'code': 'no_card', 'message': 'User have no card'},
    None,
    0,
    2,
    '',
    '',
    0,
)
ERROR_ORDER_REGISTRATION = (
    conftest.JWT_USER_2,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    10.3,
    conftest.PARTNER_2,
    '',
    '',
    SOME_B2P_ERROR_RESPONSE,
    '',
    RESPONSE_BIG_BALANCE,
    400,
    {'code': '109', 'message': 'Ошибка: неверная цифровая подпись.'},
    models.WithdrawalRequestStatus.ERROR.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
SENT_TO_MANUAL_AND_BLOCK = (
    conftest.JWT_USER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    21000,
    conftest.PARTNER_5,
    '',
    """<?xml version="1.0" encoding="UTF-8"?><response>
                   <code>1</code>
                   <description>Successful financial transaction</description>
               </response>""",
    RESPONSE_SUCCESS_REGISTER % '1617605',
    '',
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    1,
    4,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    1,
)
REQUEST_TOO_MUCH_MONEY = (
    conftest.JWT_USER_5,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    21000,
    conftest.PARTNER_5,
    '',
    SOME_B2P_ERROR_RESPONSE,
    RESPONSE_SUCCESS_REGISTER % '1617605',
    '',
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    1,
    4,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    0,
)
REQUEST_TOO_MUCH_MONEY_VIP = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    21000,
    conftest.PARTNER_11,
    """<?xml version="1.0" encoding="UTF-8"?><order>
                <id>1617605</id>
                <state>COMPLETED</state>
                <amount>10000</amount>
                <currency>643</currency>
                <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
            </order>""",
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    SOME_B2P_ERROR_RESPONSE,
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    4,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
REJECTED_BY_BANK = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    100,
    conftest.PARTNER_11,
    SOME_B2P_ERROR_RESPONSE,
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    SOME_B2P_ERROR_RESPONSE,
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': 'Произошла ошибка 109. Пожалуйста, обратитесь в поддержку.',
    },
    models.WithdrawalRequestStatus.B2P_REJECTED.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
FATALY_REJECTED_BY_BANK = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    100,
    conftest.PARTNER_11,
    """<?xml version="1.0" encoding="UTF-8"?><order>
            <id>1617605</id>
            <state>REGISTERED</state>
            <amount>10000</amount>
            <currency>643</currency>
            <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
        </order>""",
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    FATAL_B2P_ERROR_RESPONSE,
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': (
            'Произошла ошибка виртуальной карты 142, пожалуйста, '
            'обратитесь в поддержку.'
        ),
    },
    models.WithdrawalRequestStatus.B2P_REJECTED.value,
    0,
    1,
    ERROR_PUSH['text']['default'],
    ERROR_PUSH['title']['default'],
    0,
)
ORDER_INFO_REGISTERED = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    100,
    conftest.PARTNER_11,
    """<?xml version="1.0" encoding="UTF-8"?><order>
                <id>1617605</id>
                <state>REGISTERED</state>
                <amount>10000</amount>
                <currency>643</currency>
                <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
            </order>""",
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    SOME_B2P_ERROR_RESPONSE,
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.CAN_RETRY.value,
        'message': 'Error bank connection, try again later',
    },
    models.WithdrawalRequestStatus.AUTO_APPROVED.value,
    0,
    4,
    '',
    '',
    0,
)
ORDER_INFO_COMPLETED = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    100,
    conftest.PARTNER_11,
    """<?xml version="1.0" encoding="UTF-8"?><order>
                <id>1617605</id>
                <state>COMPLETED</state>
                <amount>10000</amount>
                <currency>643</currency>
                <signature>MDFmMDE0MWU4YjdhY2YwOGM0YWMzNDVjZmNlZjA3ZWI=</signature>
            </order>""",
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    SOME_B2P_ERROR_RESPONSE,
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    4,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
PAYOUT_SUCCESS = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    100,
    conftest.PARTNER_11,
    '',
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    RESPONSE_SUCCESS_PAYOUT % '1617605',
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    4,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
REQUEST_WITH_ERROR = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN001',
    1000.3,
    conftest.PARTNER_11,
    '',
    '',
    '',
    '',
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.ERROR.value,
        'message': (
            'Your request was rejected, please, try later '
            'or contact support for details'
        ),
    },
    None,
    0,
    1,
    '',
    '',
    0,
)
ALREADY_SUCCESS_REQUEST = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN002',
    100,
    conftest.PARTNER_11,
    '',
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
    4,
    '',
    '',
    0,
)
SUCCESS_AFTER_PRECHECK = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN003',
    100,
    conftest.PARTNER_11,
    '',
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    RESPONSE_SUCCESS_PAYOUT % '1617605',
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    4,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
SUCCESS_AFTER_PRECHECK_ORDER = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN004',
    100,
    conftest.PARTNER_11,
    '',
    '',
    '',
    RESPONSE_SUCCESS_PAYOUT % '1617602',
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    4,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
SUCCESS_AFTER_AUTO_APPROVED = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN005',
    100,
    conftest.PARTNER_11,
    '',
    '',
    '',
    RESPONSE_SUCCESS_PAYOUT % '1617603',
    '',
    200,
    {
        'status': models.WithdrawalCheckoutStatus.SUCCESS.value,
        'message': 'Successfully finished',
    },
    models.WithdrawalRequestStatus.SENT_TO_B2P.value,
    0,
    4,
    SUCCESS_PUSH['text']['default'],
    SUCCESS_PUSH['title']['default'],
    0,
)
ALREADY_MANUAL_CHECK = (
    conftest.JWT_USER_11,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN006',
    100,
    conftest.PARTNER_11,
    '',
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
    4,
    '',
    '',
    0,
)
MANUAL_CHECK_SEVERAL_WITHDRAWAL_CARD_FRAUD = (
    conftest.JWT_USER_2,
    'D12345YyYWUwODk4ZDYwMTNiYTYwN000',
    10,
    conftest.PARTNER_2,
    '',
    '',
    RESPONSE_SUCCESS_REGISTER % '1617605',
    RESPONSE_SUCCESS_PAYOUT % '1617605',
    RESPONSE_BIG_BALANCE,
    200,
    {
        'status': models.WithdrawalCheckoutStatus.MANUAL.value,
        'message': 'Request sent to manual check',
    },
    models.WithdrawalRequestStatus.MANUAL_CHECK.value,
    3,
    4,
    MANUAL_PUSH['text']['default'],
    MANUAL_PUSH['title']['default'],
    0,
)


@pytest.mark.parametrize(
    'jwt, unique_precheck_key, amount, partners_response, '
    'order_info_response, set_restricted_response, b2p_register_answer, '
    'b2p_checkout_answer, b2p_user_info_answer, expected_status, '
    'expected_result, expected_withdrawal_status, expected_manual_status, '
    'expected_pay_rows, expected_push_text, expected_push_title, '
    'expected_b2p_block_mcc, use_pg',
    [
        pytest.param(
            *REQUEST_MORE_THEN_BALANCE,
            True,
            marks=conftest.get_db_usage_exp(4, True),
            id='pg too much money to request',
        ),
        pytest.param(
            *REQUEST_PLUS_FEE_MORE_THEN_BALANCE,
            True,
            marks=[
                conftest.get_db_usage_exp(4, True),
                ENABLE_B2P_WITHDRAWAL_COMMISSION,
            ],
            id='pg too much money to request including fee',
        ),
        pytest.param(
            *TOO_MUCH_REQUESTS,
            True,
            marks=conftest.get_db_usage_exp(4, True),
            id='pg too much requests',
        ),
        pytest.param(
            *USER_WITH_NO_CARD,
            True,
            marks=conftest.get_db_usage_exp(6, True),
            id='pg user have no card',
        ),
        pytest.param(
            *ERROR_ORDER_REGISTRATION,
            True,
            marks=conftest.get_db_usage_exp(2, True),
            id='pg error order registration',
        ),
        pytest.param(
            *SENT_TO_MANUAL_AND_BLOCK,
            True,
            marks=conftest.get_db_usage_exp(5, True),
            id='pg sent to manual check and block',
        ),
        pytest.param(
            *REQUEST_TOO_MUCH_MONEY,
            True,
            marks=conftest.get_db_usage_exp(5, True),
            id='pg request to withdraw big amount, not vip',
        ),
        pytest.param(
            *REQUEST_TOO_MUCH_MONEY_VIP,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg request to withdraw big amount, vip',
        ),
        pytest.param(
            *REJECTED_BY_BANK,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg error all around vip',
        ),
        pytest.param(
            *FATALY_REJECTED_BY_BANK,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg fatal error - invalidate',
        ),
        pytest.param(
            *ORDER_INFO_REGISTERED,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg registered order info',
        ),
        pytest.param(
            *ORDER_INFO_COMPLETED,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg complete order info',
        ),
        pytest.param(
            *PAYOUT_SUCCESS,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg success payout',
        ),
        pytest.param(
            *REQUEST_WITH_ERROR,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg request with error',
        ),
        pytest.param(
            *ALREADY_SUCCESS_REQUEST,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg already success',
        ),
        pytest.param(
            *SUCCESS_AFTER_PRECHECK,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg success after precheck',
        ),
        pytest.param(
            *SUCCESS_AFTER_PRECHECK_ORDER,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg success precheck + order_id',
        ),
        pytest.param(
            *SUCCESS_AFTER_AUTO_APPROVED,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg success after auto approved',
        ),
        pytest.param(
            *ALREADY_MANUAL_CHECK,
            True,
            marks=conftest.get_db_usage_exp(11, True),
            id='pg already manual check',
        ),
        pytest.param(
            *MANUAL_CHECK_SEVERAL_WITHDRAWAL_CARD_FRAUD,
            True,
            marks=conftest.get_db_usage_exp(2, True),
            id='pg withdrawal card fraud',
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
    EATS_TIPS_WITHDRAWAL_COMMISSION_SETINGS={
        'withdrawal_type_settings': [
            {'withdrawal_type': 'best2pay', 'max': 0, 'min': 0, 'percent': 0},
            {'withdrawal_type': 'SBPb2p', 'max': 0, 'min': 0, 'percent': 0},
        ],
    },
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 90.0},
    ],
    value={'min': 18, 'max': 100, 'percent': 1},
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-withdrawal', 'dst': 'personal'}],
)
@pytest.mark.config(
    EATS_TIPS_WITHDRAWAL_ERROR_SETTINGS={
        'bd_error_separator': '<br>',
        'default_error_text': {
            'default': (
                'Произошла ошибка {error_code}. '
                'Пожалуйста, обратитесь в поддержку.'
            ),
        },
        'errors': [
            {
                'error_id': 142,
                'text': {
                    'default': (
                        'Произошла ошибка виртуальной карты {error_code},'
                        ' пожалуйста, обратитесь в поддержку.'
                    ),
                },
            },
            {'error_id': 194, 'manual_check': True},
            {'error_id': 165, 'manual_check': True},
            {'error_id': 185, 'manual_check': True},
        ],
    },
)
@pytest.mark.now('2021-06-22T19:11:44.477345+03:00')
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_b2p_card_withdrawal(
        taxi_eats_tips_withdrawal_web,
        mock_eats_tips_partners,
        mock_eats_tips_payments,
        web_app_client,
        web_context,
        mock_best2pay,
        stq,
        mockserver,
        mock_uantifraud,
        jwt,
        unique_precheck_key,
        amount,
        partners_response,
        order_info_response,
        set_restricted_response,
        b2p_register_answer,
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
        mockserver,
        partners_response,
        b2p_register_answer,
        b2p_checkout_answer,
        b2p_user_info_answer,
        set_restricted_response,
        order_info_response,
        mock_uantifraud,
    )

    response = await web_app_client.post(
        '/v1/withdrawal/to-card',
        params={'amount': str(amount)},
        headers={
            'X-Chaevie-Token': jwt,
            'X-Idempotency-Token': unique_precheck_key,
        },
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
        assert (
            withdrawal_row['withdrawal_method'] == withdrawal_card.PAY_METHOD
        )
        partner_id = str(withdrawal_row['partner_id'])
        amount = withdrawal_row['amount']

    assert withdrawal_row['status'] == expected_withdrawal_status
    if expected_manual_status:
        if expected_manual_status < 2:
            assert withdrawal_row['is_blacklist'] == 1
            assert withdrawal_row['is_one_card'] == 1
            assert withdrawal_row['exceeded_threshold_fresh'] == 1
            assert withdrawal_row['is_from_3k_pay'] == 1
        elif expected_manual_status in (1, 2):
            assert withdrawal_row['exceeded_threshold'] == 1

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
        mockserver,
        partners_response,
        b2p_register_answer,
        b2p_checkout_answer,
        b2p_user_info_answer,
        set_restricted_response,
        order_info_response,
        mock_uantifraud,
):
    expected_fullname = partners_response['full_name']

    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {
                'id': PARTNERS_INFO_BY_ALIAS[request.query['alias']]['id'],
                'alias': request.query['alias'],
            },
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
    async def _mock_blacklisted(request):
        return web.json_response({'count': 1 if expected_manual_status else 0})

    @mock_eats_tips_payments('/internal/v1/payments/max-pays-from-one-card')
    def _mock_one_card(request):
        return web.json_response({'count': 4 if expected_manual_status else 1})

    @mock_eats_tips_payments('/internal/v1/payments/max-income-amount')
    def _mock_max_amount(request):
        return web.json_response(
            {'amount': '4000.00' if expected_manual_status else 10},
        )

    @mock_best2pay('/webapi/Register')
    async def _mock_register_order(request):
        return web.Response(
            body=b2p_register_answer,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    @mock_best2pay('/webapi/b2puser/PayOut2')
    async def _mock_payout2(request):
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

    @mockserver.json_handler('/personal/v1/identifications/store')
    def _mock_identifications_store(request):
        assert request.json == {'value': expected_fullname, 'validate': True}
        return {
            'value': expected_fullname,
            'id': FULLNAME_MAP[expected_fullname],
        }

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_identifications_retrieve(request):
        assert request.json == {'id': FULLNAME_MAP[expected_fullname]}
        return {
            'value': expected_fullname,
            'id': FULLNAME_MAP[expected_fullname],
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_phones_retrieve(request):
        return {'id': request.json['id'], 'value': '+79998887766'}

    @mock_uantifraud('/v1/tips/withdrawal')
    async def _mock_tips_check(request: test_http.Request):
        return web.json_response({'status': 'allow'}, status=200)

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

    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v2_partner(request):
        partner_id = str(request.query['partner_id'])
        return web.json_response(
            conftest.format_partner_response(partner_id), status=200,
        )
