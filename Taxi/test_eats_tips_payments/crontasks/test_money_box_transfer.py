import datetime

from aiohttp import web
import psycopg2.extras
import pytest
from submodules.testsuite.testsuite.utils import http

from taxi.util import dates

from eats_tips_payments.generated.cron import run_cron

NOW = datetime.datetime(2022, 1, 24, 14, 30, 15, tzinfo=datetime.timezone.utc)

ORDER_1 = {
    'updated_at': dates.localize(NOW).replace(
        tzinfo=None,
    ) - datetime.timedelta(minutes=5),
    'order_id_b2p': None,
    'idempotency_token': 'token1-00000000-0000-0000-1000-000000000001',
    'recipient_id': '00000000-0000-0000-1000-000000000001',
    'recipient_id_b2p': '00000000-0000-0000-1000-000000000001',
    'recipient_type': 'partner',
    'commission': 0,
    'amount': 100,
    'guest_amount': 100,
    'payment_type': 'b2p',
    'payer_type': 'MONEY_BOX',
    'payer_id': '00000000-0000-0000-0000-000000000001',
    'status': 'CREATED',
    'status_b2p': None,
    'money_box_period_id': '10000000-0000-0000-0000-000000000001',
}
ORDER_2 = {
    'updated_at': dates.localize(NOW).replace(
        tzinfo=None,
    ) - datetime.timedelta(minutes=5),
    'order_id_b2p': '42',
    'idempotency_token': 'token1-00000000-0000-0000-1000-000000000001',
    'recipient_id': '00000000-0000-0000-1000-000000000001',
    'recipient_id_b2p': '00000000-0000-0000-1000-000000000001',
    'recipient_type': 'partner',
    'commission': 0,
    'amount': 100,
    'guest_amount': 100,
    'payment_type': 'b2p',
    'payer_type': 'MONEY_BOX',
    'payer_id': '00000000-0000-0000-0000-000000000001',
    'status': 'REGISTERED',
    'status_b2p': 'REGISTERED',
    'money_box_period_id': '10000000-0000-0000-0000-000000000002',
}
ORDER_3 = {
    'updated_at': dates.localize(NOW).replace(
        tzinfo=None,
    ) - datetime.timedelta(minutes=5),
    'order_id_b2p': None,
    'idempotency_token': 'token1-00000000-0000-0000-1000-000000000001',
    'recipient_id': '00000000-0000-0000-1000-000000000001',
    'recipient_id_b2p': '00000000-0000-0000-1000-000000000001',
    'recipient_type': 'partner',
    'commission': 0,
    'amount': 100,
    'guest_amount': 100,
    'payment_type': 'b2p',
    'payer_type': 'MONEY_BOX',
    'payer_id': '00000000-0000-0000-0000-000000000001',
    'status': 'TO_RETRY',
    'status_b2p': None,
    'money_box_period_id': '10000000-0000-0000-0000-000000000003',
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.parametrize(
    (
        'db_order',
        'db_tries',
        'b2p_order_response',
        'b2p_register_response',
        'b2p_payout_response',
        'b2p_expected_amount',
        'expected_order',
        'expected_tries',
    ),
    (
        pytest.param(
            ORDER_1,
            None,
            None,
            'b2p_register_response.xml',
            'b2p_payout_response.xml',
            '10000',
            {'status': 'COMPLETED', 'status_b2p': 'COMPLETED'},
            None,
            id='success-full',
        ),
        pytest.param(
            ORDER_2,
            None,
            'b2p_order_response_not_found.xml',
            'b2p_register_response.xml',
            'b2p_payout_response.xml',
            '10000',
            {'status': 'COMPLETED', 'status_b2p': 'COMPLETED'},
            None,
            id='success-full-with-id',
        ),
        pytest.param(
            ORDER_2,
            None,
            'b2p_order_response_registered.xml',
            None,
            'b2p_payout_response.xml',
            None,
            {'status': 'COMPLETED', 'status_b2p': 'COMPLETED'},
            None,
            id='success-registered',
        ),
        pytest.param(
            ORDER_2,
            None,
            'b2p_order_response_completed.xml',
            None,
            None,
            None,
            {'status': 'COMPLETED', 'status_b2p': 'COMPLETED'},
            None,
            id='success-completed',
        ),
        pytest.param(
            ORDER_1,
            None,
            None,
            'b2p_register_response_error.xml',
            None,
            '10000',
            {'status': 'REGISTER_FAILED', 'status_b2p': None},
            {
                'tries': 1,
                'next_try': dates.localize(
                    NOW + datetime.timedelta(minutes=1),
                ),
            },
            id='retry-register',
        ),
        pytest.param(
            ORDER_3,
            {'tries': 9, 'next_try': NOW},
            None,
            'b2p_register_response_error.xml',
            None,
            '10000',
            {'status': 'FAILED', 'status_b2p': None},
            {'tries': 9, 'next_try': dates.localize(NOW)},
            id='fail-register',
        ),
    ),
)
@pytest.mark.skip('needs fix in EASYT-974')
async def test_money_box_transfer(
        pgsql,
        load,
        insert_row,
        mock_best2pay,
        db_order,
        db_tries,
        b2p_order_response,
        b2p_register_response,
        b2p_payout_response,
        b2p_expected_amount,
        expected_order,
        expected_tries,
):
    created_order_id = insert_row('orders', db_order)
    if db_tries:
        insert_row(
            'orders_retries',
            {**db_tries, 'order_id': created_order_id},
            'order_id',
        )

    @mock_best2pay('/webapi/Order')
    async def _mock_b2p_order(request: http.Request):
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load(b2p_order_response),
        )

    @mock_best2pay('/webapi/Register')
    async def _mock_b2p_register(request: http.Request):
        assert request.form['amount'] == b2p_expected_amount
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load(b2p_register_response),
        )

    @mock_best2pay('/webapi/b2puser/sd-services/SDPayOut')
    async def _mock_b2p_payout(request: http.Request):
        return web.Response(
            status=200,
            content_type='application/xml',
            body=load(b2p_payout_response),
        )

    await run_cron.main(
        ['eats_tips_payments.crontasks.retry_payments', '-t', '0'],
    )

    assert _mock_b2p_order.times_called == (
        1 if db_order['order_id_b2p'] else 0
    )
    assert _mock_b2p_register.times_called == (
        1 if b2p_register_response else 0
    )
    assert _mock_b2p_payout.times_called == (1 if b2p_payout_response else 0)

    with pgsql['eats_tips_payments'].cursor(
            cursor_factory=psycopg2.extras.RealDictCursor,
    ) as cursor:
        cursor.execute(
            f'SELECT {", ".join(expected_order.keys())} '
            f'FROM eats_tips_payments.orders '
            f'WHERE id = %s',
            (created_order_id,),
        )
        actual_order = cursor.fetchone()
        assert actual_order == expected_order

        if expected_tries:
            cursor.execute(
                f'SELECT {", ".join(expected_tries.keys())} '
                f'FROM eats_tips_payments.orders_retries WHERE order_id = %s',
                (created_order_id,),
            )
            actual_tries = cursor.fetchone()
            if actual_tries.get('next_try'):
                actual_tries['next_try'] = dates.localize(
                    actual_tries['next_try'],
                )
            assert actual_tries == expected_tries
