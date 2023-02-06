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
        #   OrderCreated ('placeId' = int),
        #   OrderChanged ('placeId' = int),
        #   OrderChanged ('placeId' = int),
        #   OrderChanged ('placeId' = int),
        #   PaymentMethodSet,
        #   StartPickerOrderEvent,
        #   PaymentNotReceived,
        #   OrderCancelled,
        # На выходе биллинг-события:
        #   BillingPaymentNotReceived,
        #   BillingCancelled.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=2147995772,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'currency': 'EUR',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 20,
                            'deliveryPrice': 10,
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
                        doc_id=713,
                        order_nr=consts.ORDER_NR,
                        kind='OrderChanged',
                        data={
                            'orderType': 'retail',
                            'placeId': consts.PLACE_ID,
                            'currency': 'THB',
                            'updatedAt': '2020-10-24T18:39:39+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 400},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': 'online',
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
                            'currency': 'THB',
                            'updatedAt': '2020-10-24T18:32:32+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 400},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': 'online',
                                'promocodeGoodsDiscount': 100,
                                'promocodeDeliveryDiscount': 200,
                                'promocodeAssemblyDiscount': 300,
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
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'isPlaceFault': False,
                            'orderCancelId': consts.ORDER_CANCEL_ID,
                            'isPaymentExpected': True,
                            'isReimbursementRequired': False,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=718,
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
                        kind='BillingCancelled',
                        event_at=consts.ORDER_CANCELLED_DATE,
                        external_event_ref='BillingCancelled/'
                        f'{consts.ORDER_NR}/{consts.ORDER_CANCEL_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'cancelled_at': consts.ORDER_CANCELLED_DATE,
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'order_cancel_id': str(consts.ORDER_CANCEL_ID),
                            'is_payment_expected': True,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            # Данные берутся из OrderChanged с doc_id=713
                            'currency': 'THB',
                            'service_fee_amount': '9',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '400',
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '100',
                                    'type': 'marketing_promocode',
                                    'product_type': 'retail',
                                },
                            ],
                            'order_type': 'native',
                            'flow_type': 'retail',
                        },
                    ),
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
                            'currency': 'THB',
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
                    doc_id=2147995772, status='complete',
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
                helpers.make_storage_finish_request(
                    doc_id=718, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Events "BillingCancelled", '
            '"BillingPaymentNotReceived" created.',
        ),
        # На входе сырые события:
        #   OrderCreated ('placeId' = string),
        #   PaymentMethodSet,
        #   PaymentReceived,
        #   StartPickerOrderEvent ('picker_id' = int),
        #   OrderDelivered,
        #   Refund.
        # На выходе биллинг-события:
        #   BillingPayment (товары),
        #   BillingPayment (доставка),
        #   BillingPayment (сборка),
        #   BillingDelivered,
        #   BillingRefund,
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
                            'placeId': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'updatedAt': '2020-10-24T18:39:39+03:00',
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
                        kind='PaymentReceived',
                        data={
                            'amount': 3500,
                            'currency': 'RUB',
                            'goodsAmount': 2000,
                            'deliveryAmount': 1000,
                            'assemblyAmount': 500,
                            'paymentReceivedAt': consts.PAYMENT_RECEIVED_AT,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': int(consts.PICKER_ID),
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=715,
                        order_nr=consts.ORDER_NR,
                        kind='OrderDelivered',
                        data={'deliveredAt': consts.OTHER_DATE},
                    ),
                    helpers.make_billing_doc(
                        doc_id=716,
                        order_nr=consts.ORDER_NR,
                        kind='Refund',
                        data={
                            'amount': 1000,
                            'currency': 'RUB',
                            'refundId': consts.REFUND_ID,
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
                        doc_id=717,
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
                            'amount': '2000',
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
                            'amount': '1000',
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
                            'amount': '500',
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
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingDelivered',
                        external_event_ref='BillingDelivered/'
                        f'{consts.ORDER_NR}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.START_PICKER_ORDER_DATE,
                            'delivered_at': consts.OTHER_DATE,
                            'courier_id': consts.COURIER_ID_AS_STRING,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'service_fee_amount': '9',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '400',  # promoDiscount
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                    'entity_id': 'some_promo_id',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': (
                                        '100'
                                    ),  # promocodeGoodsDiscount
                                    'type': 'some_promocode_type',
                                    'product_type': 'retail',
                                    'entity_id': 'some_promocode_id',
                                },
                            ],
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingRefund',
                        external_event_ref='BillingRefund/'
                        f'{consts.ORDER_NR}/{consts.REFUND_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.REFUNDED_AT,
                            'amount': '1000',
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
            id='Events "BillingPayment", "BillingDelivered", '
            '"BillingRefund" created.',
        ),
    ],
)
async def test_complex_cases(
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
        mock_customer_service_retrieve,
        mock_customer_service_retrieve_new,
        mock_order_revision_list,
        mock_order_revision_list_new,
):
    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])
    mock_order_revision_list_new(revisions=[{'origin_revision_id': '123-321'}])

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
