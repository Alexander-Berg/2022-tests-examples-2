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
        #   StartPickerOrderEvent,
        #   PaymentNotReceived.
        #   (нет события PaymentMethodSet,
        #    нужного для BillingPaymentNotReceived).
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
                            'currency': 'RUB',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {
                                'promoId': 'some_promo_id',
                                'promoDiscount': 400,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id',
                                'promocodeType': 'some_promocode_type',
                                'promocodeGoodsDiscount': 100,
                                'promocodeDeliveryDiscount': 200,
                                'promocodeAssemblyDiscount': 300,
                            },
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
                        kind='PaymentNotReceived',
                        data={'paymentNotReceivedAt': consts.OTHER_DATE},
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
            id='No event "PaymentMethodSet" for case '
            '"PaymentNotReceived" => "BillingPaymentNotReceived".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet,
        #   PaymentNotReceived.
        #   (нет события StartPickerOrderEvent,
        #    нужного для BillingPaymentNotReceived).
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
                            'currency': 'RUB',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {
                                'promoId': 'some_promo_id',
                                'promoDiscount': 400,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id',
                                'promocodeType': 'some_promocode_type',
                                'promocodeGoodsDiscount': 100,
                                'promocodeDeliveryDiscount': 200,
                                'promocodeAssemblyDiscount': 300,
                            },
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
                        kind='PaymentNotReceived',
                        data={'paymentNotReceivedAt': consts.OTHER_DATE},
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
            id='No event "StartPickerOrderEvent" for case '
            '"PaymentNotReceived" => "BillingPaymentNotReceived".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (без terminal_id),
        #   StartPickerOrderEvent,
        #   PaymentNotReceived.
        # На выходе биллинг-события:
        #   BillingPaymentNotReceived (без terminal_id).
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
                            'currency': 'BTC',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 400},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': None,
                                'promocodeGoodsDiscount': 100,
                                'promocodeDeliveryDiscount': 200,
                                'promocodeAssemblyDiscount': 300,
                            },
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
                        kind='PaymentNotReceived',
                        data={'paymentNotReceivedAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPaymentNotReceived',
                        external_event_ref='BillingPaymentNotReceived/'
                        f'{consts.ORDER_NR}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'payment_not_received_at': consts.OTHER_DATE,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': None,
                            'currency': 'BTC',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'product_type': 'retail',
                                    'value_amount': '2000',  # goodsPrice
                                },
                                {
                                    'product_id': 'delivery/retail/native',
                                    'product_type': 'delivery',
                                    'value_amount': '1000',  # deliveryPrice
                                },
                                {
                                    'product_id': 'assembly/retail/native',
                                    'product_type': 'assembly',
                                    'value_amount': '500',  # assembleCost
                                },
                            ],
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingPaymentNotReceived" created (1).',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   OrderChanged, OrderChanged, OrderChanged,
        #   PaymentMethodSet (с terminal_id),
        #   StartPickerOrderEvent,
        #   PaymentNotReceived.
        # На выходе биллинг-события:
        #   BillingPaymentNotReceived (с terminal_id).
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
                            'currency': 'RUB',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 2,
                            'deliveryPrice': 1,
                            'assembleCost': 5,
                            'promo': {'promoId': None, 'promoDiscount': 4},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': None,
                                'promocodeGoodsDiscount': 1,
                                'promocodeDeliveryDiscount': 2,
                                'promocodeAssemblyDiscount': 3,
                            },
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='OrderChanged',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'currency': 'THB',
                            'updatedAt': '2020-10-24T18:31:31+03:00',
                            'goodsPrice': 200,
                            'deliveryPrice': 100,
                            'assembleCost': 50,
                            'promo': {'promoId': None, 'promoDiscount': 40},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': None,
                                'promocodeGoodsDiscount': 10,
                                'promocodeDeliveryDiscount': 20,
                                'promocodeAssemblyDiscount': 30,
                            },
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='OrderChanged',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'currency': 'BTC',
                            'updatedAt': '2020-10-24T18:39:39+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 400},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': None,
                                'promocodeGoodsDiscount': 100,
                                'promocodeDeliveryDiscount': 200,
                                'promocodeAssemblyDiscount': 300,
                            },
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='OrderChanged',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'currency': 'USD',
                            'updatedAt': '2020-10-24T18:32:32+03:00',
                            'goodsPrice': 20000,
                            'deliveryPrice': 10000,
                            'assembleCost': 5000,
                            'promo': {'promoId': None, 'promoDiscount': 4000},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': None,
                                'promocodeGoodsDiscount': 1000,
                                'promocodeDeliveryDiscount': 2000,
                                'promocodeAssemblyDiscount': 3000,
                            },
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentMethodSet',
                        data={
                            'paymentMethod': consts.PAYMENT_METHOD,
                            'paymentTerminalId': consts.PAYMENT_TERMINAL_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=716,
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
                        doc_id=717,
                        order_nr=consts.ORDER_NR,
                        kind='PaymentNotReceived',
                        data={'paymentNotReceivedAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPaymentNotReceived',
                        external_event_ref='BillingPaymentNotReceived/'
                        f'{consts.ORDER_NR}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'payment_not_received_at': consts.OTHER_DATE,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            # Данные берутся из OrderChanged с doc_id=713
                            'currency': 'BTC',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'product_type': 'retail',
                                    'value_amount': '2000',  # goodsPrice
                                },
                                {
                                    'product_id': 'delivery/retail/native',
                                    'product_type': 'delivery',
                                    'value_amount': '1000',  # deliveryPrice
                                },
                                {
                                    'product_id': 'assembly/retail/native',
                                    'product_type': 'assembly',
                                    'value_amount': '500',  # assembleCost
                                },
                            ],
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
                helpers.make_storage_finish_request(
                    doc_id=716, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=717, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingPaymentNotReceived" created (2).',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   PaymentMethodSet (с terminal_id),
        #   StartPickerOrderEvent,
        #   PaymentNotReceived.
        # На выходе биллинг-события:
        #   BillingPaymentNotReceived (с terminal_id).
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
                            'currency': 'BTC',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 0,
                            'deliveryPrice': 0,
                            'assembleCost': 0,
                            'promo': {'promoId': None, 'promoDiscount': 0},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': None,
                                'promocodeGoodsDiscount': 0,
                                'promocodeDeliveryDiscount': 0,
                                'promocodeAssemblyDiscount': 0,
                            },
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
                        kind='PaymentNotReceived',
                        data={'paymentNotReceivedAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingPaymentNotReceived',
                        external_event_ref='BillingPaymentNotReceived/'
                        f'{consts.ORDER_NR}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'payment_not_received_at': consts.OTHER_DATE,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'payment_type': consts.PAYMENT_METHOD,
                            'payment_terminal_id': consts.PAYMENT_TERMINAL_ID,
                            'currency': 'BTC',
                            'flow_type': 'retail',
                            'order_type': 'native',
                            'products': [],
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingPaymentNotReceived" without '
            'zero-amount products created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   StartPickerOrderEvent,
        #   PaymentNotReceived.
        #   (нет события PaymentMethodSet,
        #    нужного для BillingPaymentNotReceived).
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
                            'currency': 'RUB',
                            'createdAt': '2021-10-24T18:30:30+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {
                                'promoId': 'some_promo_id',
                                'promoDiscount': 400,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id',
                                'promocodeType': 'some_promocode_type',
                                'promocodeGoodsDiscount': 100,
                                'promocodeDeliveryDiscount': 200,
                                'promocodeAssemblyDiscount': 300,
                            },
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
                        kind='PaymentNotReceived',
                        data={'paymentNotReceivedAt': consts.OTHER_DATE},
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
async def test_billing_payment_not_received(
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
