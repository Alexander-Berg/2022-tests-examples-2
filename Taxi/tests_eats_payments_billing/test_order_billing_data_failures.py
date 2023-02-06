import pytest

from testsuite.utils import http

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'billing_data_response_code, expect_fail, '
    'billing_storage_times_called, eats_billing_processor_times_called,'
    'reschedule_called',
    [
        (200, False, 1, 1, 0),
        (400, True, 0, 0, 0),
        (403, True, 0, 0, 0),
        (425, False, 0, 0, 1),
        (500, True, 0, 0, 0),
    ],
)
async def test_order_billing_data_responses(
        stq_runner,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        mock_stq_reschedule,
        billing_data_response_code,
        expect_fail,
        billing_storage_times_called,
        eats_billing_processor_times_called,
        reschedule_called,
):
    order_billing_data_mock = mock_order_billing_data(
        order_id=consts.ORDER_ID, response_code=billing_data_response_code,
    )

    billing_storage_mock = mock_eats_billing_storage()
    stq_reschedule_mock = mock_stq_reschedule()
    eats_billing_processor_mock = mock_eats_billing_processor()

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task',
        kwargs=helpers.make_stq_kwargs(
            items=[helpers.make_stq_item(item_id='food', amount='2.00')],
        ),
        expect_fail=expect_fail,
    )

    assert order_billing_data_mock.times_called > 0
    assert billing_storage_mock.times_called == billing_storage_times_called
    assert (
        eats_billing_processor_mock.times_called
        == eats_billing_processor_times_called
    )
    assert stq_reschedule_mock.times_called == reschedule_called


@pytest.mark.parametrize('error', [http.TimeoutError, http.NetworkError])
async def test_order_billing_data_errors(
        stq_runner,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        error,
):
    order_billing_data_mock = mock_order_billing_data(
        order_id=consts.ORDER_ID, error=error,
    )

    billing_storage_mock = mock_eats_billing_storage()
    eats_billing_processor_mock = mock_eats_billing_processor()

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task',
        kwargs=helpers.make_stq_kwargs(
            items=[helpers.make_stq_item(item_id='food', amount='2.00')],
        ),
        expect_fail=True,
    )

    assert order_billing_data_mock.times_called > 0
    assert billing_storage_mock.times_called == 0
    assert eats_billing_processor_mock.times_called == 0
