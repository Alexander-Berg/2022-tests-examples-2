import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args, input_events,expected_input_stq_fail,'
    'times_called,expected_requests',
    [
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='One OrderCreated event, happy path',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00',
                        goods_gmv_amount='100.00',
                        place_compensations=[
                            {'type': 'delivery', 'amount': '1.00'},
                        ],
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                    place_compensations=[
                        {
                            'product_id': 'delivery/native/native',
                            'product_type': 'delivery',
                            'amount': '1',
                        },
                    ],
                ),
            ],
            id='One OrderCreated event with place_compensations',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderPickedUp',
                    external_event_ref=f'{consts.ORDER_NR}/OrderPickedUp',
                    data=helpers.make_order_picked_up_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='One OrderPickedUp event, happy path',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='OrderChanged',
                    external_event_ref=f'{consts.ORDER_NR}/OrderChanged/3',
                    data=helpers.make_order_changed_ie(
                        goods_price='300.00',
                        goods_gmv_amount='300.00',
                        revision_id='3',
                    ),
                ),
                helpers.make_db_row(
                    kind='OrderChanged',
                    external_event_ref=f'{consts.ORDER_NR}/OrderChanged/2',
                    data=helpers.make_order_changed_ie(
                        goods_price='200.00',
                        goods_gmv_amount='200.00',
                        revision_id='2',
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='300'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='Test last revision',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}'
                    f'/AccountingCorrection',
                    data=helpers.make_accounting_correction_ie(
                        amount='50.00',
                        correction_id='1',
                        account_correction_type='goods',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'AccountingCorrection/{consts.ORDER_NR}'
                    f'/1/order_gmv/1',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='150'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='Test accounting correction, happy path',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}'
                    f'/AccountingCorrection/1',
                    data=helpers.make_accounting_correction_ie(
                        amount='50.00',
                        correction_id='1',
                        account_correction_type='delivery',
                    ),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}'
                    f'/AccountingCorrection/2',
                    data=helpers.make_accounting_correction_ie(
                        amount='135.00',
                        correction_id='2',
                        account_correction_type='goods',
                    ),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}'
                    f'/AccountingCorrection/3',
                    data=helpers.make_accounting_correction_ie(
                        amount='-65.00',
                        correction_id='3',
                        account_correction_type='goods',
                    ),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}'
                    f'/AccountingCorrection/4',
                    data=helpers.make_accounting_correction_ie(
                        amount='10.00',
                        correction_id='4',
                        account_correction_type='goods',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'AccountingCorrection/{consts.ORDER_NR}'
                    f'/1/order_gmv/4',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='180'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='Test complex accounting correction '
            'with delivery and negative amounts',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00',
                        goods_gmv_amount='100.00',
                        promo=helpers.make_promo(
                            promo_id=consts.ENTITY_ID, promo_discount='10.00',
                        ),
                        promocode=helpers.make_promocode(
                            promocode_id=consts.ENTITY_ID,
                            promocode_type='sorrycode',
                            promocode_goods_discount='15.00',
                            promocode_delivery_discount='20.00',
                            promocode_assembly_discount='30.00',
                        ),
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(
                        [
                            helpers.make_order_delivered_products(
                                product_id='product/native/native',
                                product_type='product',
                                payment_type='marketing',
                                value_amount='10',
                            ),
                            helpers.make_order_delivered_products(
                                product_id='product/native/native',
                                product_type='product',
                                payment_type='compensation_promocode',
                                value_amount='15',
                            ),
                        ],
                    ),
                ),
            ],
            id='Test OrderDelivered with incentives',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}'
                    f'/AccountingCorrection/1',
                    data=helpers.make_accounting_correction_ie(
                        amount='50.00',
                        correction_id='1',
                        account_correction_type='delivery',
                        place_id='134075',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            2,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'AccountingCorrection/{consts.ORDER_NR}'
                    f'/1/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
            ],
            id='Getting place info from AccountingCorrecting event',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00',
                        goods_gmv_amount='100.00',
                        delivery_price='10.00',
                        order_type='marketplace',
                        promocode=helpers.make_promocode(
                            promocode_id=consts.ENTITY_ID,
                            promocode_goods_discount='100.00',
                            promocode_delivery_discount='10.00',
                        ),
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(rules='marketplace'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(
                        products=[
                            helpers.make_order_delivered_products(
                                product_id='product/native/marketplace',
                                product_type='product',
                                payment_type='marketing_promocode',
                                value_amount='100',
                            ),
                            helpers.make_order_delivered_products(
                                product_id='delivery/native/marketplace',
                                product_type='delivery',
                                payment_type='marketing_promocode',
                                value_amount='10',
                            ),
                        ],
                    ),
                ),
            ],
            id='Promocode for marketplace delivery',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00',
                        goods_gmv_amount='100.00',
                        delivery_price='10.00',
                        order_type='marketplace',
                        dynamic_price='20.00',
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(rules='marketplace'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(
                        gmv_amount='100', dynamic_price='20',
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='Passing dynamic price',
        ),
    ],
)
async def test_order_delivered(
        stq_runner,
        experiments3,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called,
        expected_requests,
        mock_customer_service_retrieve,
        mock_customer_service_retrieve_new,
        mock_order_revision_list,
        mock_order_revision_list_new,
):
    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])
    mock_order_revision_list_new(revisions=[{'origin_revision_id': '123-321'}])

    experiments3.add_experiment(**helpers.make_use_core_revisions_exp())

    await helpers.input_events_process_test_func(
        stq_runner,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called,
        expected_requests,
    )
