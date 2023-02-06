import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.config(
    EATS_ORDERS_BILLING_DISTLOCK_SETTINGS={
        'namespace_name': 'eats-orders-billing',
        'acquire_interval_ms': 100,
        'prolong_interval_ms': 100,
        'lock_ttl_ms': 1000,
        'forced_stop_margin_ms': 500,
        'wait_until_lock_is_free': True,
        'whole_task_timeout_sec': 1,
    },
)
@pytest.mark.parametrize(
    'input_stq_args,'
    'expected_search_request,'
    'search_sleep_and_wait_cancellation,'
    'search_response,'
    'expected_input_stq_fail',
    [
        # Happy path.
        # Таска под дистлоком завершается успешно => stq-таска тоже.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_sleep_and_wait_cancellation
            False,
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[helpers.make_order_created_doc()],
            ),
            # expected_input_stq_fail
            False,
            id='Task succeeded.',
        ),
        # Таска под дистлоком фейлится => stq-таска фейлится.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_sleep_and_wait_cancellation
            False,
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            # Отсутствуют ожидаемые поля в событии
                        },
                    ),
                ],
            ),
            # expected_input_stq_fail
            True,
            id='Task failed.',
        ),
        # Таска под дистлоком отменяется по таймауту => stq-таска фейлится.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_sleep_and_wait_cancellation
            True,
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[helpers.make_order_created_doc()],
            ),
            # expected_input_stq_fail
            True,
            id='Task timed out.',
        ),
    ],
)
async def test_distlock(
        stq_runner,
        mock_storage_search,
        input_stq_args,
        expected_search_request,
        search_sleep_and_wait_cancellation,
        search_response,
        expected_input_stq_fail,
):
    storage_search = mock_storage_search(
        expected_request=expected_search_request,
        sleep_and_wait_cancellation=search_sleep_and_wait_cancellation,
        response=search_response,
    )

    await stq_runner.eats_orders_billing_process_billing_events.call(
        task_id='test_input_task',
        kwargs=input_stq_args,
        expect_fail=expected_input_stq_fail,
    )

    assert storage_search.times_called == 1
