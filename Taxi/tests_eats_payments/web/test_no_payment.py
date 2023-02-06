import datetime as dt

import pytest

URL = 'v1/orders/close'

NOW = '2020-08-12T07:20:00+00:00'
CHECK_AFTER_SECONDS = 60

BASE_HEADERS = {'X-Yandex-Uid': '100500'}
BASE_BODY = {'id': 'test_order'}


@pytest.mark.now(NOW)
@pytest.mark.config(
    EATS_PAYMENTS_CHECK_NO_PAYMENT={
        'check_no_payment_after_seconds': CHECK_AFTER_SECONDS,
    },
)
@pytest.mark.parametrize(
    'close_call_count, stq_task_eta',
    [
        pytest.param(
            # close_call_count
            1,
            # stq_task_eta
            dt.datetime.fromisoformat(NOW).replace(tzinfo=None)
            + dt.timedelta(seconds=CHECK_AFTER_SECONDS),
            id='Single clear',
        ),
    ],
)
async def test_scheduling(
        upsert_order,
        taxi_eats_payments,
        check_no_payment_callback,
        close_call_count,
        stq_task_eta,
        mockserver,
        mock_retrieve_invoice_retrieve,
):
    invoice_close_request_body = {**BASE_BODY, **{'clear_eta': NOW}}
    response_status = 200
    response_body = {}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_close_invoice_handler(request):
        assert request.json == invoice_close_request_body
        return mockserver.make_response(**{'status': 200, 'json': {}})

    extra = {'personal_phone_id': '123456'}

    mock_retrieve_invoice_retrieve(**extra)

    body = BASE_BODY
    headers = BASE_HEADERS
    for _ in range(close_call_count):
        upsert_order('test_order')
        response = await taxi_eats_payments.post(
            URL, json=body, headers=headers,
        )
        assert response.status == response_status
        assert response.json() == response_body

    assert _transactions_close_invoice_handler.times_called == close_call_count

    check_no_payment_callback(
        task_id=f'test_order',
        invoice_id='test_order',
        order_id='test_order',
        times_called=close_call_count,
        eta=stq_task_eta,
    )
