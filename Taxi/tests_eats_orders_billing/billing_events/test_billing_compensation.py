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
        # Happy path с продуктами, без скидок.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingCompensation с retail, delivery, assembly.
        # На выходе:
        # - PayoutOrder для retail.
        # - PayoutOrder для delivery.
        # - PayoutOrder для assembly.
        #
        # Проверяем, что:
        # - PayoutOrder создается для каждого продукта из BillingCompensation.
        # - BillingCompensation финализируется.
        # - 'paysys_partner_id' = 'yaeda'
        # - 'payment_type' = 'our_refund'
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
                        kind='BillingCompensation',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'items': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'type': 'retail',
                                    'amount': '100',
                                    'discounts': [],
                                },
                                {
                                    'product_id': 'delivery/retail/native',
                                    'type': 'delivery',
                                    'amount': '200',
                                    'discounts': [],
                                },
                                {
                                    'product_id': 'assembly/retail/native',
                                    'type': 'assembly',
                                    'amount': '300',
                                    'discounts': [],
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
                        'BillingCompensation/2147995772/'
                        'retail/retail/native',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'our_refund',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/2147995772/'
                                'retail/retail/native'
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
                    billing_date=consts.COMPENSATION_AT_UTC,
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
            id='Happy path with products -discounts.',
        ),
        # Happy path с продуктами и со скидками.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingCompensation с retail и скидками
        #   marketing, marketing_promocode.
        # На выходе:
        # - PayoutOrder для retail.
        # - PayoutOrder для marketing (refund).
        # - PayoutOrder для marketing (payment).
        # - PayoutOrder для marketing_promocode (refund).
        # - PayoutOrder для marketing_promocode (payment).
        #
        # Проверяем, что:
        # - Для каждой скидки создается рефанд и платеж.
        # - У рефанда 'payment_type' == тип скидки
        # - У платежа 'payment_type' == 'our_refund'
        # - 'paysys_partner_id' = 'yaeda'
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
                        kind='BillingCompensation',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'items': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'type': 'retail',
                                    'amount': '100',
                                    'discounts': [
                                        {'type': 'marketing', 'amount': '20'},
                                        {
                                            'type': 'marketing_promocode',
                                            'amount': '30',
                                        },
                                    ],
                                },
                                {
                                    'product_id': 'assembly/retail/native',
                                    'type': 'assembly',
                                    'amount': '10',
                                    'discounts': [
                                        {
                                            'type': 'marketing_promocode',
                                            'amount': '5',
                                        },
                                    ],
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
                        'BillingCompensation/711/'
                        'retail/retail/native',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'our_refund',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '100',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/711/'
                                'retail/retail/native'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCompensation/711/'
                        'retail/retail/native/'
                        'marketing/refund',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'marketing',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '20',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/711/'
                                'retail/retail/native/'
                                'marketing/refund'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCompensation/711/'
                        'retail/retail/native/'
                        'marketing/payment',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'our_refund',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '20',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/711/'
                                'retail/retail/native/'
                                'marketing/payment'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCompensation/711/'
                        'retail/retail/native/'
                        'marketing_promocode/refund',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'marketing_promocode',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '30',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/711/'
                                'retail/retail/native/'
                                'marketing_promocode/refund'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCompensation/711/'
                        'retail/retail/native/'
                        'marketing_promocode/payment',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'our_refund',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '30',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/711/'
                                'retail/retail/native/'
                                'marketing_promocode/payment'
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='PayoutOrder',
                        event_at=consts.PICKER_ORDER_PAID_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingCompensation/711/'
                        'assembly/retail/native/'
                        'marketing_promocode/refund',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'service_id': 111,
                            'dt': consts.COMPENSATION_AT,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'refund',
                            'payload': {},
                            'payment_type': 'picker_marketing_promocode',
                            'payment_terminal_id': None,
                            # из конфига EATS_BILLING_PROCESSOR_PRODUCT_ID_MAP
                            'product': 'goods',
                            'value_amount': '5',
                            'currency': 'RUB',
                            'commission': '11',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingCompensation/711/'
                                'assembly/retail/native/'
                                'marketing_promocode/refund'
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
                    billing_date=consts.COMPENSATION_AT_UTC,
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.PICKER_ID,
                        'product_type': 'delivery',
                        'agreement_type': 'picker',
                    },
                ),
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.COMPENSATION_AT_UTC,
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
            id='Happy path with products +discounts. Commission on assembly',
        ),
        # Happy path без продуктов.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingCompensation без продуктов.
        # На выходе ничего.
        #
        # Проверяем, что:
        # - Пустой BillingCompensation нормально обрабатывается
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
                        kind='BillingCompensation',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'items': [],
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
        # Кейс с неизвестным product_id.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingCompensation с продуктом 'unknown_product_id'.
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
                        kind='BillingCompensation',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'items': [
                                {
                                    'product_id': 'unknown_product_id',
                                    'type': 'retail',
                                    'amount': '100',
                                    'discounts': [],
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
                    billing_date=consts.COMPENSATION_AT_UTC,
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
            id='Unknown product_id.',
        ),
        # TODO: кейс для 'product' (компенсация ресторану?)
        # TODO: кейс для 'delivery' и друого флоу (marketplace?)
        # TODO: кейс для 'tips' - для чаевых ничего не происходит
        # TODO: кейс для 'restaraunt_tips' - для чаевых ничего не происходит
    ],
)
async def test_billing_compensation(
        stq_runner,
        experiments3,
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
    experiments3.add_experiment(**helpers.make_use_core_revisions_exp())

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
