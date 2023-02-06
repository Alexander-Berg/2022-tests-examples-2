# pylint: disable=invalid-name
# pylint: disable=W0601
import typing

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as test_http

from test_eats_tips_payments import conftest

ORDER_ID_1 = '5e65dc9f-f9f3-4306-9476-cb2691e1af56'
ORDER_ID_2 = '2e776108-3d51-4c8e-951d-4237015f3a41'


def _format_request_params(*, order_id_b2p='437', recipient_id='partner_id_1'):
    return {
        'id': order_id_b2p,
        'recipient_id': recipient_id,
        'reference': '0',  # make no sense
    }


def _format_headers(*, yandex_login: str = '123'):
    return {'X-Yandex-Login': yandex_login}


def _format_expected_response(order_id_str: str = ORDER_ID_1):
    return {'order_id_str': order_id_str, 'plus_amount': 10, 'has_plus': True}


def make_pytest_param(
        *,
        id,  # pylint: disable=redefined-builtin, invalid-name
        params: typing.Any = conftest.SENTINEL,
        request_headers: typing.Any = conftest.SENTINEL,
        expected_status: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
        b2p_complete_response: typing.Any = conftest.SENTINEL,
        b2p_complete_times_called: typing.Any = conftest.SENTINEL,
        expected_order_status: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(params, _format_request_params()),
        conftest.value_or_default(request_headers, _format_headers()),
        conftest.value_or_default(expected_status, 200),
        conftest.value_or_default(
            expected_response, _format_expected_response(),
        ),
        conftest.value_or_default(
            b2p_complete_response, 'b2p_complete_response.xml',
        ),
        conftest.value_or_default(b2p_complete_times_called, 1),
        conftest.value_or_default(expected_order_status, 'COMPLETED'),
        id=id,
    )


@pytest.mark.parametrize(
    'params,'
    'request_headers,'
    'expected_status,'
    'expected_response,'
    'b2p_complete_response,'
    'b2p_complete_times_called,'
    'expected_order_status,',
    (
        make_pytest_param(id='success'),
        make_pytest_param(
            id='try to complete already completed',
            params=_format_request_params(order_id_b2p='438'),
            b2p_complete_times_called=0,
            expected_response=_format_expected_response(ORDER_ID_2),
        ),
        make_pytest_param(
            id='b2p error response',
            b2p_complete_response='b2p_complete_response_error.xml',
            b2p_complete_times_called=1,
            expected_status=200,
            expected_order_status='COMPLETE_FAILED',
        ),
        make_pytest_param(
            id='b2p error response for completed order',
            params=_format_request_params(order_id_b2p='438'),
            b2p_complete_response='b2p_complete_response_error.xml',
            b2p_complete_times_called=0,
            expected_status=200,
            expected_response=_format_expected_response(ORDER_ID_2),
            expected_order_status='COMPLETED',
        ),
        make_pytest_param(
            id='b2p error response (operation rejected)',
            b2p_complete_response='b2p_complete_response_rejected.xml',
            b2p_complete_times_called=1,
            expected_status=200,
            expected_order_status='COMPLETE_FAILED',
        ),
    ),
)
async def test_complete_payment(
        taxi_eats_tips_payments_web,
        web_context,
        mock_best2pay,
        stq,
        pgsql,
        load,
        # params:
        params,
        request_headers,
        expected_status,
        expected_response,
        b2p_complete_response,
        b2p_complete_times_called,
        expected_order_status,
):
    @mock_best2pay('/webapi/b2puser/Complete')
    async def _mock_b2p_complete(request: test_http.Request):
        assert request.form['id'] == '437'
        return web.Response(
            status=200,
            content_type='text/html',
            body=load(b2p_complete_response),
        )

    response = await taxi_eats_tips_payments_web.post(
        '/v1/payments/complete', params=params, headers=request_headers,
    )
    assert response.status == expected_status
    response_json = await response.json()
    if expected_response is not None:
        assert response_json == expected_response
    assert _mock_b2p_complete.times_called == b2p_complete_times_called
    with pgsql['eats_tips_payments'].dict_cursor() as cursor:
        cursor.execute(
            f'select * from eats_tips_payments.orders '
            f'where order_id_b2p = %s;',
            (params['id'],),
        )
        order = cursor.fetchall()[-1]
    assert order['status'] == expected_order_status

    success_push = web_context.config.EATS_TIPS_PAYMENTS_PUSH_TEMPLATES
    if order['status'] == 'COMPLETED' and b2p_complete_times_called != 0:
        assert stq.eats_tips_partners_send_push.times_called == 1
        conftest.check_task_queued(
            stq,
            stq.eats_tips_partners_send_push,
            {
                'text': success_push['text'].format(
                    amount=order['recipient_amount'],
                ),
                'partner_id': order['recipient_id'],
                'title': success_push['title'],
                'intent': 'payment',
            },
        )


async def test_complete_payment_race_condition(
        taxi_eats_tips_payments_web,
        web_context,
        mock_best2pay,
        pgsql,
        load,
        testpoint,
):
    request_params = _format_request_params()
    request_headers = _format_headers()
    b2p_complete_response = 'b2p_complete_response.xml'
    is_first_call = True

    @mock_best2pay('/webapi/b2puser/Complete')
    async def _mock_b2p_complete(request: test_http.Request):
        return web.Response(
            status=200,
            content_type='text/html',
            body=load(b2p_complete_response),
        )

    async def fetch_order_status(response) -> str:
        with pgsql['eats_tips_payments'].dict_cursor() as cursor:
            cursor.execute(
                f'select * from eats_tips_payments.orders where id = %s;',
                ((await response.json())['order_id_str'],),
            )
            order = cursor.fetchall()[-1]
        return order['status']

    @testpoint('fetch_and_complete_order')
    async def fetch_and_complete_order(data):
        nonlocal is_first_call
        if not is_first_call:
            return
        is_first_call = False
        # выполнение второго запроса во время выполнения первого -
        # второй запрос переводит заказ в статус COMPLETE_PENDING и завершает
        # платёж, первый же запрос по факту уже ничего не делает
        response = await taxi_eats_tips_payments_web.post(
            '/v1/payments/complete',
            params=request_params,
            headers=request_headers,
        )
        assert response.status == 200
        # после завершения второй запрос высталяет заказу статус COMPLETED
        assert await fetch_order_status(response) == 'COMPLETED'

    response = await taxi_eats_tips_payments_web.post(
        '/v1/payments/complete',
        params=request_params,
        headers=request_headers,
    )
    assert fetch_and_complete_order.times_called == 2
    # всего один запрос в B2P, выполненный вторым запросом
    assert _mock_b2p_complete.times_called == 1
    assert response.status == 200
    assert await fetch_order_status(response) == 'COMPLETED'


def _format_blocking_settings(card_pan_count_threshold=3):
    return {
        'amount_threshold': 3000,
        'amount_threshold_whitelist': 10000,
        'card_pan_count_threshold': card_pan_count_threshold,
        'enabled': True,
        'order_count_threshold': 1,
        'period_hours': 24,
    }


def make_pytest_param_block_recipient(
        *,
        id,  # pylint: disable=redefined-builtin, invalid-name
        params: typing.Any = conftest.SENTINEL,
        expected_blocked_recipient_ids: typing.Any = conftest.SENTINEL,
        expected_reason: typing.Any = conftest.SENTINEL,
        blocking_settings: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(params, _format_request_params()),
        conftest.value_or_default(expected_blocked_recipient_ids, set()),
        conftest.value_or_default(expected_reason, ''),
        id=id,
        marks=pytest.mark.config(
            EATS_TIPS_PAYMENTS_BLOCKING_SETTINGS=conftest.value_or_default(
                blocking_settings, _format_blocking_settings(),
            ),
        ),
    )


@pytest.mark.parametrize(
    'params, expected_blocked_recipient_ids, expected_reason',
    (
        make_pytest_param_block_recipient(id='no blocking'),
        make_pytest_param_block_recipient(
            blocking_settings=_format_blocking_settings(
                card_pan_count_threshold=2,
            ),
            expected_blocked_recipient_ids={
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000002',
            },
            expected_reason=(
                'check for blocking: order count for card pan '
                '676531******0129 is 2 and exceeds the threshold'
            ),
            id='blocking by card pan',
        ),
        make_pytest_param_block_recipient(
            params=_format_request_params(order_id_b2p='439'),
            expected_blocked_recipient_ids={
                '00000000-0000-0000-0000-000000000002',
            },
            expected_reason=(
                'check for blocking: order count for recipient '
                '00000000-0000-0000-0000-000000000002 is 1 and '
                'exceeds the threshold'
            ),
            id='blocking by order count',
        ),
        make_pytest_param_block_recipient(
            params=_format_request_params(order_id_b2p='442'),
            expected_blocked_recipient_ids=set(),
            id='trying to block vip partner',
        ),
    ),
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_complete_payment_block_recipient(
        taxi_eats_tips_payments_web,
        web_context,
        mock_best2pay,
        mock_uantifraud,
        mock_eats_tips_partners,
        pgsql,
        mysql,
        load,
        testpoint,
        # params:
        params,
        expected_blocked_recipient_ids,
        expected_reason,
):
    global blocked_partners
    blocked_partners = set()

    @mock_eats_tips_partners('/v1/partner/block')
    async def _mock_block_user(request):
        global blocked_partners
        blocked_partners.add(request.json['partner_id'])
        assert request.json['partner_id'] in expected_blocked_recipient_ids
        assert request.json['reason'] == expected_reason
        return web.json_response()

    @mock_best2pay('/webapi/b2puser/Complete')
    async def _mock_b2p_complete(request: test_http.Request):
        return web.Response(
            status=200,
            content_type='text/html',
            body=load('b2p_complete_response.xml'),
        )

    @mock_uantifraud('/v1/tips/deposit')
    async def _mock_tips_check(request: test_http.Request):
        return web.json_response({'status': 'allow'}, status=200)

    @mock_eats_tips_partners('/v1/partner')
    async def _mock_get_partner(request):
        partner_id = str(request.query['partner_id'])
        return web.json_response(
            {
                'id': partner_id,
                'mysql_id': '0',
                'b2p_id': '0',
                'display_name': '',
                'full_name': '',
                'phone_id': '',
                'saving_up_for': '',
                'registration_date': '2000-01-22T22:22:00+00:00',
                'date_first_pay': '2000-01-22T22:22:00+00:00',
                'is_vip': True,
                'best2pay_blocked': False,
                'is_admin_reg': False,
                'is_free_procent': False,
                'trans_guest': False,
                'trans_guest_block': False,
            },
        )

    @testpoint('block_recipients_if_needed')
    async def block_recipients_if_needed(data):
        pass

    response = await taxi_eats_tips_payments_web.post(
        '/v1/payments/complete', params=params, headers=_format_headers(),
    )
    assert response.status == 200
    await block_recipients_if_needed.wait_call()
    assert blocked_partners == expected_blocked_recipient_ids
