# pylint: disable=too-many-lines,unused-variable
import datetime
import decimal
import typing
import uuid

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as test_http

from eats_tips import components as tips_common

from eats_tips_payments.models import order as models_order
from test_eats_tips_payments import conftest

PLUS_DEFAULT_PERCENT = 0.05
PLUS_DEFAULT_THRESHOLD = 100
LOGIN_IP_HEADERS = {'X-Yandex-Login': '123', 'X-Remote-IP': '1.2.3.4'}

NOW = datetime.datetime(2021, 6, 15, 14, 30, 15, tzinfo=datetime.timezone.utc)


def _format_request_body(
        *,
        amount_str='50',
        commission_str='3',
        amount: int = 50,
        payment_type: str = 'apple_pay_b2p',
        payment_token: typing.Optional[dict] = None,
        yandex_token: typing.Optional[str] = None,
        recipient_type: str = 'partner',
        round_profit: typing.Optional[str] = None,
        place_id: typing.Optional[str] = conftest.PLACE_ID_2,
):
    request_body = {
        'amount_str': amount_str,
        'alias': '1',
        'commission_str': commission_str,
        'payment_type': payment_type,
        'recipient_id': conftest.PARTNER_ID_1,
        'recipient_type': recipient_type,
        'payload': {
            'amount': amount,
            'review_id': 'review00-0000-0000-0000-cb2691e1af56',
            'PKPaymentToken': payment_token or {'paymentData': {}},
            'user_id': '',
        },
    }
    if yandex_token:
        request_body['payload']['yandexToken'] = yandex_token
    if place_id:
        request_body['place_id'] = place_id
    if round_profit:
        request_body['round_profit'] = round_profit
    return request_body


def _format_headers(*, idempotency_token: str = 'idempotency_token_2'):
    return {
        'X-Idempotency-Token': idempotency_token,
        'X-Tips-Link': 'tips_link_1',
        **LOGIN_IP_HEADERS,
    }


def _format_eats_tips_partners_response(
        *, blocked=False, place_id=conftest.PLACE_ID_2,
):
    result = {
        'info': {
            'id': conftest.PARTNER_ID_1,
            'b2p_id': 'partner_b2p_id_1',
            'display_name': '',
            'full_name': '',
            'phone_id': 'phone_id_1',
            'saving_up_for': '',
            'best2pay_blocked': False,
            'registration_date': '1970-01-01T03:00:00+03:00',
            'is_vip': False,
            'blocked': blocked,
            'date_first_pay': '2000-01-22T22:22:00+00:00',
            'is_admin_reg': False,
            'is_free_procent': False,
            'trans_guest': False,
            'trans_guest_block': False,
        },
        'places': [
            {
                'place_id': place_id,
                'title': '',
                'address': '',
                'confirmed': True,
                'show_in_menu': True,
                'roles': [],
            },
        ],
    }
    if place_id == conftest.PLACE_ID_1:
        result['places'][0]['brand_slug'] = 'shoko'
    return result


def _format_eats_tips_partners_sd_response(*, sd_id=str(uuid.uuid4())):
    return {
        'id': sd_id,
        'display_name': 'display_name',
        'alias': 'alias',
        'place_id': 'place_id_1',
        'avatar': '',
        'balance': '0',
        'caption': '',
        'fallback_partner_id': '',
        'saving_up_for': '',
        'registration_date': '2000-01-22T22:22:00+00:00',
        'trans_guest': False,
        'trans_guest_block': False,
    }


def make_pytest_param(
        *,
        id,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        request_body: typing.Any = conftest.SENTINEL,
        request_headers: typing.Any = conftest.SENTINEL,
        eats_tips_partners_response: typing.Any = conftest.SENTINEL,
        b2p_register_response: typing.Any = conftest.SENTINEL,
        b2p_pay_in_debit_response: typing.Any = conftest.SENTINEL,
        expected_status: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
        b2p_expected_amount: typing.Any = conftest.SENTINEL,
        b2p_expected_fee: typing.Any = conftest.SENTINEL,
        b2p_register_times_called: typing.Any = conftest.SENTINEL,
        b2p_pay_in_debit_times_called: typing.Any = conftest.SENTINEL,
        b2p_complete_times_called: typing.Any = conftest.SENTINEL,
        b2p_sdcomplete_times_called: typing.Any = conftest.SENTINEL,
        expected_order_status: typing.Any = conftest.SENTINEL,
        eats_tips_partners_sd_response: typing.Any = conftest.SENTINEL,
        expected_block_type: typing.Any = conftest.SENTINEL,
        ya_antifraud_answer: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(request_body, _format_request_body()),
        conftest.value_or_default(request_headers, _format_headers()),
        conftest.value_or_default(
            eats_tips_partners_response, _format_eats_tips_partners_response(),
        ),
        conftest.value_or_default(
            b2p_register_response, 'b2p_register_response.xml',
        ),
        conftest.value_or_default(
            b2p_pay_in_debit_response, 'b2p_pay_in_debit_response.html',
        ),
        conftest.value_or_default(expected_status, 200),
        conftest.value_or_default(expected_response, None),
        conftest.value_or_default(b2p_expected_amount, '4700'),
        conftest.value_or_default(b2p_expected_fee, '300'),
        conftest.value_or_default(b2p_register_times_called, 1),
        conftest.value_or_default(b2p_pay_in_debit_times_called, 1),
        conftest.value_or_default(b2p_complete_times_called, 0),
        conftest.value_or_default(b2p_sdcomplete_times_called, 0),
        conftest.value_or_default(expected_order_status, 'REDIRECTED'),
        conftest.value_or_default(
            eats_tips_partners_sd_response,
            _format_eats_tips_partners_sd_response(),
        ),
        conftest.value_or_default(
            expected_block_type, tips_common.TrancodeUserBlock.TOTAL,
        ),
        conftest.value_or_default(ya_antifraud_answer, 'allow'),
        id=id,
        marks=marks,
    )


@pytest.mark.config(
    TVM_USER_TICKETS_ENABLED=True,
    TVM_API_URL='$mockserver/tvm',
    EATS_TIPS_PAYMENTS_PLUS_SETTINGS={
        'enabled': False,
        'payment_ttl': 0,
        'service_name': 'tips',
    },
    EATS_TIPS_PAYMENTS_AMOUNT_SETTINGS={'max_amount': 10000, 'min_amount': 5},
    TVM_RULES=[{'src': 'eats-tips-payments', 'dst': 'personal'}],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    TVM_USER_TICKETS_ENABLED=True,
    TVM_API_URL='$mockserver/tvm',
    EATS_TIPS_PAYMENTS_COMMISSION_SETTINGS={'percent': 6},
)
@pytest.mark.parametrize(
    'request_body,'
    'request_headers,'
    'eats_tips_partners_response,'
    'b2p_register_response,'
    'b2p_pay_in_debit_response,'
    'expected_status,'
    'expected_response,'
    'b2p_expected_amount,'
    'b2p_expected_fee,'
    'b2p_register_times_called,'
    'b2p_pay_in_debit_times_called,'
    'b2p_complete_times_called,'
    'b2p_sdcomplete_times_called,'
    'expected_order_status,'
    'eats_tips_partners_sd_response,'
    'expected_block_type,'
    'ya_antifraud_answer,',
    (
        make_pytest_param(
            id='round_profit',
            request_body=_format_request_body(round_profit='100'),
        ),
        make_pytest_param(id='success'),
        make_pytest_param(
            id='ya antifraud blocked transaction',
            expected_status=403,
            expected_response={
                'code': 'antifraud_failed',
                'message': 'Failed ya antifraud check',
            },
            b2p_pay_in_debit_times_called=0,
            ya_antifraud_answer=(
                models_order.AntifraudCheckStatus.BLOCK_WITHDRAWAL.value
            ),
            b2p_register_times_called=0,
        ),
        make_pytest_param(
            id='ya antifraud blocked account',
            expected_status=403,
            expected_response={
                'code': 'antifraud_failed',
                'message': 'Failed ya antifraud check',
            },
            b2p_pay_in_debit_times_called=0,
            b2p_register_times_called=0,
            ya_antifraud_answer=(
                models_order.AntifraudCheckStatus.BLOCK_ACCOUNT.value
            ),
        ),
        make_pytest_param(
            id='payment type is google pay',
            request_body=_format_request_body(
                payment_type='google_pay_b2p',
                payment_token={'tokenizationData': {'token': 'test'}},
            ),
        ),
        make_pytest_param(
            id='payment money_box type to complete',
            request_body=_format_request_body(
                payment_type='google_pay_b2p',
                recipient_type='money_box',
                payment_token={'tokenizationData': {'token': 'test'}},
            ),
            eats_tips_partners_sd_response=_format_eats_tips_partners_sd_response(  # noqa: F401,E501
                sd_id='20000000-0000-0000-0000-000000000200',
            ),
            b2p_sdcomplete_times_called=1,
            expected_order_status='COMPLETED',
            b2p_pay_in_debit_response=web.Response(
                status=302, headers={'Location': 'test'},
            ),
            expected_response={'url': 'test'},
        ),
        make_pytest_param(
            id='payment money_box type to complete without active sd',
            request_body=_format_request_body(recipient_type='money_box'),
            b2p_sdcomplete_times_called=1,
            expected_order_status='COMPLETED',
            b2p_pay_in_debit_response=web.Response(
                status=302, headers={'Location': 'test'},
            ),
            expected_response={'url': 'test'},
        ),
        make_pytest_param(
            id='payment type is google pay to money_box',
            request_body=_format_request_body(
                payment_type='google_pay_b2p',
                recipient_type='money_box',
                payment_token={'tokenizationData': {'token': 'test'}},
            ),
            b2p_sdcomplete_times_called=0,
        ),
        make_pytest_param(
            id='payment type is yandex pay',
            request_body=_format_request_body(
                payment_type='yandex_pay_b2p', yandex_token='test',
            ),
        ),
        make_pytest_param(
            id='payment type is card',
            request_body=_format_request_body(payment_type='b2p'),
            expected_response={
                # 'order_id_str': ...,  # autogenerated
                'url': (
                    '$mockserver/best2pay/webapi/b2puser/PayInDebit'
                    '?id=457'
                    '&sector=6666'
                    '&signature=YmU4ZWQzMjg1N2E2Yzk2YzAzZTBiODhjN2E3YjYwNzg%3D'
                ),
            },
            b2p_pay_in_debit_times_called=0,
        ),
        make_pytest_param(
            id='idempotency token is already in db',
            expected_status=409,
            request_headers=_format_headers(
                idempotency_token='idempotency_token_1',
            ),
            expected_response={
                'code': 'idempotency_token_is_already_registered',
                'message': '',
            },
            b2p_register_times_called=0,
        ),
        make_pytest_param(
            id='b2p register error response',
            b2p_register_response='b2p_register_response_error.xml',
            expected_status=400,
            expected_response={'code': 'best2pay_error', 'message': ''},
            b2p_pay_in_debit_times_called=0,
            expected_order_status='REGISTER_FAILED',
        ),
        make_pytest_param(
            id='redirect to complete',
            b2p_pay_in_debit_response=web.Response(
                status=302, headers={'Location': 'test'},
            ),
            expected_response={'url': 'test'},
            b2p_pay_in_debit_times_called=1,
            b2p_complete_times_called=1,
            expected_order_status='COMPLETED',
        ),
        make_pytest_param(
            id='wrong given commission',
            request_body=_format_request_body(
                amount_str='50', commission_str='4',
            ),
            expected_status=400,
            expected_response={
                'code': 'commission_is_different',
                'message': 'calculated commission is 3 but given value is 4',
            },
            b2p_register_times_called=0,
        ),
        make_pytest_param(
            id='low amount',
            request_body=_format_request_body(
                amount_str='0', commission_str='0',
            ),
            expected_status=400,
            expected_response={
                'code': 'invalid_amount',
                'message': 'total amount must be a number between 5 and 10000',
            },
            b2p_register_times_called=0,
        ),
        make_pytest_param(
            id='high amount',
            request_body=_format_request_body(
                amount_str='10001', commission_str='601',
            ),
            expected_status=400,
            expected_response={
                'code': 'invalid_amount',
                'message': 'total amount must be a number between 5 and 10000',
            },
            b2p_register_times_called=0,
        ),
        make_pytest_param(
            id='brand is shoko (no commission)',
            eats_tips_partners_response=_format_eats_tips_partners_response(
                place_id=conftest.PLACE_ID_1,
            ),
            request_body=_format_request_body(
                payment_type='yandex_pay_b2p',
                yandex_token='test',
                place_id=conftest.PLACE_ID_1,
            ),
            b2p_expected_amount='5000',
            b2p_expected_fee='0',
        ),
        # TODO: move other test cases
    ),
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[{'name': 'brand_slug', 'type': 'string', 'value': 'shoko'}],
    value={
        'commission_percent': 5,
        'commission_should_be_compensated': True,
        'theme_name': 'shoko',
        'promo_url': 'test_promo_url',
        'promo_image_url': 'test_promo_image_url',
    },
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/brand-settings',
    config_name='eats_tips_payments_brand_settings',
    args=[],
    value={'commission_percent': 6, 'commission_should_be_compensated': False},
)
async def test_register_payment(
        web_app_client,
        mocked_tvm,
        web_context,
        mock_best2pay,
        mock_uantifraud,
        mock_eats_tips_partners,
        pgsql,
        load,
        # params:
        request_body,
        request_headers,
        eats_tips_partners_response,
        b2p_register_response,
        b2p_pay_in_debit_response,
        expected_status,
        expected_response,
        b2p_expected_amount,
        b2p_expected_fee,
        b2p_register_times_called,
        b2p_pay_in_debit_times_called,
        b2p_complete_times_called,
        b2p_sdcomplete_times_called,
        expected_order_status,
        eats_tips_partners_sd_response,
        expected_block_type,
        ya_antifraud_answer,
):
    if request_body['recipient_type'] == 'partner':
        recipient_id = eats_tips_partners_response['info']['id']
    else:
        recipient_id = eats_tips_partners_sd_response['id']

    @mock_best2pay('/webapi/Register')
    async def _mock_b2p_register(request: test_http.Request):
        assert request.form['amount'] == b2p_expected_amount
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load(b2p_register_response),
        )

    @mock_best2pay('/webapi/b2puser/PayInDebit')
    async def _mock_b2p_pay_in_debit(request: test_http.Request):
        assert request.form['id'] == '457'
        if isinstance(b2p_pay_in_debit_response, web.Response):
            # to return redirect
            return b2p_pay_in_debit_response
        return web.Response(
            status=200,
            content_type='text/html',
            body=load(b2p_pay_in_debit_response),
        )

    @mock_best2pay('/webapi/b2puser/Complete')
    async def _mock_b2p_complete(request: test_http.Request):
        assert request.form['id'] == '457'
        return web.Response(
            status=200,
            content_type='text/html',
            body=load('b2p_complete_response.xml'),
        )

    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v1_partner(request: test_http.Request):
        return web.json_response(eats_tips_partners_response, status=200)

    @mock_best2pay('/webapi/b2puser/sd-services/SDComplete')
    async def _mock_b2p_sdcomplete(request: test_http.Request):
        assert request.form['id'] == '457'
        return web.Response(
            status=200,
            content_type='text/html',
            body=load('b2p_sd_complete_response.xml'),
        )

    @mock_eats_tips_partners('/v1/money-box')
    async def _mock_eats_tips_money_box(request: test_http.Request):
        return web.json_response(eats_tips_partners_sd_response, status=200)

    @mock_uantifraud('/v1/tips/deposit')
    async def _mock_tips_check(request: test_http.Request):
        return web.json_response({'status': ya_antifraud_answer}, status=200)

    @mock_eats_tips_partners('/v1/partner/block')
    async def _mock_block_user(request):
        assert request.json['partner_id'] == request_body['recipient_id']
        assert request.json['reason'] == 'ya_payment_antifraud'
        assert request.json['block_state'] == expected_block_type.value
        return web.json_response()

    response = await web_app_client.post(
        '/v1/payments/register',
        json=request_body,
        headers=request_headers,
        allow_redirects=False,
    )
    assert response.status == expected_status
    response_json = await response.json()
    if expected_status == 200:
        assert response_json['order_id_str']
        # unable to check cause autogenerated
        response_json.pop('order_id_str', None)
    if expected_response is not None:
        assert response_json == expected_response
    assert _mock_b2p_register.times_called == b2p_register_times_called
    if b2p_register_times_called > 0:
        assert (
            _mock_b2p_pay_in_debit.times_called
            == b2p_pay_in_debit_times_called
        )
        if request_body['recipient_type'] == 'partner':
            assert _mock_b2p_complete.times_called == b2p_complete_times_called
        else:
            assert (
                _mock_b2p_sdcomplete.times_called
                == b2p_sdcomplete_times_called
            )

    if b2p_register_times_called > 0:
        with pgsql['eats_tips_payments'].dict_cursor() as cursor:
            cursor.execute(
                'select * from eats_tips_payments.orders order by created_at;',
            )
            order = cursor.fetchall()[-1]
        assert order['status'] == expected_order_status
        assert order['tips_link'] == 'tips_link_1'
        assert order['recipient_id'] == recipient_id
        assert order['recipient_type'] == request_body['recipient_type']
        try:
            assert order['round_profit'] == decimal.Decimal(
                request_body['round_profit'],
            )
        except KeyError:
            assert order['round_profit'] == decimal.Decimal('0')
        assert order['place_id'] in (conftest.PLACE_ID_1, conftest.PLACE_ID_2)
        if expected_order_status == 'COMPLETED':
            assert order['order_id_b2p'] == '457'
            assert order['status_b2p']
            assert order['card_pan'] == '676531******0129'
            assert order['status_b2p'] == 'COMPLETED'


@pytest.mark.config(EATS_TIPS_PAYMENTS_COMMISSION_SETTINGS={'percent': 6})
@pytest.mark.client_experiments3(
    consumer='eats-tips-payments/registration_payment_400',
    experiment_name='eda_tips_payments_registration_payment_400',
    args=[
        {'name': 'yandex_uid', 'type': 'string', 'value': conftest.TEST_UID},
    ],
    value={},
)
async def test_400_experiment(web_app_client):
    request_body = {
        'payment_type': 'apple_pay_b2p',
        'recipient_id': '',
        'payload': {'amount': 50, 'user_id': '000010', 'PKPaymentToken': {}},
    }
    request_headers = {'X-Yandex-UID': conftest.TEST_UID, **LOGIN_IP_HEADERS}
    response = await web_app_client.post(
        '/v1/payments/register', json=request_body, headers=request_headers,
    )

    assert response.status == 400
    response_json = await response.json()
    assert response_json == {
        'code': 'experiments_400',
        'message': 'eda_tips_payments_registration_payment_400',
    }
