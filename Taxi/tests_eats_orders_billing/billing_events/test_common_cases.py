import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args,'
    'expected_search_request,'
    'search_response,'
    'expected_store_request,'
    'expected_finish_requests,'
    'expected_business_rules_requests,'
    'business_rules_responses,'
    'expected_input_stq_fail',
    [
        # Не нашлось никаких событий.
        # Ничего не происходит.
        #
        # Проверяем, что отсутствие событий ни на что не влияет.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(billing_docs=[]),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='No events.',
        ),
        # На входе:
        #   - Всякие неизвестные события.
        # Ничего не происходит.
        #
        # Проверяем, что неизвестные события ни на что не влияют.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='SomethingHappened',
                        data={},
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='ThisHasNeverHappenedBeforeAndHereItIsAgain',
                        data={},
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='NatashaWakeUpWeDroppedEverything',
                        data={},
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='Unknown events.',
        ),
    ],
)
async def test_common_cases(
        stq_runner,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
):
    await helpers.billing_processing_test_func(
        stq_runner,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
    )


@pytest.mark.parametrize(
    'input_stq_args, expected_input_stq_fail',
    [
        pytest.param(
            # input_stq_args
            helpers.make_input_event_stq_args(
                consts.ORDER_NR, 'external_event_ref_value',
            ),
            # expected_input_stq_fail
            False,
        ),
    ],
)
async def test_billing_input_events(
        stq,
        stq_runner,
        select_billing_input_events,
        input_stq_args,
        expected_input_stq_fail,
):
    await helpers.billing_input_events_test_func(
        stq,
        stq_runner,
        select_billing_input_events,
        input_stq_args,
        expected_input_stq_fail,
    )
