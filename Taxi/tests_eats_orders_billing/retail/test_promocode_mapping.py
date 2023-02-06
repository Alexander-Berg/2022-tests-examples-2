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
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 0},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': 'sorrycode',
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
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '100',
                                    'type': 'compensation_promocode',
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
            id='OrderCancelled with sorry promocode type',
        ),
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
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 0},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': 'employee',
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
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '100',
                                    'type': 'employee_PC',
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
            id='OrderCancelled with employee promocode type',
        ),
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
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 0},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': 'paid',
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
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '100',
                                    'type': 'paid_PC',
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
            id='OrderCancelled with paid promocode type',
        ),
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
                            'goodsPrice': 2000,
                            'deliveryPrice': 1000,
                            'assembleCost': 500,
                            'promo': {'promoId': None, 'promoDiscount': 0},
                            'promocode': {
                                'promocodeId': None,
                                'promocodeType': 'corporate_all',
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
                            'currency': 'RUB',
                            'products': [
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '2000',
                                    'type': 'payment_not_received',
                                    'product_type': 'retail',
                                },
                                {
                                    'product_id': 'retail/retail/native',
                                    'value_amount': '100',
                                    'type': 'corporate',
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
            id='OrderCancelled with paid corporate type',
        ),
    ],
)
async def test_promocode_mapping(
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
):
    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])

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
