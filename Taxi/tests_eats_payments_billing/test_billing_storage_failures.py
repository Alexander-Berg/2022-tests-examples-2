import pytest

from testsuite.utils import http

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'billing_storage_response_code, expect_fail',
    [(200, False), (400, True), (403, True), (500, True)],
)
async def test_billing_storage_responses(
        stq_runner,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        billing_storage_response_code,
        expect_fail,
):
    order_billing_data_mock = mock_order_billing_data(order_id=consts.ORDER_ID)

    billing_storage_mock = mock_eats_billing_storage(
        response_code=billing_storage_response_code,
    )
    mock_eats_billing_processor()

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task',
        kwargs=helpers.make_stq_kwargs(
            items=[helpers.make_stq_item(item_id='food', amount='2.00')],
        ),
        expect_fail=expect_fail,
    )

    assert order_billing_data_mock.times_called == 1
    assert billing_storage_mock.times_called > 0


@pytest.mark.parametrize('error', [http.TimeoutError, http.NetworkError])
async def test_billing_storage_errors(
        stq_runner,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        error,
):
    order_billing_data_mock = mock_order_billing_data(order_id=consts.ORDER_ID)

    billing_storage_mock = mock_eats_billing_storage(error=error)

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task',
        kwargs=helpers.make_stq_kwargs(
            items=[helpers.make_stq_item(item_id='food', amount='2.00')],
        ),
        expect_fail=True,
    )

    assert order_billing_data_mock.times_called == 1
    assert billing_storage_mock.times_called > 0
