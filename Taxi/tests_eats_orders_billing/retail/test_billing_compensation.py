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
        #   Compensation.
        #   (нет события StartPickerOrderEvent,
        #    нужного для BillingCompensation).
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
                        kind='Compensation',
                        data={
                            'compensationId': consts.COMPENSATION_ID,
                            'compensationAt': consts.OTHER_DATE,
                            'currency': 'RUB',
                            'amount': 200,
                            'items': [
                                {
                                    'type': 'product',
                                    'amount': '100',
                                    'discounts': [
                                        {
                                            'type': 'discount_group_0_0',
                                            'amount': '10.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
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
            # expected_output_stq_args
            None,
            # expected_input_stq_fail
            True,
            id='No event "StartPickerOrderEvent" for case '
            '"Compensation" => "BillingCompensation".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   StartPickerOrderEvent,
        #   Compensation.
        # На выходе биллинг-события:
        #   BillingCompensation.
        #
        # В этом тесте проверяем, что:
        # - в BillingCompensation попадают все items
        # - BillingCompensation['items'] группируются по типу,
        # причем типы 'product' и 'option'
        # превращаются в 'retail' и группируются с ним.
        # - BillingCompensation['items']['discounts'] объединяются по типу.
        # - нормально принимается 'compensationId' типа int
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
                            'promocode': {'promocodeType': 'sorrycode'},
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
                        kind='Compensation',
                        data={
                            'compensationId': int(consts.COMPENSATION_ID),
                            'compensationAt': consts.COMPENSATION_AT,
                            'currency': 'RUB',
                            'amount': 200,
                            'items': [
                                {  # Войдет в группу 0
                                    'type': 'product',
                                    'amount': '100',
                                    'discounts': [
                                        {  # Войдет в подгруппу 0:0
                                            'type': 'discount_group_0_0',
                                            'amount': '10.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'product',
                                    'amount': '200',
                                    'discounts': [
                                        {  # Войдет в подгруппу 0:1
                                            'type': 'discount_group_0_1',
                                            'amount': '20.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'retail',
                                    'amount': '300',
                                    'discounts': [
                                        {  # Войдет в подгруппу 0:0
                                            'type': 'discount_group_0_0',
                                            'amount': '30.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'retail',
                                    'amount': '400',
                                    'discounts': [
                                        {  # Войдет в подгруппу 0:1
                                            'type': 'discount_group_0_1',
                                            'amount': '40.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'option',
                                    'amount': '500',
                                    'discounts': [
                                        {  # Войдет в подгруппу 0:0
                                            'type': 'discount_group_0_0',
                                            'amount': '50.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'option',
                                    'amount': '600',
                                    'discounts': [
                                        {  # Войдет в подгруппу 0:1
                                            'type': 'discount_group_0_1',
                                            'amount': '60.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 1
                                    'type': 'delivery',
                                    'amount': '700',
                                    'discounts': [
                                        {  # Войдет в подгруппу 1:0
                                            'type': 'discount_group_1_0',
                                            'amount': '70.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 1
                                    'type': 'delivery',
                                    'amount': '800',
                                    'discounts': [
                                        {  # Войдет в подгруппу 1:0
                                            'type': 'discount_group_1_0',
                                            'amount': '80.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 1
                                    'type': 'delivery',
                                    'amount': '900',
                                    'discounts': [
                                        {  # Войдет в подгруппу 1:1
                                            'type': 'discount_group_1_1',
                                            'amount': '90.00',
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'product',
                                    'amount': '1000',
                                    'discounts': [
                                        {  # Никуда не войдет
                                            'type': 'discount_group_0_0',
                                            'amount': '100.00',
                                            'discountProvider': 'place',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'retail',
                                    'amount': '1100',
                                    'discounts': [
                                        {  # Никуда не войдет
                                            'type': 'discount_group_0_0',
                                            'amount': '110.00',
                                            'discountProvider': 'place',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'option',
                                    'amount': '1200',
                                    'discounts': [
                                        {  # Никуда не войдет
                                            'type': 'discount_group_0_0',
                                            'amount': '120.00',
                                            'discountProvider': 'place',
                                        },
                                    ],
                                },
                                {  # Группа 1
                                    'type': 'delivery',
                                    'amount': '1300',
                                    'discounts': [
                                        {  # Никуда не войдет
                                            'type': 'discount_group_0_0',
                                            'amount': '130.00',
                                            'discountProvider': 'place',
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
                        kind='BillingCompensation',
                        external_event_ref='BillingCompensation/'
                        f'{consts.ORDER_NR}/{consts.COMPENSATION_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': str(consts.PICKER_ID),
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'items': [
                                {  # Группа 0
                                    'product_id': 'retail/retail/native',
                                    'type': 'retail',
                                    'amount': '5400',
                                    'discounts': [
                                        {  # Подгруппа 0:0
                                            'type': 'sorrycode',
                                            'amount': '210',
                                        },
                                    ],
                                },
                                {  # Группа 1
                                    'product_id': 'delivery/retail/native',
                                    'type': 'delivery',
                                    'amount': '3700',
                                    'discounts': [],
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCompensation" created for case '
            '"Compensation" => "BillingCompensation".',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   StartPickerOrderEvent,
        #   Compensation (с нулевыми скидками).
        # На выходе биллинг-события:
        #   BillingCompensation.
        #
        # В этом тесте проверяем, что:
        # - в BillingCompensation не попадают нулевые скидки.
        # - нормально принимается 'compensationId' типа string
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
                            'promocode': {'promocodeType': 'paid'},
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
                        kind='Compensation',
                        data={
                            'compensationId': str(consts.COMPENSATION_ID),
                            'compensationAt': consts.COMPENSATION_AT,
                            'currency': 'RUB',
                            'amount': 1000,
                            'items': [
                                {  # Войдет в группу 0
                                    'type': 'product',
                                    'amount': '100',
                                    'discounts': [
                                        {  # Никуда не войдет, т.к. 0
                                            'type': 'discount_group_0_0',
                                            'amount': 0,
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 1
                                    'type': 'delivery',
                                    'amount': '900',
                                    'discounts': [
                                        {  # Никуда не войдет, т.к. 0
                                            'type': 'discount_group_1_0',
                                            'amount': 0,
                                            'discountProvider': 'own',
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
                        kind='BillingCompensation',
                        external_event_ref='BillingCompensation/'
                        f'{consts.ORDER_NR}/{consts.COMPENSATION_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': str(consts.PICKER_ID),
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'items': [
                                {  # Группа 0
                                    'product_id': 'retail/retail/native',
                                    'type': 'retail',
                                    'amount': '100',
                                    'discounts': [],
                                },
                                {  # Группа 1
                                    'product_id': 'delivery/retail/native',
                                    'type': 'delivery',
                                    'amount': '900',
                                    'discounts': [],
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCompensation" without '
            'zero-amount discounts created.',
        ),
        # На входе сырые события:
        #   OrderCreated,
        #   StartPickerOrderEvent,
        #   Compensation (с service fee).
        # На выходе биллинг-события:
        #   BillingCompensation.
        #
        # В этом тесте проверяем, что:
        # - в BillingCompensation корректно попадает serviceFee
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
                            'promocode': {'promocodeType': 'paid'},
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
                        kind='Compensation',
                        data={
                            'compensationId': str(consts.COMPENSATION_ID),
                            'compensationAt': consts.COMPENSATION_AT,
                            'currency': 'RUB',
                            'amount': 1000,
                            'items': [
                                {  # Войдет в группу 0
                                    'type': 'product',
                                    'amount': '100',
                                    'discounts': [
                                        {  # Никуда не войдет, т.к. 0
                                            'type': 'discount_group_0_0',
                                            'amount': 0,
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 0
                                    'type': 'service_fee',
                                    'amount': '9',
                                    'discounts': [
                                        {  # Никуда не войдет, т.к. 0
                                            'type': 'discount_group_0_0',
                                            'amount': 0,
                                            'discountProvider': 'own',
                                        },
                                    ],
                                },
                                {  # Войдет в группу 1
                                    'type': 'delivery',
                                    'amount': '900',
                                    'discounts': [
                                        {  # Никуда не войдет, т.к. 0
                                            'type': 'discount_group_1_0',
                                            'amount': 0,
                                            'discountProvider': 'own',
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
                        kind='BillingCompensation',
                        external_event_ref='BillingCompensation/'
                        f'{consts.ORDER_NR}/{consts.COMPENSATION_ID}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'flow_type': 'retail',
                            'transaction_date': consts.COMPENSATION_AT,
                            'compensation_id': str(consts.COMPENSATION_ID),
                            'courier_id': None,
                            'picker_id': str(consts.PICKER_ID),
                            'place_id': str(consts.PLACE_ID),
                            'currency': 'RUB',
                            'service_fee_amount': '9',
                            'items': [
                                {  # Группа 0
                                    'product_id': 'retail/retail/native',
                                    'type': 'retail',
                                    'amount': '100',
                                    'discounts': [],
                                },
                                {  # Группа 1
                                    'product_id': 'delivery/retail/native',
                                    'type': 'delivery',
                                    'amount': '900',
                                    'discounts': [],
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "BillingCompensation" with service fee ',
        ),
    ],
)
async def test_billing_compensation(
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
