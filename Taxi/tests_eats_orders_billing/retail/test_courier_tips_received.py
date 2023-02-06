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
        #   CourierTipsReceived.
        # Нет события CourierAssigned,
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
                        data={
                            'orderType': 'retail',
                            'createdAt': '2020-11-01T00:00:00+03:00',
                        },
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
                        kind='CourierTipsReceived',
                        data={
                            'amount': '99',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
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
            id='"StartPickerOrderEvent" not found.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   CourierAssigned,
        #   CourierTipsReceived.
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
                            'createdAt': '2020-11-01T00:00:00+03:00',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='CourierTipsReceived',
                        data={
                            'amount': '99',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
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
            id='"PaymentMethodSet" not found.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (с терминалом типа string),
        #   CourierAssigned,
        #   CourierTipsReceived,
        #   StartPickerOrderEvent
        # На выходе биллинг-события:
        #   BillingPayment (tips)
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
                            'createdAt': '2020-11-01T00:00:00+03:00',
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
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='CourierTipsReceived',
                        data={
                            'amount': '99',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': int(consts.PICKER_ID),
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
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
                        'tips/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '99',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': 'eda_tips',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'tips',
                            'product_id': 'tips/retail/native',
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
            id='"BillingPayment" with terminal created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (без терминала),
        #   CourierAssigned,
        #   CourierTipsReceived,
        #   StartPickerOrderEvent
        # На выходе биллинг-события:
        #   BillingPayment (tips).
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
                            'createdAt': '2020-11-01T00:00:00+03:00',
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
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='CourierTipsReceived',
                        data={
                            'amount': '99',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': int(consts.PICKER_ID),
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
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
                        'tips/retail/native',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'amount': '99',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': 'eda_tips',
                            'payment_terminal_id': None,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'tips',
                            'product_id': 'tips/retail/native',
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
            id='"BillingPayment" without terminal created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (с терминалом типа int),
        #   CourierAssigned,
        #   CourierTipsReceived (с нулевой суммой).
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
                            'createdAt': '2020-11-01T00:00:00+03:00',
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
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='CourierTipsReceived',
                        data={
                            'amount': '0',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
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
            id='No zero-amount "BillingPayment" created.',
        ),
        # На входе сырые события:
        #   OrderCreated с paymentService = "EatsPayments",
        #   PaymentMethodSet,
        #   CourierTipsReceived.
        # Ничего не происходит.
        #
        # Проверяем, что:
        # - для заказов через Траст платежи не создаем по этому событию
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
                            'createdAt': '2020-11-01T00:00:00+03:00',
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
                        kind='CourierTipsReceived',
                        data={
                            'amount': '99',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
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
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (с терминалом типа string),
        #   CourierAssigned,
        #   CourierTipsReceived,
        #   StartPickerOrderEvent
        # На выходе биллинг-события:
        #   ничего, платежи фильтруются
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
                            'createdAt': '2021-11-01T00:00:00+03:00',
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
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='CourierTipsReceived',
                        data={
                            'amount': '99',
                            'currency': 'RUB',
                            'receivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': int(consts.PICKER_ID),
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
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
            id='Payture payments are filtered',
        ),
    ],
)
async def test_courier_tips_received(
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
