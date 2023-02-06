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
        # Кейс happy path.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingRefund (1) с delivery.
        # - BillingRefund (2) с assembly.
        # - BillingRefund (3) с tips.
        #
        # На выходе:
        # - PayoutOrder для (1).
        # - PayoutOrder для (2).
        # - PayoutOrder для (3).
        #
        # Проверяем, что:
        # - Для BillingRefund с delivery создается PayoutOrder с комиссией.(1)
        # - Для BillingRefund с assembly создается PayoutOrder с комиссией.(2)
        # - Для BillingRefund с tips создается PayoutOrder без комиссии. (3)
        # - Правильно считаются комиссии. (1) (2)
        # - Исходные события финализируются. (1) (2) (3)
        # - BillingRefund['payment_terminal_id'] пробрасывается
        #   в PayoutOrder['payment_terminal_id'] как есть.
        # - (При оплате картой) BillingRefund['payment_terminal_id'] маппится
        #   по конфигу EATS_BILLING_PROCESSOR_PAYMENT_TERMINAL_ID_MAP
        #   в правильный PayoutOrder['paysys_partner_id'].
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
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '100',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'cash',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'assembly',
                            'product_id': 'product_with_payment_only',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
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
                            'product_type': 'tips',
                            'product_id': 'product_with_payment_only',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
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
                        'BillingRefund/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'paysys_partner_id': 'sberbank_partner',
                            'transaction_type': 'refund',
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
                                'BillingRefund/711'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingRefund/712',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'payture',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'cash',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'subsidy',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '30',  # 100 * (10 + 10) / 100 + 10
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/712'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingRefund/713',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'sberbank_partner',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': 'sberbank_terminal',
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'subsidy',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/713'
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
                    doc_id=713, status='complete',
                ),
            ],
            # expected_business_rules_requests
            [
                # запрос для doc_id=711
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
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=10,
                    acquiring_commission=10,
                    fix_commission=10,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Happy path (with client_id).',
        ),
        # Кейс для BillingRefund без client_id.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingRefund с tips (1), без client_id.
        # - BillingRefund с delivery (2), без client_id.
        #
        # На выходе:
        # - PayoutOrder для (1).
        # - PayoutOrder для (2).
        #
        # Проверяем, что:
        # - За client_id всегда ходим в business-rules,
        #   даже если не нужна комиссия.
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
                            'amount': '1000',
                            'currency': 'RUB',
                            'client_id': None,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'tips',
                            'product_id': (
                                'product_with_payment_and_commission'
                            ),
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '1000',
                            'currency': 'RUB',
                            'client_id': None,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'delivery',
                            'product_id': 'product_with_payment_only',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
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
                        'BillingRefund/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': 'best_client',
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '1000',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/711'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingRefund/712',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': 'best_client',
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'subsidy',
                            'value_amount': '1000',
                            'currency': 'RUB',
                            'commission': '200',  # 1000 * (10 + 5) / 100 + 50
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/712'
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
                        'product_type': 'tips',
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
                helpers.make_business_rules_response(
                    client_id='best_client',
                    commission=10,
                    acquiring_commission=5,
                    fix_commission=50,
                ),
                helpers.make_business_rules_response(
                    client_id='best_client',
                    commission=10,
                    acquiring_commission=5,
                    fix_commission=50,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Happy path (without client_id).',
        ),
        # Кейс с неизвестным payment_terminal_id.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingRefund с неизвестным payment_terminal_id.
        # - BillingRefund без payment_terminal_id.
        #
        # На выходе:
        # - PayoutOrder для (1).
        # - PayoutOrder для (2).
        #
        # Проверяем, что:
        # - Если такого payment_terminal_id нет в конфиге,
        #   то в 'paysys_partner_id' будет 'payture'.
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
                            'amount': '1000',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': 'unknown_terminal',
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'tips',
                            'product_id': (
                                'product_with_payment_and_commission'
                            ),
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '1000',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'delivery',
                            'product_id': 'product_with_payment_only',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
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
                        'BillingRefund/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'payture',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': 'unknown_terminal',
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '1000',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/711'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingRefund/712',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'payture',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'subsidy',
                            'value_amount': '1000',
                            'currency': 'RUB',
                            'commission': '200',  # 1000 * (10 + 5) / 100 + 50
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/712'
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
                    client_id='best_client',
                    commission=10,
                    acquiring_commission=5,
                    fix_commission=50,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Happy path (with unknown terminal id).',
        ),
        # Кейс с неизвестным продуктом.
        #
        # На входе:
        # - OrderCreated (retail).
        #   - BillingRefund с неизвестным product_id.
        #
        # STQ-таска падает.
        #
        # Проверяем, что:
        # - STQ падает, если нет нужного product_id в конфиге.
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
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'delivery',
                            'product_id': 'unknown_product',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                        },
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
            True,
            id='STQ fails for unknown product_id.',
        ),
        # Кейс с неправильно настроенным продуктом.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingRefund, с product_id, для которого
        #   в конфиге нет параметров для PayoutOrder.
        #
        # STQ-таска падает.
        #
        # Проверяем, что:
        # - STQ падает, если для product_id в конфиге
        #   нет параметров по PayoutOrder.
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
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'delivery',
                            'product_id': 'product_with_commission_only',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                        },
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
            True,
            id='STQ fails for product_id with no refund in config.',
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
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'assembly',
                            'product_id': 'assembly/retail/native',
                            'transaction_type': 'refund',
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
                        'BillingRefund/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'payture',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'picker_card',
                            'payment_terminal_id': None,
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '125',  # 500 * (10 + 5) / 100 + 50
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/711'
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
                    acquiring_commission=5,
                    fix_commission=50,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Test custom payment type',
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
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'refund',
                            'flow_type': 'retail',
                            'payment_service': 'yandex_market',
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
                        'BillingRefund/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.START_PICKER_ORDER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yandex_market',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/711'
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
            None,
            # business_rules_response
            None,
            False,
            id='Test changing paysys_partner_id',
        ),
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
                        kind='BillingRefund',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'BYN',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PLACE_ID_AS_STRING,
                            'product_type': 'retail',
                            'product_id': 'product/native/native',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
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
                        event_at=consts.OTHER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingRefund/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'ecommpay',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'BYN',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/711'
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
            None,
            # business_rules_response
            None,
            False,
            id='Test changing paysys_partner_id',
        ),
    ],
)
async def test_biling_refund(
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
