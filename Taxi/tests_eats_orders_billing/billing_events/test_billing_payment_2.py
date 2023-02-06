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
        # - BillingPayment (1) с badge_corporate.
        # - BillingPayment (2) с corporate.
        #
        # На выходе:
        # - 2 PayoutOrder c верным paysys_partner_id
        #
        # Проверяем, что:
        # - paysys_partner_id подменяется
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
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '100',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'corporate',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
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
                        'BillingPayment/2147995772',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'badge_corporate',
                            'payment_terminal_id': None,
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/2147995772'
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
                            'service_id': 111,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yaeda',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'corporate',
                            'payment_terminal_id': None,
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
            None,
            # business_rules_response
            None,
            # expected_input_stq_fail
            False,
            id='Test badge corporate payment type',
        ),
        # Кейс happy path.
        #
        # На входе:
        # - OrderCreated (retail).
        # - BillingPayment payment_service=yandex_market
        #
        # На выходе:
        # - PayoutOrder c верным paysys_partner_id
        #
        # Проверяем, что:
        # - paysys_partner_id подменяется
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
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'flow_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
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
                        'BillingPayment/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'yandex_market',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/711'
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
            # expected_input_stq_fail
            False,
            id='Test changing paysys_partner_id',
        ),
        # Кейс happy path.
        #
        # На входе:
        # - OrderCreated (burger_king).
        # - BillingPayment payment_service=burger_king
        #
        # На выходе:
        # - PayoutOrder c верным paysys_partner_id
        #
        # Проверяем, что:
        # - paysys_partner_id подменяется
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(order_type='burger_king'),
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.COURIER_ID_2_AS_STRING,
                            'product_type': 'delivery',
                            'flow_type': 'burger_king',
                            'order_type': 'native',
                            'product_id': 'delivery/burger_king/native',
                            'transaction_type': 'payment',
                            'payment_service': 'burger_king',
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
                        'BillingPayment/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'burger_king',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            'product': 'native_delivery',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '5',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/711'
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
                    counteragent_type='courier',
                    counteragent_details={
                        'courier_id': consts.COURIER_ID_2_AS_STRING,
                        'product_type': 'delivery',
                        'agreement_type': 'delivery',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=1,
                    acquiring_commission=0,
                    fix_commission=0,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='Test changing paysys_partner_id burger_king',
        ),
        # Кейс happy path.
        #
        # На входе:
        # - BillingPayment с donation
        #
        # На выходе:
        # - PayoutOrder
        #
        # Проверяем, что:
        # - создаётся событие платежа
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(
                consts.ORDER_NR,
                billing_extra_data={
                    'flow_type': 'native',
                    'order_created': consts.OTHER_DATE,
                },
            ),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'RUB',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PLACE_ID_AS_STRING,
                            'product_type': 'donation',
                            'flow_type': 'native',
                            'order_type': 'native',
                            'product_id': 'donation/native/native',
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
                        event_at=consts.OTHER_DATE,
                        external_event_ref=f'PayoutOrder/{consts.ORDER_NR}/'
                        'BillingPayment/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 676,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'payture',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            'product': 'donation',
                            'value_amount': '500',
                            'currency': 'RUB',
                            'commission': '10.01',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/711'
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
            [],
            # business_rules_response
            [],
            # expected_input_stq_fail
            False,
            id='Test creation payoutOrder for donation events',
        ),
        # Кейс happy path.
        #
        # На входе:
        # - OrderCreated (native).
        # - BillingPayment currency=BYN
        #
        # На выходе:
        # - PayoutOrder c верным paysys_partner_id
        #
        # Проверяем, что:
        # - paysys_partner_id подменяется
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
                        kind='BillingPayment',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'amount': '500',
                            'currency': 'BYN',
                            'client_id': consts.CLIENT_ID,
                            'payment_method': 'card',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PLACE_ID_AS_STRING,
                            'product_type': 'product',
                            'flow_type': 'native',
                            'product_id': 'product/native/native',
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
                        'BillingPayment/711',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 111,
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'paysys_partner_id': 'ecommpay',
                            'transaction_type': 'payment',
                            'payload': {},
                            'payment_type': 'card',
                            'payment_terminal_id': None,
                            'product': 'goods',
                            'value_amount': '500',
                            'currency': 'BYN',
                            'commission': '0',
                            'identity': (
                                f'PayoutOrder/{consts.ORDER_NR}/'
                                'BillingPayment/711'
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
            # expected_input_stq_fail
            False,
            id='Test changing paysys_partner_id for BYN',
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
