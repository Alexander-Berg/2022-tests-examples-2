import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


# С этой датой еще не обрабатываются
DISABLED_ORDER_DATE = '2020-11-30T23:59:59+03:00'
DISABLED_ORDER_DATE_FOR_TLOG = '2021-11-30T23:59:59+03:00'
# С этой датой уже обрабатываются
ENABLED_ORDER_DATE = '2020-12-01T00:00:00+03:00'


@pytest.mark.config(
    EDA_CORE_SWITCH_TO_EATS_BILLING_PROCESSOR={
        # >= чем ENABLED_ORDER_DATE
        'retail_billing_start_date': '2020-12-01T00:00:00+03:00',
        'retail_billing_tlog_start_date': '2021-09-01T00:00:00+03:00',
    },
)
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
        # Кейс с BillingPayment.
        #
        # На входе:
        # - OrderCreated (retail), старая дата.
        # - BillingPayment.
        #
        # На выходе ничего.
        #
        # Проверяем, что:
        # - События BillingPayment для старых заказов игнорируются.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='retail', created_at=DISABLED_ORDER_DATE,
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
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
            id='BillingPayment for retail ignored.',
        ),
        # Кейс с BillingPayment.
        #
        # На входе:
        # - OrderCreated (retail), новая дата.
        # - BillingPayment.
        #
        # На выходе ничего.
        #
        # Проверяем, что:
        # - События BillingPayment для новых заказов игнорируются.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='retail',
                        created_at=DISABLED_ORDER_DATE_FOR_TLOG,
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={},
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=712, status='complete',
                ),
            ],
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='BillingPayment for retail ignored because we moving on tlog',
        ),
        # Кейс с BillingPayment.
        #
        # На входе:
        # - OrderCreated (retail), новая дата.
        # - BillingPayment.
        #
        # На выходе ничего.
        #
        # Проверяем, что:
        # - События BillingPayment для новых заказов обрабатываются.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='retail', created_at=ENABLED_ORDER_DATE,
                    ),
                    helpers.make_billing_doc(
                        doc_id=2147995772,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': 'sberbank_terminal',
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'delivery',
                            'flow_type': 'native',
                            'product_id': (
                                'product_with_payment_and_commission'
                            ),
                            'transaction_type': 'payment',
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPayment/2147995772',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'paysys_partner_id': 'sberbank_partner',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': 'sberbank_terminal',
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '125',  # 500 * (10 + 5) / 100 + 50
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/2147995772'
                            ),
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=2147995772, status='complete',
                ),
            ],
            # expected_business_rules_requests
            [
                # запрос для doc_id=712
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.START_PICKER_ORDER_DATE_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'delivery',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=5,
                    fix_commission=50,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='BillingPayment for retail processed.',
        ),
    ],
)
async def test_retail_not_processed(
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
