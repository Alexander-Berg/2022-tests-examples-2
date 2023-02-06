import typing

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest

ROUBLES_CURRENCY_RULES = {
    'code': 'RUB',
    'sign': '₽',
    'template': '$VALUE$&nbsp$SIGN$$CURRENCY$',
    'text': 'руб.',
}


def _format_request_params(limit=3):
    return {
        'date_from': '2021-11-21T00:00:00+03:00',
        'date_to': '2021-11-22T00:00:00+03:00',
        'limit': limit,
    }


def _format_headers(jwt=conftest.JWT_USER_1):
    return {'X-Chaevie-Token': jwt}


def _format_transaction(
        transaction_id_hash,
        operation_type,
        created_at,
        amount,
        operation_status,
        mcc=None,
        mcc_name=None,
        card_pan=None,
        place_name=None,
        fee=None,
):
    result = {
        'hash': transaction_id_hash,
        'operation_type': operation_type,
        'created_at': created_at,
        'amount': {'price_value': amount},
        'operation_status': operation_status,
        'mcc': mcc,
        'mcc_name': mcc_name,
        'card_pan': card_pan,
        'place_name': place_name,
    }
    if fee is not None:
        result['fee'] = {'price_value': fee}
    return {key: value for key, value in result.items() if value is not None}


TRANSACTION_1 = _format_transaction(  # from b2p
    'ecdce0d02a2ce79a6f62c2ecdadcf460',
    'payment',
    '2021-11-21T20:54:24+03:00',
    '185.50',
    'completed',
    mcc='5812',
    mcc_name='Eating Places and Restaurants',
)
TRANSACTION_2 = _format_transaction(  # from eats-tips-payments
    '7c6d47949e202b50d1748a386778bc19',
    'income',
    '2021-11-21T20:50:00+03:00',
    '100.00',
    'completed',
    place_name='Заведение 1',
)
TRANSACTION_3 = _format_transaction(  # from b2p
    '9c7c359a9c1bfa58f398fd6e5b031de5',
    'payment',
    '2021-11-21T20:29:44+03:00',
    '156.00',
    'completed',
    mcc='4121',
    mcc_name='Taxicabs and Limousines',
)
TRANSACTION_4 = _format_transaction(  # from eats-tips-withdrawal
    '96eed3672b43f9a59a941a926cbd2912',
    'withdrawal',
    '2021-11-21T20:20:00+03:00',
    '200.00',
    'completed',
    fee='10',
    card_pan='676531******0129',
)

ALL_TRANSACTIONS = [TRANSACTION_1, TRANSACTION_2, TRANSACTION_3, TRANSACTION_4]
NON_PAYMENT_TRANSACTIONS = [TRANSACTION_2, TRANSACTION_4]


def _format_expected_response(*transactions):
    return {'transactions': list(transactions)}


def make_pytest_param(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        request_params: typing.Any = conftest.SENTINEL,
        request_headers: typing.Any = conftest.SENTINEL,
        b2p_response_filename: typing.Any = conftest.SENTINEL,
        expected_status: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(request_params, _format_request_params()),
        conftest.value_or_default(request_headers, _format_headers()),
        conftest.value_or_default(b2p_response_filename, 'b2p_response.xml'),
        conftest.value_or_default(expected_status, 200),
        conftest.value_or_default(
            expected_response,
            _format_expected_response(*ALL_TRANSACTIONS[:3]),
        ),
        id=id,
        marks=marks,
    )


@pytest.mark.parametrize(
    (
        'request_params',
        'request_headers',
        'b2p_response_filename',
        'expected_status',
        'expected_response',
    ),
    [
        make_pytest_param(id='success'),
        make_pytest_param(
            request_params=_format_request_params(limit=2),
            expected_response=_format_expected_response(
                TRANSACTION_1, TRANSACTION_2,
            ),
            id='small limit',
        ),
        make_pytest_param(
            request_params=_format_request_params(limit=4),
            expected_response=_format_expected_response(*ALL_TRANSACTIONS),
            id='big limit',
        ),
        make_pytest_param(
            b2p_response_filename='b2p_response_error.xml',
            expected_response=_format_expected_response(
                *NON_PAYMENT_TRANSACTIONS,
            ),
            id='b2p error response',
        ),
        make_pytest_param(
            expected_response=_format_expected_response(
                *NON_PAYMENT_TRANSACTIONS,
            ),
            id='payment transactions disabled',
            marks=[
                pytest.mark.config(
                    EATS_TIPS_ADMIN_RECIPIENT_TRANSACTIONS_SETTINGS={
                        'include_payments': False,
                    },
                ),
            ],
        ),
    ],
)
async def test_get_transactions(
        taxi_eats_tips_admin_web,
        mock_eats_tips_payments,
        mock_eats_tips_partners,
        mock_eats_tips_withdrawal,
        mock_best2pay,
        load,
        # params:
        request_params,
        request_headers,
        b2p_response_filename,
        expected_status,
        expected_response,
):
    @mock_eats_tips_payments('/internal/v1/orders/list')
    async def _mock_v1_orders_list(request: http.Request):
        assert request.query['recipient_ids'] == conftest.USER_ID_1
        assert request.query['date_from'] == '2021-11-21T00:00:00+03:00'
        assert request.query['date_to'] == '2021-11-22T00:00:00+03:00'
        assert request.query['limit'] == str(request_params['limit'])
        return web.json_response(
            {
                'orders': [
                    {
                        'order_id': '36e118ca-a148-48f2-87e3-69c0cdf302e8',
                        'recipient_id': conftest.USER_ID_1,
                        'place_id': 'place_id_1',
                        'created_at': '2021-11-21T20:50:00+03:00',
                        'recipient_amount': {'price_value': '100.00'},
                        'status': 'COMPLETED',
                    },
                ],
            },
            status=200,
        )

    @mock_eats_tips_withdrawal('/internal/v1/withdrawal/list')
    async def _mock_withdrawal_list(request: http.Request):
        assert request.query['recipient_id'] == conftest.USER_ID_1
        assert request.query['date_from'] == '2021-11-21T00:00:00+03:00'
        assert request.query['date_to'] == '2021-11-22T00:00:00+03:00'
        assert request.query['limit'] == str(request_params['limit'])
        return web.json_response(
            {
                'withdrawals': [
                    {
                        'id': 'withdrawal_1',
                        'amount': {
                            'price_value': '200.00',
                            'currency': ROUBLES_CURRENCY_RULES,
                        },
                        'created_at': '2021-11-21T20:20:00+03:00',
                        'status': 'success',
                        'card_pan': '676531******0129',
                        'fee': {
                            'price_value': '10',
                            'currency': ROUBLES_CURRENCY_RULES,
                        },
                    },
                ],
            },
            status=200,
        )

    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '1'})

    @mock_eats_tips_partners('/v1/partner')
    async def _mock_v1_partner(request: http.Request):
        partner_id = request.query['partner_id']
        assert partner_id == conftest.USER_ID_1
        return web.json_response(
            {
                'id': partner_id,
                'b2p_id': 'partner_b2p_id_1',
                'display_name': '',
                'full_name': '',
                'phone_id': 'phone_id_1',
                'saving_up_for': '',
                'best2pay_blocked': False,
                'registration_date': '1970-01-01T03:00:00+03:00',
                'is_vip': False,
                'blocked': False,
            },
            status=200,
        )

    @mock_eats_tips_partners('/v1/place/list')
    async def _mock_v1_place_list(request: http.Request):
        partners_ids = request.query['partners_ids']
        assert partners_ids == conftest.USER_ID_1
        return web.json_response(
            {
                'places': [
                    {
                        'info': {'id': 'place_id_1', 'title': 'Заведение 1'},
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

    @mock_best2pay('/webapi/b2puser/Statement')
    async def _mock_b2p_user_statement(request: http.Request):
        assert request.query['client_ref'] == 'partner_b2p_id_1'
        assert request.query['start'] == '2021.11.21T00:00:00'
        assert request.query['end'] == '2021.11.22T00:00:00'
        assert request.query['count'] == str(request_params['limit'])
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load(b2p_response_filename),
        )

    response = await taxi_eats_tips_admin_web.get(
        '/v1/recipient/transactions',
        params=request_params,
        headers=request_headers,
    )
    assert response.status == expected_status
    assert await response.json() == expected_response
