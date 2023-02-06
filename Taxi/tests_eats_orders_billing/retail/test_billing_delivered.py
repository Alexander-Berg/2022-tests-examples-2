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
        #   OrderDelivered.
        #   (нет события StartPickerOrderEvent, нужного для BillingDelivered).
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
                        kind='OrderDelivered',
                        data={'deliveredAt': consts.OTHER_DATE},
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
            id='No event "StartPickerOrderEvent" for "BillingDelivered".',
        ),
        # На входе сырые события:
        #   OrderCreated (у промиков нет id и type),
        #   StartPickerOrderEvent,
        #   OrderDelivered.
        # На выходе биллинг-события:
        #   BillingDelivered (с дефолтными id и type).
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
                            'currency': 'RUB',
                            'createdAt': '2020-10-24T18:30:30+03:00',
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
                        kind='OrderDelivered',
                        data={'deliveredAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
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
                            'courier_id': None,
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
                                    'entity_id': None,
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': (
                                        '100'
                                    ),  # promocodeGoodsDiscount
                                    'type': 'online',
                                    'product_type': 'retail',
                                    'entity_id': None,
                                },
                            ],
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
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingDelivered" with default id and type created.',
        ),
        # На входе сырые события:
        #   OrderCreated (у промиков есть id и type),
        #   OrderChanged, OrderChanged, OrderChanged,
        #   StartPickerOrderEvent,
        #   OrderDelivered.
        # На выходе биллинг-события:
        #   BillingDelivered (id и type берутся из промиков).
        # Данные по промикам берутся из последнего OrderChanged.
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
                            'currency': 'EUR',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 20,
                            'deliveryPrice': 10,
                            'assembleCost': 5,
                            'promo': {
                                'promoId': 'some_promo_id_711',
                                'promoDiscount': 4,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id_711',
                                'promocodeType': 'some_promocode_type_711',
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
                            'promo': {
                                'promoId': 'some_promo_id_712',
                                'promoDiscount': 40,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id_712',
                                'promocodeType': 'some_promocode_type_712',
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
                            'currency': 'RUB',
                            'updatedAt': '2020-10-24T18:39:39+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {
                                'promoId': 'some_promo_id_713',
                                'promoDiscount': 400,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id_713',
                                'promocodeType': 'some_promocode_type_713',
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
                            'updatedAt': '2020-10-24T18:33:33+03:00',
                            'goodsPrice': 20000,
                            'deliveryPrice': 10000,
                            'assembleCost': 5000,
                            'promo': {
                                'promoId': 'some_promo_id_714',
                                'promoDiscount': 4000,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id_714',
                                'promocodeType': 'some_promocode_type_714',
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
                        kind='OrderDelivered',
                        data={'deliveredAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
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
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            # данные берутся из OrderChanged с doc_id=713
                            'currency': 'RUB',
                            'service_fee_amount': '9',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '400',  # promoDiscount
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                    'entity_id': 'some_promo_id_713',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': (
                                        '100'
                                    ),  # promocodeGoodsDiscount
                                    'type': 'some_promocode_type_713',
                                    'product_type': 'retail',
                                    'entity_id': 'some_promocode_id_713',
                                },
                            ],
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingDelivered" with source id and type created.',
        ),
        # На входе сырые события:
        #   OrderCreated (без promocodeAssemblyDiscount,
        #                 'assemblyCost' вместо 'assembleCost'),
        #   OrderChanged (без promocodeAssemblyDiscount,
        #                 'assemblyCost' вместо 'assembleCost'),
        #   StartPickerOrderEvent,
        #   OrderDelivered.
        # На выходе биллинг-события:
        #   BillingDelivered.
        #
        # Проверяем, что:
        # - в BillingDelivered не попадает сборка.
        # - int-овые 'promoId' и 'promocodeId' нормально принимаются.
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
                            'currency': 'EUR',
                            'createdAt': '2020-10-24T18:30:30+03:00',
                            'goodsPrice': 20,
                            'deliveryPrice': 10,
                            'assemblyCost': 5,
                            'promo': {'promoId': 7111, 'promoDiscount': 4},
                            'promocode': {
                                'promocodeId': 7112,
                                'promocodeType': 'some_promocode_type_711',
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
                            'currency': 'RUB',
                            'updatedAt': '2020-10-24T18:39:39+03:00',
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assemblyCost': 500,
                            'promo': {'promoId': 7121, 'promoDiscount': 400},
                            'promocode': {
                                'promocodeId': 7122,
                                'promocodeType': 'some_promocode_type_712',
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
                        kind='OrderDelivered',
                        data={'deliveredAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
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
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            # данные берутся из OrderChanged с doc_id=712
                            'currency': 'RUB',
                            'service_fee_amount': '9',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '400',  # promoDiscount
                                    'type': 'marketing',
                                    'product_type': 'retail',
                                    'entity_id': '7121',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': (
                                        '100'
                                    ),  # promocodeGoodsDiscount
                                    'type': 'some_promocode_type_712',
                                    'product_type': 'retail',
                                    'entity_id': '7122',
                                },
                            ],
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
            id='Event "BillingDelivered" without '
            'promocodeAssemblyDiscount created.',
        ),
        # На входе сырые события:
        #   OrderCreated (без скидок).
        #   StartPickerOrderEvent,
        #   OrderDelivered.
        # На выходе биллинг-события:
        #   BillingDelivered.
        #
        # Проверяем, что нулевые скидки не попадают
        # в BillingDelivered['products'].
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
                            'goodsPrice': 20,
                            'deliveryPrice': 10,
                            'assemblyCost': 5,
                            'promo': {
                                'promoId': 'some_promo_id_711',
                                'promoDiscount': 0,
                            },
                            'promocode': {
                                'promocodeId': 'some_promocode_id_711',
                                'promocodeType': 'some_promocode_type_711',
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
                        kind='OrderDelivered',
                        data={'deliveredAt': consts.OTHER_DATE},
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
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
                            'courier_id': None,
                            'picker_id': consts.PICKER_ID,
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'service_fee_amount': '9',
                            'products': [],
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
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingDelivered" without discounts created.',
        ),
    ],
)
async def test_billing_delivered(
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
