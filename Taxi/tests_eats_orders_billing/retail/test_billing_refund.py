import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


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
        #   Refund.
        #   (нет события StartPickerOrderEvent,
        #    нужного для BillingRefund).
        # STQ-таска падает.
        pytest.param(
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            helpers.make_storage_search_request(consts.ORDER_NR),
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
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': 'card',
                            'paymentTerminalId': consts.PAYMENT_TERMINAL_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='Refund',
                        data={
                            'amount': 374,
                            'currency': 'RUB',
                            'refundId': consts.REFUND_ID,
                            'refundedAt': consts.REFUNDED_AT,
                            'productType': 'products',
                            'isPlaceFault': True,
                        },
                    ),
                ],
            ),
            None,
            None,
            None,
            True,
            id='No event "StartPickerOrderEvent" for case '
            '"Refund" => "BillingRefund"',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   StartPickerOrderEvent,
        #   Refund.
        #   (нет события PaymentMethodSet,
        #    нужного для BillingRefund).
        # STQ-таска падает.
        pytest.param(
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            helpers.make_storage_search_request(consts.ORDER_NR),
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
                        kind='Refund',
                        data={
                            'amount': 374,
                            'currency': 'RUB',
                            'refundId': consts.REFUND_ID,
                            'refundedAt': consts.REFUNDED_AT,
                            'productType': 'products',
                            'isPlaceFault': True,
                        },
                    ),
                ],
            ),
            None,
            None,
            None,
            True,
            id='No event "PaymentMethodSet" for case '
            '"Refund" => "BillingRefund".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet
        #   StartPickerOrderEvent,
        #   Refund (productType = products, без discounts).
        # На выходе биллинг-события:
        #   BillingRefund.
        pytest.param(
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            helpers.make_storage_search_request(consts.ORDER_NR),
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
                        kind='Refund',
                        data={
                            'amount': 374,
                            'currency': 'RUB',
                            'refundId': consts.REFUND_ID,
                            'refundedAt': consts.REFUNDED_AT,
                            'productType': 'products',
                            'isPlaceFault': True,
                        },
                    ),
                ],
            ),
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        external_event_ref='BillingRefund/'
                        f'{consts.ORDER_NR}/{consts.REFUND_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.REFUNDED_AT,
                            'amount': '374',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.PICKER_ID,
                            'product_type': 'retail',
                            'product_id': 'retail/retail/native',
                            'transaction_type': 'refund',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                ],
            ),
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
            ],
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            False,
            id='Event "BillingRefund" created for case '
            '"Refund" => "BillingRefund".',
        ),
        # На входе сырые события:
        #   OrderCreated, PaymentMethodSet
        #   StartPickerOrderEvent, Refund (productType = delivery, discounts).
        # На выходе биллинг-события:
        #   BillingRefund
        # В этом тесте проверяем, что:
        # - изменение 'productType' в событии Refund
        # изменяет 'type', 'product_type' и 'product_id' в выходных событиях.
        # - нормально принимается 'refundId' типа int.
        pytest.param(
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            helpers.make_storage_search_request(consts.ORDER_NR),
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
                        kind='Refund',
                        data={
                            'amount': 374,
                            'currency': 'RUB',
                            'refundId': int(consts.REFUND_ID),
                            'refundedAt': consts.REFUNDED_AT,
                            'productType': 'delivery',
                            'isPlaceFault': True,
                            'discounts': [
                                [
                                    {
                                        'type': 'discount_group_0',
                                        'amount': 10,
                                        'discountProvider': 'own',
                                    },
                                ],
                            ],
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
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        external_event_ref='BillingRefund/'
                        f'{consts.ORDER_NR}/{consts.REFUND_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.REFUNDED_AT,
                            'amount': '374',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'delivery',
                            'product_id': 'delivery/retail/native',
                            'transaction_type': 'refund',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                ],
            ),
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
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            False,
            id='Events "BillingRefund" created (2).',
        ),
        # На входе сырые события:
        #   OrderCreated, PaymentMethodSet
        #   StartPickerOrderEvent, Refund (с нулевыми скидками).
        # На выходе биллинг-события:
        #   BillingRefund
        # В этом тесте проверяем, что:
        # - нормально принимается 'refundId' типа string.
        pytest.param(
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            helpers.make_storage_search_request(consts.ORDER_NR),
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
                        kind='Refund',
                        data={
                            'amount': 374,
                            'currency': 'RUB',
                            'refundId': str(consts.REFUND_ID),
                            'refundedAt': consts.REFUNDED_AT,
                            'productType': 'delivery',
                            'isPlaceFault': True,
                            'discounts': [
                                [
                                    {
                                        'type': 'discount_group_0',
                                        'amount': 0,
                                        'discountProvider': 'own',
                                    },
                                ],
                                [
                                    {
                                        'type': 'discount_group_1',
                                        'amount': 0,
                                        'discountProvider': 'own',
                                    },
                                ],
                            ],
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
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        external_event_ref='BillingRefund/'
                        f'{consts.ORDER_NR}/{consts.REFUND_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.REFUNDED_AT,
                            'amount': '374',
                            'currency': 'RUB',
                            'client_id': None,
                            'event_at': consts.OTHER_DATE,
                            'payment_method': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'counteragent_id': consts.COURIER_ID_AS_STRING,
                            'product_type': 'delivery',
                            'product_id': 'delivery/retail/native',
                            'transaction_type': 'refund',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'external_payment_id': consts.ORDER_NR,
                        },
                    ),
                ],
            ),
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
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            False,
            id='Events "BillingRefund"  ' ' created.',
        ),
        # На входе сырые события:
        #   OrderCreated с paymentService = "EatsPayments",
        #   PaymentMethodSet, StartPickerOrderEvent,
        #   Refund (productType = products, без discounts).
        # На выходе биллинг-события:
        #   ничего
        # В этом тесте проверяется, для заказа через Траст
        # BillingRefund не создается
        pytest.param(
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            helpers.make_storage_search_request(consts.ORDER_NR),
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=711,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'paymentService': 'EatsPayments',
                            'placeId': consts.PLACE_ID,
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
                        kind='Refund',
                        data={
                            'amount': 374,
                            'currency': 'RUB',
                            'refundId': consts.REFUND_ID,
                            'refundedAt': consts.REFUNDED_AT,
                            'productType': 'products',
                            'isPlaceFault': True,
                        },
                    ),
                ],
            ),
            None,
            None,
            None,
            False,
            id='EatsPayments orders payments not billed, '
            'no compensation events',
        ),
    ],
)
async def test_billing_refund(
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
