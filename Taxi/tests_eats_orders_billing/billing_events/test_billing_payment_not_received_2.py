# pylint: disable=too-many-lines

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
        # BillingPaymentNotReceived, созаданный сервисом долгов
        # и BillingPayment с разными external_payment_id.
        #
        # На входе:
        # - OrderCreated.
        # - BillingPaymentNotReceived с external_payment_id
        # debt-service
        # - BillingPayment c external_payment_id (2).
        #
        # На выходе:
        # - PayoutOrder для BillingPaymentNotReceived
        # - PayoutOrder для сторнирования BillingPaymentNotReceived
        # - PayoutOrder для платежа
        #
        # Проверяем, что:
        # - Созданный для BillingPaymentNotReceived платеж сторнируется,
        #   если в нем external_payment_id содержит debt-service
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
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'product/native/native',
                                    'product_type': 'product',
                                    'value_amount': '100',
                                },
                            ],
                            'external_payment_id': (
                                f'debt-service/no-payment/{consts.ORDER_NR}'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '100',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'product',
                            'product_id': 'product/native/native',
                            'transaction_type': 'payment',
                            'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
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
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/2147995772/'
                        'product/native/native/payment',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'payment_not_received',
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/2147995772/'
                                'product/native/native/payment'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/2147995772/'
                        'product/native/native/refund',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'payment_not_received',
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/2147995772/'
                                'product/native/native/refund'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPayment/712',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/712'
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
                helpers.make_storage_finish_request(
                    doc_id=712, status='complete',
                ),
            ],
            # expected_business_rules_requests
            [
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
                # doc_id=2147995772
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Revert debt-service compensation if payment received',
        ),
    ],
)
async def test_billing_payment_not_received(
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
