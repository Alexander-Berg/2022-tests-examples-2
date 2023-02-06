from urllib import parse

import pytest

from . import utils


NOW = '2022-03-31T16:00:00+00:00'
ORDER_NR = '123456-123456'
PICKER_ID = '123456'
PAYMENT_LIMIT = 3000
SPENT_SUM = 2000
RECEIPT = {
    't': '20220331T160000',
    's': f'{SPENT_SUM}',
    'fn': '4891689280440300',
    'i': '19097',
    'fp': '313667667',
    'n': '1',
}
EDADEAL_RETRIES = 3


# pylint: disable=dangerous-default-value
def mock_edadeal_checkprovider(
        mockserver, status, receipt=RECEIPT, order_nr=ORDER_NR,
):
    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def mock_edadeal(request):
        if receipt:
            assert (
                dict(parse.parse_qsl(request.get_data().decode())) == receipt
            )
        if order_nr:
            assert request.headers['X-Correlation-Id'] == ORDER_NR
        return mockserver.make_response(status=status)

    return mock_edadeal


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'handle',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/receipt', id='client handler',
        ),
        pytest.param('/api/v1/order/receipt', id='admin handler'),
    ],
)
async def test_add_failed_receipt(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        get_failed_receipts,
        handle,
):
    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            return mockserver.make_response(
                json={'amount': PAYMENT_LIMIT - SPENT_SUM}, status=200,
            )
        return mockserver.make_response(
            json={'order_id': ORDER_NR}, status=200,
        )

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    create_order(
        eats_id=ORDER_NR,
        payment_limit=PAYMENT_LIMIT,
        picker_id=PICKER_ID,
        state='picked_up',
    )

    mock_edadeal = mock_edadeal_checkprovider(mockserver, 500)
    response = await taxi_eats_picker_orders.post(
        handle,
        params={'eats_id': ORDER_NR},
        json=RECEIPT,
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 200
    assert mock_edadeal.times_called / EDADEAL_RETRIES == 1

    failed_receipts = get_failed_receipts()
    assert len(failed_receipts) == 1
    del failed_receipts[0]['updated_at']
    assert failed_receipts[0] == {
        'id': 1,
        'order_nr': ORDER_NR,
        'receipt': RECEIPT,
        'retry_cnt': 0,
    }


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'handle',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/receipt', id='client handler',
        ),
        pytest.param('/api/v1/order/receipt', id='admin handler'),
    ],
)
async def test_update_failed_receipt(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        add_failed_receipt,
        get_failed_receipts,
        handle,
):
    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            return mockserver.make_response(
                json={'amount': PAYMENT_LIMIT - SPENT_SUM}, status=200,
            )
        return mockserver.make_response(
            json={'order_id': ORDER_NR}, status=200,
        )

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    receipt = RECEIPT
    create_order(
        eats_id=ORDER_NR,
        payment_limit=PAYMENT_LIMIT,
        picker_id=PICKER_ID,
        state='picked_up',
    )
    add_failed_receipt(
        {'order_nr': ORDER_NR, 'receipt': receipt, 'retry_cnt': 42},
    )

    receipt['t'] = '20220331T160001'  # change the receipt in any way
    mock_edadeal = mock_edadeal_checkprovider(mockserver, 500, receipt)

    response = await taxi_eats_picker_orders.post(
        handle,
        params={'eats_id': ORDER_NR},
        json=receipt,
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status == 200
    assert mock_edadeal.times_called / EDADEAL_RETRIES == 1

    failed_receipts = get_failed_receipts()
    assert len(failed_receipts) == 1
    del failed_receipts[0]['updated_at']
    assert failed_receipts[0] == {
        'id': 1,
        'order_nr': ORDER_NR,
        'receipt': receipt,
        'retry_cnt': 0,
    }


@pytest.mark.now(NOW)
async def test_retry_failed_receipt(
        taxi_eats_picker_orders,
        mockserver,
        add_failed_receipt,
        get_failed_receipts,
):
    add_failed_receipt(
        {'order_nr': ORDER_NR, 'receipt': RECEIPT, 'retry_cnt': 0},
    )

    mock_edadeal = mock_edadeal_checkprovider(mockserver, 200)

    await taxi_eats_picker_orders.run_distlock_task('failed-receipts-uploader')
    assert mock_edadeal.times_called == 1
    assert not get_failed_receipts()


@pytest.mark.now(NOW)
async def test_reschedule_failed_receipt(
        taxi_eats_picker_orders,
        mockserver,
        add_failed_receipt,
        get_failed_receipts,
):
    add_failed_receipt(
        {'order_nr': ORDER_NR, 'receipt': RECEIPT, 'retry_cnt': 0},
    )

    mock_edadeal = mock_edadeal_checkprovider(mockserver, 500)

    await taxi_eats_picker_orders.run_distlock_task('failed-receipts-uploader')
    assert mock_edadeal.times_called / EDADEAL_RETRIES == 1
    failed_receipts = get_failed_receipts()
    assert len(failed_receipts) == 1
    del failed_receipts[0]['updated_at']
    assert failed_receipts[0] == {
        'id': 1,
        'order_nr': ORDER_NR,
        'receipt': RECEIPT,
        'retry_cnt': 1,
    }


@pytest.mark.now(NOW)
async def test_failed_receipt_metrics(
        taxi_eats_picker_orders,
        taxi_eats_picker_orders_monitor,
        mockserver,
        add_failed_receipt,
        get_failed_receipts,
):
    mock_edadeal_checkprovider(mockserver, 500, None, None)

    for i in range(1, 10):
        add_failed_receipt(
            {
                'order_nr': f'{ORDER_NR}-{i}',
                'receipt': RECEIPT,
                'retry_cnt': 0,
            },
        )

        await taxi_eats_picker_orders.run_distlock_task(
            'failed-receipts-uploader',
        )
        assert (
            await taxi_eats_picker_orders_monitor.get_metric(
                'current-number-of-failed-receipts',
            )
            == i
        )
        assert len(get_failed_receipts()) == i
