import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


# С этой датой еще не обрабатываются
DISABLED_ORDER_DATE = '2020-11-30T23:59:59+03:00'
# С этой датой уже обрабатываются
ENABLED_ORDER_DATE = '2020-12-01T00:00:00+03:00'


@pytest.mark.config(
    EDA_CORE_SWITCH_TO_EATS_BILLING_PROCESSOR={
        # >= чем ENABLED_ORDER_DATE
        'filter_core_payments_start_date': '2020-12-01T00:00:00+03:00',
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
        # На входе:
        # - OrderCreated (native) со старой датой.
        # - BillingRefund (1) с native delivery.
        # - BillingRefund (2) с native assembly.
        # - BillingRefund (3) с native tips.
        #
        # На выходе:
        # - PayoutOrder для (1).
        # - PayoutOrder для (2).
        # - PayoutOrder для (3).
        #
        # Проверяем, что:
        # - Для native доставки, сборки, чаевых рефанды процессятся всегда.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='native', created_at=DISABLED_ORDER_DATE,
                    ),
                    helpers.make_billing_doc(
                        doc_id=2147995772,
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
                            'order_type': 'native',
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
                            'order_type': 'native',
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
                            'order_type': 'native',
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
                        'BillingRefund/2147995772',
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
                                'BillingRefund/2147995772'
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
                    doc_id=2147995772, status='complete',
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
                # запрос для doc_id=2147995772
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
            id='BillingRefund for native delivery/assembly/tips '
            'always processed.',
        ),
        # На входе:
        # - OrderCreated (native) со старой датой.
        # - BillingRefund (1) с product.
        # - BillingRefund (2) с retail.
        # - BillingRefund (3) с restaurant_tips.
        #
        # На выходе ничего.
        #
        # Проверяем, что:
        # - Остальные платежи не процессятся, когда не включены в конфиге.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='native', created_at=DISABLED_ORDER_DATE,
                    ),
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
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'product',
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
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': (
                                'product_with_payment_and_commission'
                            ),
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
                            'amount': '100',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'cash',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'restaurant_tips',
                            'product_id': 'product_with_payment_only',
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
            False,
            id='Other BillingRefund not processed if disabled.',
        ),
        # На входе:
        # - OrderCreated (native) со старой датой.
        # - BillingRefund (1) с product.
        # - BillingRefund (2) с retail.
        # - BillingRefund (3) с restaurant_tips.
        #
        # На выходе:
        # - PayoutOrder для (1).
        # - PayoutOrder для (2).
        # - PayoutOrder для (3).
        #
        # Проверяем, что:
        # - Остальные платежи процессятся, когда включены в конфиге.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='native', created_at=ENABLED_ORDER_DATE,
                    ),
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
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'product',
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
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': (
                                'product_with_payment_and_commission'
                            ),
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
                            'amount': '100',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'restaurant_tips',
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
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'card',
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
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '0',
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
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'subsidy',
                            'value_amount': '100',
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
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='Other BillingRefund processed if enabled.',
        ),
        # Проверка исправления бага
        # https://st.yandex-team.ru/EDAORDERS-4168
        # (Для marketplace-доставки сервис должен ходить за правилами
        # для ресторана, а ошибочно ходит за правилами для курьера.)
        #
        # На входе:
        # - OrderCreated (native).
        # - BillingRefund с mp_delivery
        #   (здесь добавлен order_type который есть в событии от траста,
        #   но еще нет в событиях от эвент-комбайнера ритейла).
        #
        # На выходе:
        # - PayoutOrder для mp_delivery.
        #
        # Проверяем, что:
        # - Для BillingRefund с mp_delivery создается PayoutOrder с комиссией.
        # - В ручку business-rules ходим с правильными аргументами (ресторан).
        # - Правильно считается комиссия (для marketplace всегда 0).
        # - Исходное событие финализируются.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(
                        order_type='native', created_at=ENABLED_ORDER_DATE,
                    ),
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': str(consts.PLACE_ID),
                            'product_type': 'delivery',
                            'product_id': 'delivery/native/marketplace',
                            'transaction_type': 'refund',
                            'flow_type': 'native',
                            'order_type': 'marketplace',
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
                        'BillingRefund/1',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 4168,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'paysys_partner_id': consts.PAYSYS_PARTNER_ID,
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'mp_delivery',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingRefund/1'
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
                    commission=4,
                    acquiring_commission=1,
                    fix_commission=68,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Bugfix: EDAORDERS-4168',
        ),
    ],
)
async def test_nonretail_refunds(
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
