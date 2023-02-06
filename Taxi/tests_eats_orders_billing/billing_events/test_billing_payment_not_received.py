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
        # Happy path с продуктами.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingPaymentNotReceived с retail, delivery, assembly, product.
        # На выходе:
        # - PayoutOrder для retail.
        # - PayoutOrder для product.
        #
        # Проверяем, что:
        # - PayoutOrder создается только для товаров ('retail', 'product').
        # - BillingPaymentNotReceived финализируется.
        # - 'paysys_partner_id' = 'yaeda'
        # - 'payment_type' = 'payment_not_received'
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
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/2147995772/'
                        'retail/retail/native/payment',
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
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/2147995772/'
                                'retail/retail/native/payment'
                            ),
                        },
                    ),
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
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '400',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/2147995772/'
                                'product/native/native/payment'
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
                    acquiring_commission=10,
                    fix_commission=10,
                ),
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Happy path with products.',
        ),
        # Happy path с продуктами.
        #
        # На входе:
        # - OrderCreated (marketplace).
        # - BillingPaymentNotReceived с delivery, product.
        # На выходе:
        # - PayoutOrder для delivery.
        # - PayoutOrder для product.
        #
        # Проверяем, что:
        # - PayoutOrder создается только для товаров ('delivery', 'product').
        # - BillingPaymentNotReceived финализируется.
        # - 'paysys_partner_id' = 'yaeda'
        # - 'payment_type' = 'payment_not_received'
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(order_type='native'),
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPaymentNotReceived',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'native',
                            'order_type': 'marketplace',
                            'transaction_date': consts.OTHER_DATE,
                            'payment_not_received_at': consts.OTHER_DATE,
                            'courier_id': None,
                            'picker_id': None,
                            'place_id': str(consts.PLACE_ID),
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': None,
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': (
                                        'delivery/native/marketplace'
                                    ),
                                    'product_type': 'delivery',
                                    'value_amount': '200',
                                },
                                {
                                    'product_id': 'product/native/marketplace',
                                    'product_type': 'product',
                                    'value_amount': '400',
                                },
                            ],
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
                        'BillingPaymentNotReceived/711/'
                        'delivery/native/marketplace/payment',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 4168,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'payment_not_received',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'mp_delivery',
                            'value_amount': '200',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/711/'
                                'delivery/native/marketplace/payment'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/711/'
                        'product/native/marketplace/payment',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 4168,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'payment_not_received',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '400',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/711/'
                                'product/native/marketplace/payment'
                            ),
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=711, status='complete',
                ),
            ],
            # expected_business_rules_requests
            [
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.OTHER_DATE_UTC,
                    counteragent_type='place',
                    counteragent_details={
                        'place_id': str(consts.PLACE_ID),
                        'commission_type': 'delivery',
                    },
                ),
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.OTHER_DATE_UTC,
                    counteragent_type='place',
                    counteragent_details={
                        'place_id': str(consts.PLACE_ID),
                        'commission_type': 'delivery',
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
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Happy path with products and marketplace delivery',
        ),
        # Happy path без продуктов.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingPaymentNotReceived без продуктов.
        # На выходе ничего.
        #
        # Проверяем, что:
        # - Пустой BillingPaymentNotReceived нормально обрабатывается
        #   без создания поручений.
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
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'currency': 'RUB',
                            'products': [],
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
            id='Happy path without products.',
        ),
        # Кейс с неизвестным продуктом.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingPaymentNotReceived с продуктом 'unknown_product'.
        #
        # STQ-таска падает.
        #
        # Проверяем, что:
        # - STQ-таска падает, т.к. не нашли продукт в маппинг-конфиге.
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
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'unknown_product',
                                    'product_type': 'retail',
                                    'value_amount': '100',
                                },
                            ],
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
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
            True,
            id='Unknown product.',
        ),
        # Happy path с продуктами.
        #
        # На входе:
        # - OrderCreated.
        # - BillingPaymentNotReceived с product, retail
        #   (с external_payment_id).
        # - BillingPayment с product (с external_payment_id).
        #
        # На выходе:
        # - PayoutOrder для product (payment_not_received, payment).
        # - PayoutOrder для product (payment_not_received, refund).
        # - PayoutOrder для retail.
        # - PayoutOrder для product (payment).
        #
        # Проверяем, что:
        # - Созданный для BillingPaymentNotReceived платеж сторнируется,
        #   если есть BillingPayment с такими же
        #   продуктом и external_payment_id.
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
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'product/native/native',
                                    'product_type': 'product',
                                    'value_amount': '100',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'product_type': 'retail',
                                    'value_amount': '200',
                                },
                            ],
                            'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
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
                        'BillingPaymentNotReceived/711/'
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
                                'BillingPaymentNotReceived/711/'
                                'product/native/native/payment'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/711/'
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
                                'BillingPaymentNotReceived/711/'
                                'product/native/native/refund'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/711/'
                        'retail/retail/native/payment',
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
                            'value_amount': '200',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPaymentNotReceived/711/'
                                'retail/retail/native/payment'
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
                    doc_id=711, status='complete',
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
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Reverse order if same payment exists.',
        ),
        # BillingPaymentNotReceived и BillingPayment
        # с разными external_payment_id.
        #
        # На входе:
        # - OrderCreated.
        # - BillingPaymentNotReceived без external_payment_id (1).
        # - BillingPayment c external_payment_id (2).
        # - BillingPaymentNotReceived с одним external_payment_id (3).
        # - BillingPayment c другим external_payment_id (4).
        #
        # На выходе:
        # - PayoutOrder для (1).
        # - PayoutOrder для (2).
        # - PayoutOrder для (3).
        # - PayoutOrder для (4).
        #
        # Проверяем, что:
        # - Созданный для BillingPaymentNotReceived платеж не сторнируется,
        #   если в нем нет external_payment_id или
        #   нет BillingPayment с таким же external_payment_id.
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
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'product/native/native',
                                    'product_type': 'product',
                                    'value_amount': '100',
                                },
                            ],
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
                    helpers.make_billing_doc(
                        doc_id=811,
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
                            'external_payment_id': 'different_payment_id_1',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=812,
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
                            'external_payment_id': 'different_payment_id_2',
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
                        'BillingPaymentNotReceived/711/'
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
                                'BillingPaymentNotReceived/711/'
                                'product/native/native/payment'
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
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPaymentNotReceived/811/'
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
                                'BillingPaymentNotReceived/811/'
                                'product/native/native/payment'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPayment/812',
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
                                'BillingPayment/812'
                            ),
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=711, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=712, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=811, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=812, status='complete',
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
                # doc_id=711
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
                # doc_id=811
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Dont reverse order if different payment exists.',
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
