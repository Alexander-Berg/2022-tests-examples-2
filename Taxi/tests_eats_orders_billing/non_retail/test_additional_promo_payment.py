import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args, input_events, expected_input_stq_fail,'
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
                    kind='OrderChanged',
                    external_event_ref=f'{consts.ORDER_NR}/OrderChanged/3',
                    data=helpers.make_order_changed_ie(
                        goods_price='300.00',
                        goods_gmv_amount='300.00',
                        revision_id='3',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            1,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
            ],
            id='Test order not finished',
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
                    kind='OrderChanged',
                    external_event_ref=f'{consts.ORDER_NR}/OrderChanged/3',
                    data=helpers.make_order_changed_ie(
                        goods_price='300.00',
                        goods_gmv_amount='300.00',
                        revision_id='3',
                    ),
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
            id='Test order finished after changes',
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
                    kind='CourierAssigned',
                    external_event_ref=f'{consts.ORDER_NR}/CourierAssigned/2',
                    data=helpers.make_courier_assigned(
                        courier_id='courier_id_2',
                        assigned_at=consts.OTHER_DATE,
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
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(
                        delivered_at='2020-12-26T01:22:45+03:00',
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
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='300'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(
                        delivered_at='2020-12-26T01:22:45+03:00',
                    ),
                ),
            ],
            id='Test promo is zero',
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
                    kind='CourierAssigned',
                    external_event_ref=f'{consts.ORDER_NR}/CourierAssigned/2',
                    data=helpers.make_courier_assigned(
                        courier_id='courier_id_2',
                        assigned_at=consts.OTHER_DATE,
                    ),
                ),
                helpers.make_db_row(
                    kind='OrderChanged',
                    external_event_ref=f'{consts.ORDER_NR}/OrderChanged/3',
                    data=helpers.make_order_changed_ie(
                        goods_price='300.00',
                        goods_gmv_amount='300.00',
                        revision_id='3',
                        promo=helpers.make_promo(
                            promo_discount='50', promo_id='promo_id',
                        ),
                    ),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(
                        delivered_at='2020-12-26T01:22:45+03:00',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            4,
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
                    external_id=f'OrderChanged/{consts.ORDER_NR}/'
                    f'3/additional_promo_payment',
                    kind='additional_promo_payment',
                    data=helpers.make_additional_payment_data(amount='50'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(
                        delivered_at='2020-12-26T01:22:45+03:00',
                        products=[
                            helpers.make_order_delivered_products(
                                product_id='product/native/native',
                                value_amount='50',
                                payment_type='marketing',
                                product_type='product',
                                entity_id='promo_id',
                            ),
                        ],
                    ),
                ),
            ],
            id='Test happy path',
        ),
    ],
)
async def test_additional_promo_payment(
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
