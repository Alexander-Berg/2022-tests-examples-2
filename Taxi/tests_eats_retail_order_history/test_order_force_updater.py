import datetime

import pytest

from . import utils


@pytest.fixture(name='check_response')
def _check_response(
        taxi_eats_retail_order_history, assert_response, assert_mocks,
):
    async def do_check_response(
            expected_status,
            orders_retrieve_called,
            order_revision_list_called,
            order_revision_details_called,
            place_assortment_details_called,
            retrieve_places_called,
            get_picker_order_called,
            cart_diff_called,
            eda_candidates_list_called,
            performer_location_called,
            vgw_api_forwardings_called,
            cargo_driver_voiceforwardings_called,
            expected_response=None,
    ):
        for i in range(2):
            if i == 0:
                await taxi_eats_retail_order_history.run_distlock_task(
                    'order-force-updater',
                )
            else:
                await assert_response(expected_status, expected_response)
            assert_mocks(
                orders_retrieve_called[i]
                if isinstance(orders_retrieve_called, (list, tuple))
                else orders_retrieve_called,
                order_revision_list_called,
                order_revision_details_called,
                place_assortment_details_called,
                retrieve_places_called,
                get_picker_order_called,
                cart_diff_called,
                eda_candidates_list_called,
                performer_location_called,
                vgw_api_forwardings_called,
                cargo_driver_voiceforwardings_called,
            )

    return do_check_response


@pytest.mark.now('2021-07-31T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'place_id, brand_id, order_nrs, history_updated_after, '
    'history_updated_before, expected_orders',
    [
        (None, None, None, None, None, []),
        ('place_id_1', None, None, None, None, ['order_nr_1', 'order_nr_2']),
        ('place_id_2', None, None, None, None, ['order_nr_3']),
        ('place_id_0', None, None, None, None, []),
        (None, '2', None, None, None, ['order_nr_3', 'order_nr_4']),
        (None, '6', None, None, None, ['order_nr_7']),
        (None, None, ['order_nr_1'], None, None, ['order_nr_1']),
        (
            None,
            None,
            ['order_nr_1', 'order_nr_3'],
            None,
            None,
            ['order_nr_1', 'order_nr_3'],
        ),
        (
            None,
            None,
            None,
            '2021-08-02T12:00:00.123456+00:00',
            None,
            [f'order_nr_{i}' for i in range(2, 8)],
        ),
        (
            None,
            None,
            None,
            '2021-08-03T12:00:00.123456+00:00',
            None,
            [f'order_nr_{i}' for i in range(3, 8)],
        ),
        (
            None,
            None,
            None,
            None,
            '2021-08-07T12:00:00.123456+00:00',
            [f'order_nr_{i}' for i in range(1, 8)],
        ),
        (
            None,
            None,
            None,
            None,
            '2021-08-06T12:00:00.123456+00:00',
            [f'order_nr_{i}' for i in range(1, 7)],
        ),
        (
            None,
            None,
            None,
            None,
            '2021-08-06T15:00:00.123456+03:00',
            [f'order_nr_{i}' for i in range(1, 7)],
        ),
        (
            None,
            None,
            None,
            None,
            '2021-08-05T12:00:00.123456+00:00',
            [f'order_nr_{i}' for i in range(1, 6)],
        ),
        (
            None,
            None,
            None,
            '2021-08-03T12:00:00.123456+00:00',
            '2021-08-05T12:00:00.123456+00:00',
            [f'order_nr_{i}' for i in range(3, 6)],
        ),
        ('place_id_3', '2', None, None, None, ['order_nr_4']),
        (
            'place_id_1',
            '1',
            ['order_nr_1'],
            '2021-08-01T12:00:00.123456+00:00',
            '2021-08-01T12:00:00.123456+00:00',
            ['order_nr_1'],
        ),
        (
            'place_id_1',
            '2',
            ['order_nr_1'],
            '2021-08-01T12:00:00.123456+00:00',
            '2021-08-01T12:00:00.123456+00:00',
            [],
        ),
    ],
)
async def test_synchronize_order_history_force_update(
        taxi_eats_retail_order_history,
        environment,
        load_json,
        create_order_from_json,
        experiments3,
        place_id,
        brand_id,
        order_nrs,
        history_updated_after,
        history_updated_before,
        expected_orders,
):
    experiments3.add_experiment3_from_marker(
        utils.synchronizer_force_update_cfg3(
            place_id=place_id,
            brand_id=brand_id,
            order_nrs=order_nrs,
            history_updated_after=history_updated_after,
            history_updated_before=history_updated_before,
        ),
        None,
    )
    orders = load_json('db_orders_force_update.json')['orders']
    for order in orders:
        create_order_from_json(order)
    await taxi_eats_retail_order_history.run_distlock_task(
        'order-force-updater',
    )
    actual_orders = []
    for _ in range(environment.mock_orders_retrieve.times_called):
        args = environment.mock_orders_retrieve.next_call()
        actual_orders.append(args['request'].json['range']['order_id'])
    assert sorted(actual_orders) == sorted(expected_orders)


@utils.synchronizer_config3()
@utils.synchronizer_force_update_cfg3(order_nrs=[utils.ORDER_ID])
@pytest.mark.parametrize(
    'status, picking_status, is_cart_diff_404, is_cart_diff_empty, '
    'do_change_diff, order_revision_details_called, '
    'place_assortment_details_called',
    [
        # diff меняется, так как получили новый cart_diff
        ('cooking', 'picked_up', False, False, True, 1, 1),
        ('cooking', 'picking', False, False, True, 1, 1),
        # diff не меняется, так как cart_diff в случае отсутствия
        # достаём из базы
        ('cooking', 'picked_up', True, None, False, 1, 1),
        ('cooking', 'picking', True, None, False, 1, 1),
        # diff меняется, так как берем изменения из последней ревизии из-за
        # того, что заказ уже готов
        ('delivered', 'complete', False, False, True, 2, 2),
        ('delivered', 'complete', True, None, True, 2, 2),
    ],
)
@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
async def test_synchronize_order_history_force_update_cart_diff(
        environment,
        load_json,
        create_order_from_json,
        get_order_by_order_nr,
        check_response,
        now,
        status,
        picking_status,
        is_cart_diff_404,
        is_cart_diff_empty,
        do_change_diff,
        order_revision_details_called,
        place_assortment_details_called,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    order = load_json('db_order_force_update_cart_diff.json')
    create_order_from_json(order)
    revision_ids = ['aaa', 'bbb']
    environment.add_user_order(status=status)
    environment.add_order_customer_service(
        revision_id=revision_ids[0],
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='50.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000',
                name='Макароны',
                cost_for_customer='50.00',
                origin_id='item-0',
            ),
        ],
    )
    # между двумя этими ревизиями были добавлены чебупели, периодик обновил
    # заказ, он перешел в автокомплит и перестал обновляться, затем чебупели
    # были удалены, а в макаронах обновилась цена
    environment.add_order_customer_service(
        revision_id=revision_ids[1],
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='70.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000',
                name='Макароны',
                cost_for_customer='70.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_place_product(
        origin_id=f'item-0', image_urls=[f'https://yandex.ru/item-0.jpg'],
    )
    environment.add_place_info(our_picking=True, business='shop')
    environment.add_picker_order(picking_status=picking_status)
    if not is_cart_diff_404:
        update = []
        picked_items = []
        if not is_cart_diff_empty:
            update = [
                {
                    'from_item': environment.make_picker_item(
                        id_='item-0',
                        is_catch_weight=False,
                        quantity=1,
                        price='50.00',
                        measure_value=200,
                        measure_quantum=200,
                        quantum_quantity=1,
                        quantum_price='50.00',
                        name='Макароны',
                    ),
                    'to_item': environment.make_picker_item(
                        id_='item-0',
                        is_catch_weight=False,
                        quantity=1,
                        price='70.00',
                        measure_value=200,
                        measure_quantum=200,
                        quantum_quantity=1,
                        quantum_price='70.00',
                        name='Макароны',
                        price_updated_at=now.isoformat(),
                    ),
                },
            ]
            picked_items = ['item-0']
        environment.add_order_diff(
            add=[],
            remove=[],
            update=update,
            replace=[],
            soft_delete=[],
            picked_items=picked_items,
        )
    expected_response = load_json(
        'expected_response_force_update_change_diff.json'
        if do_change_diff
        else 'expected_response_force_update_do_not_change_diff.json',
    )
    expected_response['picking_status'] = picking_status
    expected_response['status_for_customer'] = status
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=order_revision_details_called,
        place_assortment_details_called=place_assortment_details_called,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )
    cart_diff = get_order_by_order_nr(utils.ORDER_ID)['cart_diff']
    if is_cart_diff_404 or is_cart_diff_empty:
        assert cart_diff == order['order']['cart_diff']
    else:
        assert cart_diff != order['order']['cart_diff']
