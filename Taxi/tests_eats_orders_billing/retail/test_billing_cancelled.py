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
        #   OrderCreated, OrderCancelled.
        #   (Нет события StartPickerOrderEvent)
        # На выходе billing-события:
        #   BillingCancelled без picker_id и transaction_date.
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
                            'currency': 'THB',
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
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'isPlaceFault': False,
                            'orderCancelId': consts.ORDER_CANCEL_ID,
                            'isPaymentExpected': False,
                            'isReimbursementRequired': False,
                        },
                    ),
                ],
            ),
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
                            'transaction_date': None,
                            'order_cancel_id': str(consts.ORDER_CANCEL_ID),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'picker_id': None,
                            'courier_id': None,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'THB',
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
                ],
            ),
            [
                helpers.make_storage_finish_request(
                    doc_id=711, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=712, status='complete',
                ),
            ],
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCancelled" without picker_id '
            'and transaction_date created.',
        ),
        # На входе сырые события:
        #   OrderCreated, OrderCancelled, CourierAssigned
        # На выходе billing-события:
        #   BillingCancelled без picker_id и transaction_date
        #  есть courier_id
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
                            'currency': 'THB',
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
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'isPlaceFault': False,
                            'orderCancelId': consts.ORDER_CANCEL_ID,
                            'isPaymentExpected': False,
                            'isReimbursementRequired': False,
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
                ],
            ),
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
                            'transaction_date': None,
                            'order_cancel_id': str(consts.ORDER_CANCEL_ID),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'picker_id': None,
                            'courier_id': consts.COURIER_ID_AS_STRING,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'THB',
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
            ],
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCancelled" without picker_id '
            'and transaction_date created. Courier is assigned',
        ),
        # На входе сырые события:
        #   OrderCreated, OrderCancelled, CourierAssigned 2
        # На выходе billing-события:
        #  BillingCancelled без picker_id и transaction_date
        #  есть courier_id из последнего события
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
                            'currency': 'THB',
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
                        doc_id=712,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'isPlaceFault': False,
                            'orderCancelId': consts.ORDER_CANCEL_ID,
                            'isPaymentExpected': False,
                            'isReimbursementRequired': False,
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
                        kind='CourierAssigned',
                        data={
                            'courierId': consts.COURIER_ID_2,
                            'assignedAt': consts.COURIER_ASSIGNED_AT_DATE_2,
                        },
                    ),
                ],
            ),
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
                            'transaction_date': None,
                            'order_cancel_id': str(consts.ORDER_CANCEL_ID),
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'picker_id': None,
                            'courier_id': consts.COURIER_ID_AS_STRING,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'THB',
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
            # expected_input_stq_fail
            False,
            id='Event "BillingCancelled" without picker_id '
            'and transaction_date created. Courier is assigned',
        ),
        # На входе сырые события:
        #   OrderCreated, OrderChanged, OrderChanged, OrderChanged,
        #   StartPickerOrderEvent, OrderCancelled.
        # На выходе billing-события:
        #   BillingCancelled с courier_id и transaction_date.
        # Данные по стоимости должны взяться из последнего OrderChanged.
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
                            'currency': 'USD',
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
                            'currency': 'RUB',
                            'updatedAt': '2020-10-24T18:33:33+03:00',
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
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (
                                consts.START_PICKER_ORDER_DATE
                            ),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=716,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'orderCancelId': consts.ORDER_CANCEL_ID,
                            'isPaymentExpected': True,
                            'isReimbursementRequired': True,
                        },
                    ),
                ],
            ),
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
                            'is_reimbursement_required': True,
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
                helpers.make_storage_finish_request(
                    doc_id=716, status='complete',
                ),
            ],
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCancelled" with picker_id '
            'and transaction_date created.',
        ),
        # На входе сырые события:
        #   OrderCreatedOrderChanged,
        #   StartPickerOrderEvent, OrderCancelled.
        # На выходе billing-события:
        #   BillingCancelled с courier_id и transaction_date.
        #
        # Проверяем, что:
        # - данные по стоимости должны взяться из последнего OrderChanged.
        # - в BillingCancelled попадают courier_id и transaction_date.
        # - нормально принимается 'orderCancelId' типа int.
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
                            },
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
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'orderCancelId': consts.ORDER_CANCEL_ID,
                            'isPaymentExpected': True,
                            'isReimbursementRequired': True,
                        },
                    ),
                ],
            ),
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
                            'is_reimbursement_required': True,
                            'picker_id': consts.PICKER_ID,
                            'courier_id': None,
                            'place_id': str(consts.PLACE_ID),
                            # Данные берутся из OrderChanged с doc_id=712
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
            # expected_input_stq_fail
            False,
            id='Event "BillingCancelled" without '
            'promocodeAssemblyDiscount created.',
        ),
        # На входе сырые события:
        # OrderCreated (с нулевыми суммами), StartPickerOrderEvent,
        # OrderCancelled.
        # На выходе billing-события:
        # BillingCancelled с courier_id и transaction_date.
        #
        # Проверяем, что:
        # - в BillingCancelled не попадают продукты с нулевой суммой.
        # - нормально принимается 'orderCancelId' типа string.
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
                            'currency': 'RUB',
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
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'orderCancelId': str(consts.ORDER_CANCEL_ID),
                            'isPaymentExpected': False,
                            'isReimbursementRequired': False,
                        },
                    ),
                ],
            ),
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
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'products': [],
                            'order_type': 'native',
                            'flow_type': 'retail',
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
            ],
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCancelled" without '
            'zero-amount products created.',
        ),
        # На входе сырые события:
        #   OrderCreated, StartPickerOrderEvent, PickerOrderPaid,
        #   OrderCancelled.
        # На выходе billing-события:
        #   BillingCancelled с amount_picker_paid
        # Проверяем, что:
        # - в BillingCancelled при отмене заказа после оплаты
        # пишется сумма, которую сборщик заплатил на кассе
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
                            'currency': 'RUB',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 100,
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
                        kind='PickerOrderPaidEvent',
                        data={
                            'amount': 100,
                            'paid_at': (consts.PICKER_ORDER_PAID_DATE),
                            'currency': consts.CURRENCY,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=714,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCancelled',
                        data={
                            'cancelledAt': consts.ORDER_CANCELLED_DATE,
                            'orderCancelId': str(consts.ORDER_CANCEL_ID),
                            'isPaymentExpected': False,
                            'isReimbursementRequired': False,
                        },
                    ),
                ],
            ),
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
                            'is_payment_expected': False,
                            'is_reimbursement_required': False,
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '100',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                            ],
                            'amount_picker_paid': '100',
                            'order_type': 'native',
                            'flow_type': 'retail',
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
            id='Event "BillingCancelled" ' 'with amount picker paid',
        ),
    ],
)
async def test_billing_cancelled(
        stq_runner,
        stq,
        experiments3,
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

    experiments3.add_experiment(**helpers.make_use_core_revisions_exp())

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
