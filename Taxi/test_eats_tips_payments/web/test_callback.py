import typing

from aiohttp import web
import pytest

from test_eats_tips_payments import conftest


def make_pytest_param(
        *,
        id,  # pylint: disable=redefined-builtin, invalid-name
        order_id_b2p: typing.Any = conftest.SENTINEL,
        request_filename: typing.Any = conftest.SENTINEL,
        b2p_complete_response_filename: typing.Any = conftest.SENTINEL,
        b2p_complete_times_called: typing.Any = conftest.SENTINEL,
        expected_order_status: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(order_id_b2p, '101'),
        conftest.value_or_default(
            request_filename, 'callback_request_completed.xml',
        ),
        conftest.value_or_default(
            b2p_complete_response_filename, 'b2p_complete_response.xml',
        ),
        conftest.value_or_default(b2p_complete_times_called, 0),
        conftest.value_or_default(expected_order_status, 'COMPLETED'),
        id=id,
    )


@pytest.mark.parametrize(
    (
        'order_id_b2p',
        'request_filename',
        'b2p_complete_response_filename',
        'b2p_complete_times_called',
        'expected_order_status',
    ),
    [
        make_pytest_param(id='completed callback'),
        make_pytest_param(
            id='authorized callback',
            request_filename='callback_request_authorized.xml',
            b2p_complete_times_called=1,
        ),
        make_pytest_param(
            id='authorized callback for compliting order',
            order_id_b2p='102',
            request_filename='callback_request_authorized.xml',
            b2p_complete_times_called=0,
            # статус не изменяется, так как выше, чем статус AUTHORIZED
            expected_order_status='COMPLETE_PENDING',
        ),
        make_pytest_param(
            id='completed callback',
            order_id_b2p='102',
            request_filename='callback_request_completed.xml',
            b2p_complete_times_called=0,
            expected_order_status='COMPLETED',
        ),
        make_pytest_param(
            id='completed callback for completed order',
            order_id_b2p='103',
            request_filename='callback_request_completed.xml',
            b2p_complete_times_called=0,
            # текущий статус уже COMPLETED
            expected_order_status='COMPLETED',
        ),
        make_pytest_param(
            id='complete rejected callback',
            order_id_b2p='101',
            request_filename='callback_request_complete_rejected.xml',
            b2p_complete_times_called=0,
            expected_order_status='COMPLETE_FAILED',
        ),
        make_pytest_param(
            id='complete failed after authorized callback',
            order_id_b2p='101',
            request_filename='callback_request_authorized.xml',
            b2p_complete_response_filename='b2p_response_error.xml',
            b2p_complete_times_called=1,
            expected_order_status='COMPLETE_FAILED',
        ),
    ],
)
async def test_order_callback_handler(
        taxi_eats_tips_payments_web,
        pgsql,
        load,
        mock_best2pay,
        # params:
        order_id_b2p,
        request_filename,
        b2p_complete_response_filename,
        b2p_complete_times_called,
        expected_order_status,
):
    """
    Тестирование callback'а для платежей, процессинг которых полностью
    происходит в сервисе eats-tips-payments
    """

    @mock_best2pay('/webapi/b2puser/Complete')
    async def _mock_b2p_complete(request):
        return web.Response(
            status=200,
            content_type='text/html',
            body=load(b2p_complete_response_filename),
        )

    response = await taxi_eats_tips_payments_web.post(
        '/v1/payments/callback',
        data=load(request_filename).format(order_id_b2p=order_id_b2p),
        headers={'content-type': 'application/xml'},
    )
    assert response.status == 200
    assert _mock_b2p_complete.times_called == b2p_complete_times_called
    with pgsql['eats_tips_payments'].dict_cursor() as cursor:
        cursor.execute(
            f'select * from eats_tips_payments.orders '
            f'where order_id_b2p = %s;',
            (order_id_b2p,),
        )
        order = cursor.fetchall()[-1]
    assert order['status'] == expected_order_status
    if expected_order_status == 'COMPLETED':
        assert order['card_pan'] == '676531******0129'
