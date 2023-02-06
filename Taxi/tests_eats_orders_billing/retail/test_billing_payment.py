import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.config(
    EDA_CORE_SWITCH_TO_EATS_BILLING_PROCESSOR={
        # >= чем ENABLED_ORDER_DATE
        'filter_payture_payments': '2020-12-01T00:00:00+03:00',
    },
)
@pytest.mark.parametrize(
    'input_stq_args,'
    'expected_search_request,'
    'search_response,'
    'expected_store_request,'
    'expected_finish_requests,'
    'expected_output_stq_args,'
    'expected_input_stq_fail',
    [
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet,
        #   PaymentReceived.
        # Нет события StartPickerOrderEvent,
        # которое нужно для BillingPayment.
        # STQ-таска падает.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={'orderType': 'retail'},
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': 'card',
                            'paymentTerminalId': None,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'assemblyAmount': 10,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_output_stq_args
            None,
            # expected_input_stq_fail
            True,
            id='No "StartPickerOrderEvent" event for case '
            '"PaymentReceived" => "BillingPayment".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   StartPickerOrderEvent,
        #   PaymentReceived.
        # Нет события PaymentMethodSet, которое нужно для BillingPayment.
        # STQ-таска падает.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'assemblyAmount': 10,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_output_stq_args
            None,
            # expected_input_stq_fail
            True,
            id='No "PaymentMethodSet" event for case '
            '"PaymentReceived" => "BillingPayment".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (с терминалом типа string),
        #   StartPickerOrderEvent,
        #   PaymentReceived (включая доставку).
        # На выходе биллинг-события:
        #   BillingPayment (для товаров),
        #   BillingPayment (для сборки),
        #   BillingPayment (для доставки).
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'createdAt': consts.ORDER_CREATED_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': consts.PAYMENT_METHOD,
                            'paymentTerminalId': consts.PAYMENT_TERMINAL_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'assemblyAmount': 10,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'retail/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '273',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'delivery/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '189',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'delivery',
                            'product_id': 'delivery/retail/native',
                            'transaction_type': 'payment',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'assembly/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '10',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'assembly',
                            'product_id': 'assembly/retail/native',
                            'transaction_type': 'payment',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
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
                helpers.make_storage_finish_request(
                    doc_id=714, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=715, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='3 "BillingPayment" events created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (с терминалом типа int),
        #   StartPickerOrderEvent,
        #   PaymentReceived (с нулевыми суммами).
        # Ничего не происходит.
        #
        # Проверяем, что:
        # - принимается 'payment_terminal_id' типа int
        # - не создаются BillingPayment для нулевых сумм
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'createdAt': consts.ORDER_CREATED_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': consts.PAYMENT_METHOD,
                            'paymentTerminalId': int(
                                consts.PAYMENT_TERMINAL_ID,
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 0,
                            'currency': 'RUB',
                            'goodsAmount': 0,
                            'deliveryAmount': 0,
                            'assemblyAmount': 0,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_output_stq_args
            None,
            # expected_input_stq_fail
            False,
            id='No zero-amount "BillingPayment" events created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (без терминала),
        #   StartPickerOrderEvent,
        #   PaymentReceived (без доставки).
        # На выходе биллинг-события:
        #   BillingPayment (для товаров),
        #   BillingPayment (для сборки).
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'createdAt': consts.ORDER_CREATED_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': consts.PAYMENT_METHOD,
                            'paymentTerminalId': None,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'retail/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '273',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'delivery/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '189',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': None,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'delivery',
                            'product_id': 'delivery/retail/native',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'transaction_type': 'payment',
                            'external_payment_id': consts.ORDER_NR,
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
                helpers.make_storage_finish_request(
                    doc_id=714, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=715, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='2 "BillingPayment" events created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet с badge,
        #   StartPickerOrderEvent,
        #   PaymentReceived (без доставки).
        # На выходе биллинг-события:
        #   BillingPayment (для товаров),
        #   BillingPayment (для сборки).
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'createdAt': consts.ORDER_CREATED_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': 'badge',
                            'paymentTerminalId': None,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'retail/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '273',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': 'badge_corporate',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'delivery/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '189',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': 'badge_corporate',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'delivery',
                            'product_id': 'delivery/retail/native',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'transaction_type': 'payment',
                            'external_payment_id': consts.ORDER_NR,
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
                helpers.make_storage_finish_request(
                    doc_id=714, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=715, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='"BillingPayment" for badge',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet с corporate,
        #   StartPickerOrderEvent,
        #   PaymentReceived (без доставки).
        # На выходе биллинг-события:
        #   BillingPayment (для товаров),
        #   BillingPayment (для сборки).
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'createdAt': consts.ORDER_CREATED_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': 'corporate',
                            'paymentTerminalId': None,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'retail/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '273',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': 'corporate',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'payment',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPayment',
                        external_event_ref='BillingPayment/'
                        f'{consts.ORDER_NR}/'
                        '/'
                        'delivery/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '189',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': 'corporate',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'delivery',
                            'product_id': 'delivery/retail/native',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'transaction_type': 'payment',
                            'external_payment_id': consts.ORDER_NR,
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
                helpers.make_storage_finish_request(
                    doc_id=714, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=715, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='"BillingPayment" for corporate',
        ),
        # На входе сырые события:
        #   OrderCreated  c paymentService="EatsPayments",
        #   PaymentMethodSet,
        #   PaymentReceived.
        # На выходе биллинг-события:
        #   ничего
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'paymentService': 'EatsPayments',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': consts.PAYMENT_METHOD,
                            'paymentTerminalId': None,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentReceived',
                        data={
                            'amount': 462,
                            'currency': 'RUB',
                            'goodsAmount': 273,
                            'deliveryAmount': 189,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_output_stq_args
            None,
            # expected_input_stq_fail
            False,
            id='EatsPayments orders payments not billed',
        ),
    ],
)
async def test_billing_picker_order_paid(
        stq_runner,
        stq,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_output_stq_args,
        expected_input_stq_fail,
):
    await helpers.raw_processing_test_func(
        stq_runner,
        stq,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_output_stq_args,
        expected_input_stq_fail,
    )
