import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={'core_write_back_enabled': True},
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
                        doc_id=2147995772,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'badge_corporate',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'flow_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=2147995772, status='complete',
                ),
            ],
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='Test payment',
        ),
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
                        kind='BillingRefund',
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
                            'product_id': (
                                'product_with_payment_and_commission'
                            ),
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=711, status='complete',
                ),
            ],
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='Test refund',
        ),
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
                        kind='BillingPaymentNotReceived',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'payment_not_received_at': consts.OTHER_DATE,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': None,
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'product_type': 'retail',
                                    'value_amount': '100',
                                },
                                {
                                    'product_id': 'delivery/retail/native',
                                    'product_type': 'delivery',
                                    'value_amount': '200',
                                },
                                {
                                    'product_id': 'assembly/retail/native',
                                    'product_type': 'assembly',
                                    'value_amount': '300',
                                },
                                {
                                    'product_id': 'product/native/native',
                                    'product_type': 'product',
                                    'value_amount': '400',
                                },
                            ],
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=711, status='complete',
                ),
            ],
            # expected_business_rules_requests
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='Test payment not received',
        ),
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
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCancelled',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': (
                                consts.ORDER_CANCEL_ID_AS_STRING
                            ),
                            'is_payment_expected': True,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': consts.PLACE_ID_AS_STRING,
                            'currency': consts.CURRENCY,
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '1500',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '200',
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '300',
                                    'type': 'marketing_promocode',
                                    'product_type': 'retail',
                                },
                            ],
                            'amount_picker_paid': '2000',
                            'order_type': 'native',
                            'flow_type': 'retail',
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
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'marketing',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'marketing',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '200',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'marketing'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.START_PICKER_ORDER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCancelled/1/'
                        'retail/retail/native/'
                        'marketing_promocode',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'marketing_promocode',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '300',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCancelled/1/'
                                'retail/retail/native/'
                                'marketing_promocode'
                            ),
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [helpers.make_storage_finish_request(doc_id=1, status='complete')],
            # expected_business_rules_requests
            [
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.START_PICKER_ORDER_DATE_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'picker',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Test billing cancelled is processed',
        ),
    ],
)
async def test_billing_payment(
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
