# pylint: disable=too-many-lines

import datetime
import decimal

import pytest

from . import utils


EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS = {
    'adult_image_placeholder_with_resize': {
        'resized_url_pattern': 'https://yandex.ru/adult-{w}x{h}.jpg',
        'url': 'https://yandex.ru/adult.jpg',
    },
}


@pytest.fixture(name='check_response')
def _check_response(assert_response, assert_mocks):
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
        # второй итерацией проверяем, что при повторном запросе данные берутся
        # из базы, а ручки других сервисов не трогаем
        for _ in range(2):
            await assert_response(expected_status, expected_response)
            assert_mocks(
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
            )

    return do_check_response


@pytest.fixture(name='check_response_after_sync')
def _check_response_after_sync(
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
                    'order-history-synchronizer',
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


@pytest.mark.now('2021-08-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_change_item_type(
        load_json,
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order(status_for_customer=None)
        check_response = check_response_after_sync
    else:
        create_order(status_for_customer=None, yandex_uid=None)
    environment.add_user_order(status='delivered')
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='1',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='110.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='110.00',
                origin_id='item-0',
                weight=110,
            ),
        ],
    )
    environment.add_place_info(our_picking=False, business='shop')
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=load_json('expected_response_change_item_type.json'),
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'original_weight, final_weight, price_updated',
    [
        [200, 200, True],
        [300, 200, False],
        [0, 200, False],
        [300, 0, False],
        [0, 0, True],
    ],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_zero_weight_200(
        create_order,
        environment,
        check_response,
        check_response_after_sync,
        load_json,
        original_weight,
        final_weight,
        price_updated,
        sync,
):
    if sync:
        create_order(status_for_customer=None)
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    original_cost = '150.00'
    final_cost = '100.00'
    environment.add_user_order(status='delivered')
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer=original_cost,
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer=original_cost,
                origin_id='item-0',
                weight=original_weight,
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='1',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer=final_cost,
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer=final_cost,
                origin_id='item-0',
                weight=final_weight,
            ),
        ],
    )
    environment.add_place_info(our_picking=False, business='shop')
    expected_response = load_json('expected_response_zero_weight.json')
    update = expected_response['diff']['update'][0]
    expected_response['original_items'][0]['weight']['value'] = original_weight
    update['from_item']['weight']['value'] = original_weight
    update['to_item']['weight']['value'] = final_weight
    if not price_updated:
        del update['to_item']['price_updated_at']

    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'status, order_revision_details_called, place_assortment_details_called',
    [('cooking', 1, 1), ('delivered', 2, 2)],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_price_updated_200(
        load_json,
        create_order,
        environment,
        check_response,
        check_response_after_sync,
        now,
        status,
        sync,
        order_revision_details_called,
        place_assortment_details_called,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    now = now.replace(tzinfo=datetime.timezone.utc)
    items_count = 7
    revision_ids = ['aaa', 'bbb']
    environment.add_user_order(status=status)
    environment.add_order_customer_service(
        revision_id=revision_ids[0],
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='910.00',
        type_='retail',
        composition_products=[
            # не изменилось ничего
            environment.make_composition_product(
                id_='item_000-1',
                name='Макароны',
                cost_for_customer='50.00',
                origin_id='item-0',
            ),
            # изменилась только цена (невесовой товар)
            environment.make_composition_product(
                id_='item_111-1',
                name='Jinchu-Maru',
                cost_for_customer='100.00',
                origin_id='item-1',
            ),
            # изменилась только цена (весовой товар)
            environment.make_composition_product(
                id_='item_222-1',
                name='Креветки',
                weight=600,
                cost_for_customer='60.00',
                origin_id='item-2',
            ),
            # изменилось только количество (невесовой товар)
            environment.make_composition_product(
                id_='item_333-1',
                name='Дырка от бублика',
                cost_for_customer='150.00',
                origin_id='item-3',
            ),
            environment.make_composition_product(
                id_='item_333-2',
                name='Дырка от бублика',
                cost_for_customer='150.00',
                origin_id='item-3',
            ),
            # изменилось только количество (весовой товар)
            environment.make_composition_product(
                id_='item_444-1',
                name='Изюм',
                weight=500,
                cost_for_customer='100.00',
                origin_id='item-4',
            ),
            environment.make_composition_product(
                id_='item_444-1',
                name='Изюм',
                weight=500,
                cost_for_customer='100.00',
                origin_id='item-4',
            ),
            # изменилась цена и количество (cost_for_customer изменился)
            environment.make_composition_product(
                id_='item_555-1',
                name='Сгущенка',
                cost_for_customer='100.00',
                origin_id='item-5',
            ),
            # изменилась цена и количество (cost_for_customer не изменился)
            environment.make_composition_product(
                id_='item_666-1',
                name='Йогурт',
                cost_for_customer='100.00',
                origin_id='item-6',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id=revision_ids[1],
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение ' 'поручений по заказу',
        cost_for_customer='1020.00',
        type_='retail',
        composition_products=[
            # не изменилось ничего
            environment.make_composition_product(
                id_='item_000-1',
                name='Макароны',
                cost_for_customer='50.00',
                origin_id='item-0',
            ),
            # изменилась только цена (невесовой товар)
            environment.make_composition_product(
                id_='item_111-1',
                name='Jinchu-Maru',
                cost_for_customer='200.00',
                origin_id='item-1',
            ),
            # изменилась только цена (весовой товар)
            environment.make_composition_product(
                id_='item_222-1',
                name='Креветки',
                weight=600,
                cost_for_customer='300.00',
                origin_id='item-2',
            ),
            # изменилось только количество (невесовой товар)
            environment.make_composition_product(
                id_='item_333-1',
                name='Дырка от бублика',
                cost_for_customer='150.00',
                origin_id='item-3',
            ),
            # изменилось только количество (весовой товар)
            environment.make_composition_product(
                id_='item_444-1',
                name='Изюм',
                weight=500,
                cost_for_customer='100.00',
                origin_id='item-4',
            ),
            # изменилась цена и количество (cost_for_customer изменился)
            environment.make_composition_product(
                id_='item_555-1',
                name='Сгущенка',
                cost_for_customer='60.00',
                origin_id='item-5',
            ),
            environment.make_composition_product(
                id_='item_555-2',
                name='Сгущенка',
                cost_for_customer='60.00',
                origin_id='item-5',
            ),
            # изменилась цена и количество (cost_for_customer не изменился)
            environment.make_composition_product(
                id_='item_666-1',
                name='Йогурт',
                cost_for_customer='50.00',
                origin_id='item-6',
            ),
            environment.make_composition_product(
                id_='item_666-2',
                name='Йогурт',
                cost_for_customer='50.00',
                origin_id='item-6',
            ),
        ],
    )
    for i in range(items_count):
        environment.add_place_product(
            origin_id=f'item-{i}',
            image_urls=[f'https://yandex.ru/item-{i}.jpg'],
        )
    environment.add_place_info(our_picking=True, business='shop')
    environment.add_picker_order(picking_status='complete')
    environment.add_order_diff(
        add=[],
        remove=[],
        update=[
            # изменилась только цена (невесовой товар)
            {
                'from_item': environment.make_picker_item(
                    id_='item-1',
                    is_catch_weight=False,
                    quantity=1,
                    price='100.00',
                    measure_value=200,
                    measure_quantum=200,
                    quantum_quantity=1,
                    quantum_price='100.00',
                    name='Jinchu-Maru',
                ),
                'to_item': environment.make_picker_item(
                    id_='item-1',
                    is_catch_weight=False,
                    quantity=1,
                    price='200.00',
                    measure_value=200,
                    measure_quantum=200,
                    quantum_quantity=1,
                    quantum_price='200.00',
                    name='Jinchu-Maru',
                    price_updated_at=now.isoformat(),
                ),
            },
            # изменилась только цена (весовой товар)
            {
                'from_item': environment.make_picker_item(
                    id_='item-2',
                    is_catch_weight=True,
                    quantity=0.6,
                    price='100.00',
                    measure_quantum=1000,
                    quantum_quantity=0.6,
                    quantum_price='100.00',
                    name='Креветки',
                ),
                'to_item': environment.make_picker_item(
                    id_='item-2',
                    is_catch_weight=True,
                    quantity=0.6,
                    price='500.00',
                    measure_quantum=1000,
                    quantum_quantity=0.6,
                    quantum_price='500.00',
                    name='Креветки',
                    price_updated_at=now.isoformat(),
                ),
            },
            # изменилось только количество (невесовой товар)
            {
                'from_item': environment.make_picker_item(
                    id_='item-3',
                    is_catch_weight=False,
                    quantity=2,
                    price='150.00',
                    measure_value=10,
                    measure_quantum=10,
                    quantum_quantity=2,
                    quantum_price='150.00',
                    name='Дырка от бублика',
                ),
                'to_item': environment.make_picker_item(
                    id_='item-3',
                    is_catch_weight=False,
                    quantity=1,
                    price='150.00',
                    measure_value=10,
                    measure_quantum=10,
                    quantum_quantity=1,
                    quantum_price='150.00',
                    name='Дырка от бублика',
                ),
            },
            # изменилось только количество (весовой товар)
            {
                'from_item': environment.make_picker_item(
                    id_='item-4',
                    is_catch_weight=True,
                    quantity=1,
                    price='200.00',
                    measure_quantum=1000,
                    quantum_quantity=1,
                    quantum_price='200.00',
                    name='Изюм',
                ),
                'to_item': environment.make_picker_item(
                    id_='item-4',
                    is_catch_weight=True,
                    quantity=0.5,
                    price='200.00',
                    measure_quantum=1000,
                    quantum_quantity=0.5,
                    quantum_price='200.00',
                    name='Изюм',
                ),
            },
            # изменилась цена и количество (cost_for_customer изменился)
            {
                'from_item': environment.make_picker_item(
                    id_='item-5',
                    is_catch_weight=False,
                    quantity=1,
                    price='100.00',
                    measure_value=200,
                    measure_quantum=200,
                    quantum_quantity=1,
                    quantum_price='100.00',
                    name='Сгущенка',
                ),
                'to_item': environment.make_picker_item(
                    id_='item-5',
                    is_catch_weight=False,
                    quantity=2,
                    price='60.00',
                    measure_value=200,
                    measure_quantum=200,
                    quantum_quantity=2,
                    quantum_price='60.00',
                    name='Сгущенка',
                    price_updated_at=now.isoformat(),
                ),
            },
            # изменилась цена и количество (cost_for_customer не изменился)
            {
                'from_item': environment.make_picker_item(
                    id_='item-6',
                    is_catch_weight=False,
                    quantity=1,
                    price='100.00',
                    measure_value=200,
                    measure_quantum=200,
                    quantum_quantity=1,
                    quantum_price='100.00',
                    name='Йогурт',
                ),
                'to_item': environment.make_picker_item(
                    id_='item-6',
                    is_catch_weight=False,
                    quantity=2,
                    price='50.00',
                    measure_value=200,
                    measure_quantum=200,
                    quantum_quantity=2,
                    quantum_price='50.00',
                    name='Йогурт',
                    price_updated_at=now.isoformat(),
                ),
            },
        ],
        replace=[],
        soft_delete=[],
        picked_items=[f'item-{i}' for i in range(items_count)],
    )
    expected_response = load_json('expected_response_price_updated.json')
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


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'status_for_customer, picking_status, is_paid',
    [
        ['cooking', 'picking', False],
        ['cooking', 'picked_up', False],
        ['cooking', 'paid', True],
        ['cooking', 'complete', True],
        # таких комбинаций статусов в действительности быть не должно
        ['awaiting_payment', 'picked_up', False],
        ['confirmed', 'picked_up', False],
    ],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_cooking_not_finished_200(
        load_json,
        environment,
        create_order,
        status_for_customer,
        picking_status,
        is_paid,
        sync,
        check_response,
        check_response_after_sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    environment.change_order_status(
        utils.YANDEX_UID, utils.ORDER_ID, status_for_customer,
    )
    environment.add_picker_order(picking_status=picking_status)
    expected_response = load_json(
        'expected_response_cooking_not_finished_paid.json'
        if is_paid
        else 'expected_response_cooking_not_finished_not_paid.json',
    )
    expected_response['status_for_customer'] = status_for_customer
    expected_response['picking_status'] = picking_status
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=1,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'status_for_customer, picking_status,',
    [
        ['cooking', 'assigned'],
        ['cooking', 'cancelled'],
        ['cooking', None],
        ['cancelled', 'assigned'],
        ['cancelled', 'cancelled'],
        ['cancelled', 'complete'],
        ['cancelled', None],
    ],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_not_picked_200(
        load_json,
        environment,
        create_order,
        status_for_customer,
        picking_status,
        sync,
        check_response,
        check_response_after_sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    # оставляем только информацию о первой ревизии
    environment.order_revisions[utils.ORDER_ID] = dict(
        list(environment.order_revisions[utils.ORDER_ID].items())[:1],
    )
    expected_response = load_json('expected_response_not_picked.json')
    environment.change_order_status(
        utils.YANDEX_UID, utils.ORDER_ID, status_for_customer,
    )
    expected_response['status_for_customer'] = status_for_customer
    check_response_params = dict(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=1,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )
    if status_for_customer == 'cancelled':
        check_response_params['get_picker_order_called'] = 0
        check_response_params['cart_diff_called'] = 0
    if picking_status is not None:
        environment.add_picker_order(picking_status=picking_status)
    else:
        check_response_params['cart_diff_called'] = 0
    if status_for_customer != 'cancelled' and picking_status is not None:
        expected_response['picking_status'] = picking_status
    else:
        for key in (
                'picking_status',
                'courier_phone_id',
                'picker_phone_id',
                'forwarded_courier_phone',
                'forwarded_picker_phone',
        ):
            del expected_response[key]
        for key in (
                'eda_candidates_list_called',
                'performer_location_called',
                'vgw_api_forwardings_called',
        ):
            check_response_params[key] = 0
        environment.picker_orders = {}
    await check_response(**check_response_params)


@pytest.mark.now('2021-11-22T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
@pytest.mark.parametrize(
    'status_for_customer, picking_status, spent, do_fetch_picker_order, '
    'do_ignore_aligning',
    [
        # нет смысла проверять status_for_customer <= cooking,
        # так как дифф в этом случае строится по корзине
        ('delivered', 'complete', '100.00', False, True),
        ('in_delivery', 'complete', '100.00', False, True),
        ('delivered', 'paid', '100.00', True, True),
        ('delivered', 'complete', None, False, False),
        ('delivered', 'complete', '200.00', False, False),
    ],
)
async def test_order_updater_ignore_aligning_200(
        load_json,
        environment,
        create_order_from_json,
        sync,
        check_response,
        check_response_after_sync,
        status_for_customer,
        picking_status,
        spent,
        do_fetch_picker_order,
        do_ignore_aligning,
):
    order_data = load_json('db_order_ignore_aligning.json')
    order_data['order']['picking_status'] = picking_status
    order_data['order']['cost_for_place'] = spent

    if sync:
        check_response = check_response_after_sync
        # устанавливаем yandex_uid только для периодика, чтобы первый запрос
        # в ручку не пытался отдать закэшированный результат
        order_data['order']['yandex_uid'] = utils.YANDEX_UID

    create_order_from_json(order_data)

    environment.add_place_info(business='shop', our_picking=True)
    environment.add_user_order(status=status_for_customer)
    environment.add_picker_order(picking_status=picking_status, spent=spent)
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='120.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Макароны',
                cost_for_customer='70.00',
                origin_id='item-0',
            ),
            environment.make_composition_product(
                id_='item_111-0',
                name='Виноград',
                cost_for_customer='50.00',
                weight=500,
                origin_id='item-1',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='1',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Макароны',
                cost_for_customer='60.00',
                origin_id='item-0',
            ),
            environment.make_composition_product(
                id_='item_111-0',
                name='Виноград',
                cost_for_customer='30.00',
                weight=500,
                origin_id='item-1',
            ),
            environment.make_composition_product(
                id_='cost_for_place_change_item',
                name='Дополнительная сумма',
                cost_for_customer='10.00',
                origin_id='cost_for_place_change_item',
            ),
        ],
    )
    environment.add_order_diff(
        add=[],
        remove=[],
        update=[],
        replace=[],
        soft_delete=[],
        picked_items=['item-0', 'item-1'],
    )
    environment.add_claim(
        utils.ORDER_ID,
        utils.CLAIM_ID,
        {'phone': '+7(111)1111111', 'ext': '1111', 'ttl_seconds': 3600},
    )

    expected_response = load_json(
        'expected_response_ignore_aligning.json'
        if do_ignore_aligning
        else 'expected_response_do_not_ignore_aligning.json',
    )
    expected_response['status_for_customer'] = status_for_customer
    expected_response['picking_status'] = picking_status

    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=int(do_fetch_picker_order),
        cart_diff_called=int(do_fetch_picker_order),
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=1,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_no_last_revision_data_200(
        mockserver,
        load_json,
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()

    order_revisions = environment.order_revisions[utils.ORDER_ID]
    first_revision_id = next(iter(order_revisions))
    environment.add_order_customer_service(
        revision_id=first_revision_id,
        customer_service_id='delivery',
        customer_service_name='Стоимость доставки',
        cost_for_customer='0.0',
        type_='delivery',
    )
    environment.add_picker_order(picking_status='assigned')

    prev_mock = environment.mock_order_revision_details

    @mockserver.json_handler(
        '/eats-order-revision/v1/order-revision/customer-services/details',
    )
    async def _eats_order_revision_details(request):
        assert request.method == 'POST'
        order_id = request.json['order_id']
        revision_id = request.json['origin_revision_id']
        order_revisions = environment.order_revisions.get(order_id, {})
        if not order_revisions or revision_id != next(iter(order_revisions)):
            return mockserver.make_response(status=404)
        return await prev_mock(request)

    environment.mock_order_revision_details = _eats_order_revision_details

    expected_response = load_json(
        'expected_response_cooking_no_last_revision.json',
    )
    for key in (
            'picking_cost_for_customer',
            'order_refund_amount',
            'tips',
            'restaurant_tips',
    ):
        del expected_response[key]
    expected_response['original_total_cost_for_customer'] = expected_response[
        'original_cost_for_customer'
    ]
    expected_response['total_cost_for_customer'] = expected_response[
        'final_cost_for_customer'
    ]
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'business, our_picking, cart_diff_404',
    [['store', True, False], ['shop', False, False], ['shop', True, True]],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_no_cart_diff_200(
        load_json,
        environment,
        create_order,
        business,
        our_picking,
        cart_diff_404,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order(our_picking=our_picking)
        check_response = check_response_after_sync
    else:
        create_order(our_picking=our_picking, yandex_uid=None)
    environment.set_default()
    if cart_diff_404:
        environment.order_diff = {}
    environment.add_place_info(
        place_id=utils.PLACE_ID,
        place_slug=utils.PLACE_SLUG,
        brand_id=utils.BRAND_ID,
        brand_slug=utils.BRAND_SLUG,
        brand_name=utils.BRAND_NAME,
        our_picking=our_picking,
        business=business,
    )
    expected_response = load_json('expected_response_no_cart_diff.json')
    is_retail = business == 'shop'
    cart_diff_requested = is_retail and our_picking
    expected_response['place']['business'] = business
    if not cart_diff_requested:
        for key in (
                'picking_status',
                'courier_phone_id',
                'picker_phone_id',
                'forwarded_courier_phone',
                'forwarded_picker_phone',
        ):
            del expected_response[key]
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=cart_diff_requested,
        cart_diff_called=cart_diff_requested,
        eda_candidates_list_called=cart_diff_requested,
        performer_location_called=0,
        vgw_api_forwardings_called=cart_diff_requested,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'retrieve_places_response',
    [{'status': 500}, {'json': {'places': [], 'not_found_place_ids': []}}],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_place_not_found_404(
        mockserver,
        environment,
        create_order,
        retrieve_places_response,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _eats_catalog_storage_retrieve_places(request):
        return mockserver.make_response(**retrieve_places_response)

    environment.mock_retrieve_places = _eats_catalog_storage_retrieve_places
    await check_response(
        expected_status=404,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'place_assortment_response',
    [
        {'status': 500},
        {
            'status': 404,
            'json': {
                'error': 'not_found_place',
                'message': 'Магазин не найден',
            },
        },
    ],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_place_assortment_not_found_200(
        mockserver,
        load_json,
        environment,
        create_order,
        place_assortment_response,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    environment.add_picker_order(picking_status='assigned')

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _eats_products_place_assortment_details(request):
        return mockserver.make_response(**place_assortment_response)

    environment.mock_place_assortment_details = (
        _eats_products_place_assortment_details
    )
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=load_json(
            'expected_response_no_place_assortment.json',
        ),
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_revisions_not_found_404(
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    environment.order_revisions = {}
    await check_response(
        expected_status=404,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=0,
        retrieve_places_called=0,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'business', ['restaurant', 'store', 'pharmacy', 'shop', 'zapravki'],
)
@pytest.mark.parametrize(
    'claims, has_phone',
    [
        ([], False),
        (
            [
                {
                    'id': utils.CLAIM_ID,
                    'phone': utils.COURIER_PHONE,
                    'created_ts': None,
                },
            ],
            True,
        ),
        (
            [
                {
                    'id': '0',
                    'phone': None,
                    'created_ts': '2021-06-02T12:00:00Z',
                },
                {
                    'id': '1',
                    'phone': None,
                    'created_ts': '2021-06-03T12:00:00Z',
                },
                {
                    'id': utils.CLAIM_ID,
                    'phone': utils.COURIER_PHONE,
                    'created_ts': '2021-06-05T12:00:00Z',
                },
                {
                    'id': '2',
                    'phone': None,
                    'created_ts': '2021-06-04T12:00:00Z',
                },
            ],
            True,
        ),
        (
            [
                *[
                    {
                        'id': str(i),
                        'phone': None,
                        'created_ts': f'2021-06-0{i}T12:00:00Z',
                    }
                    for i in range(1, 10)
                ],
                {
                    'id': utils.CLAIM_ID,
                    'phone': utils.COURIER_PHONE,
                    'created_ts': '2021-07-01T12:00:00Z',
                },
            ],
            True,
        ),
        (
            [
                {
                    'id': utils.CLAIM_ID,
                    'phone': utils.COURIER_PHONE,
                    'created_ts': '2021-07-01T12:00:00Z',
                },
                *[
                    {
                        'id': str(i),
                        'phone': None,
                        'created_ts': f'2021-06-0{i}T12:00:00Z',
                    }
                    for i in range(9, 0)
                ],
            ],
            True,
        ),
    ],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_shop_picking_200(
        environment,
        experiments3,
        load_json,
        create_order,
        check_response,
        check_response_after_sync,
        business,
        claims,
        has_phone,
        sync,
):
    if sync:
        create_order(our_picking=False)
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    environment.add_place_info(our_picking=False, business=business)
    for claim in claims:
        environment.add_claim(
            utils.ORDER_ID, claim['id'], claim['phone'], claim['created_ts'],
        )

    expected_response = load_json('expected_response_no_cart_diff.json')
    expected_response['place']['business'] = business
    if has_phone:
        expected_response['forwarded_courier_phone'] = '+7(800)5553535,,1234'
    else:
        del expected_response['forwarded_courier_phone']
    for key in (
            'picking_status',
            'courier_phone_id',
            'picker_phone_id',
            'forwarded_picker_phone',
    ):
        del expected_response[key]
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=int(bool(claims)),
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'picking_status, get_picker_order_called',
    [['picked_up', 1], ['paid', 1], ['complete', 0]],
)
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_retail_info_synchronized_200(
        environment,
        load_json,
        create_order_from_json,
        get_order,
        check_response,
        check_response_after_sync,
        picking_status,
        get_picker_order_called,
        sync,
):
    order_data = load_json('db_order_only_retail_info.json')
    if sync:
        check_response = check_response_after_sync
        order_data['order']['yandex_uid'] = utils.YANDEX_UID
    order_data['order']['picking_status'] = picking_status
    order_id = create_order_from_json(order_data)
    environment.set_default()
    environment.picker_orders = {}
    environment.order_diff = {}
    expected_response = load_json('expected_response.json')
    expected_response['picking_status'] = picking_status
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=get_picker_order_called,
        cart_diff_called=0,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )

    db_order = get_order(order_id)
    assert db_order['yandex_uid'] == utils.YANDEX_UID
    assert db_order['customer_id'] == utils.CUSTOMER_ID


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_order_updater_diff_not_updated_200(
        environment,
        load_json,
        create_order_from_json,
        check_response_after_sync,
):
    environment.set_default()
    environment.change_order_status(
        utils.YANDEX_UID, utils.ORDER_ID, 'delivered',
    )
    order_data = load_json('db_order.json')
    order_data['order']['status_for_customer'] = 'confirmed'
    order_data['order']['last_revision_id'] = list(
        environment.order_revisions[utils.ORDER_ID].keys(),
    )[-1]
    create_order_from_json(order_data)
    expected_response = load_json('expected_response.json')
    await check_response_after_sync(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=0,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_order_updater_images_updated_200(
        environment,
        load_json,
        create_order_from_json,
        check_response_after_sync,
):
    environment.set_default()
    order_data = load_json('db_order_no_diff_images.json')
    order_data['order']['last_revision_id'] = list(
        environment.order_revisions[utils.ORDER_ID].keys(),
    )[-1]
    create_order_from_json(order_data)
    expected_response = load_json('expected_response.json')
    await check_response_after_sync(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('update_item_name', [False, True])
async def test_order_updater_diff_name_updated_200(
        environment,
        taxi_config,
        load_json,
        create_order_from_json,
        check_response_after_sync,
        # parametrize
        update_item_name,
):
    taxi_config.set_values(
        {
            'EATS_RETAIL_ORDER_HISTORY_ORDER_ITEM_UPDATE_SETTINGS': {
                'should_update_item_name_nomenclature': update_item_name,
            },
        },
    )

    environment.set_default()
    order_data = load_json('db_order_no_diff_images.json')
    order_data['order']['last_revision_id'] = list(
        environment.order_revisions[utils.ORDER_ID].keys(),
    )[-1]
    create_order_from_json(order_data)
    if update_item_name:
        expected_response = load_json(
            'expected_response_diff_name_changed.json',
        )
    else:
        expected_response = load_json('expected_response.json')
    await check_response_after_sync(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.config(
    EATS_RETAIL_ORDER_HISTORY_ORDER_ITEM_UPDATE_SETTINGS={
        'should_update_item_name_nomenclature': True,
    },
)
async def test_order_updater_diff_changed_items(
        environment,
        load_json,
        create_order_from_json,
        check_response_after_sync,
):
    """
    Тест проверяет что если в ответе eats-nomenclature нет данных для
    предыдущей версии айтема, но есть для новой версии, то эти данные
    применятся к новой версии.
    """

    environment.set_default()
    order_data = load_json('db_order_no_diff_images.json')
    order_data['order']['last_revision_id'] = list(
        environment.order_revisions[utils.ORDER_ID].keys(),
    )[-1]

    # Заполняем данные только для элемента, айди которого есть только
    # в to_item и ни в каких других айтемах его нету
    environment.place_assortment = {}
    environment.add_place_product(
        origin_id='item-6',
        image_urls=['https://yandex.ru/item-6.jpg'],
        adult=True,
    )

    create_order_from_json(order_data)
    expected_response = load_json('expected_response_to_item_updated.json')

    await check_response_after_sync(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('update_item_name', [False, True])
async def test_order_updater_orig_name_updated_200(
        environment,
        taxi_config,
        load_json,
        create_order_from_json,
        check_response_after_sync,
        # parametrize
        update_item_name,
):
    taxi_config.set_values(
        {
            'EATS_RETAIL_ORDER_HISTORY_ORDER_ITEM_UPDATE_SETTINGS': {
                'should_update_item_name_nomenclature': update_item_name,
            },
        },
    )

    environment.set_default()
    order_data = load_json('db_order_no_orig_images.json')
    order_data['order']['last_revision_id'] = list(
        environment.order_revisions[utils.ORDER_ID].keys(),
    )[-1]
    create_order_from_json(order_data)
    if update_item_name:
        expected_response = load_json(
            'expected_response_orig_name_changed.json',
        )
    else:
        expected_response = load_json('expected_response.json')
    await check_response_after_sync(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=1,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-08-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'sync, orders_retrieve_called', [(False, 1), (True, (0, 1))],
)
async def test_order_updater_retail_info_synchronized_order_not_found_404(
        mockserver,
        environment,
        get_order,
        load_json,
        create_order_from_json,
        check_response,
        check_response_after_sync,
        sync,
        orders_retrieve_called,
):
    order_data = load_json('db_order_only_retail_info.json')
    if sync:
        check_response = check_response_after_sync
    order_id = create_order_from_json(order_data)
    environment.set_default()

    @mockserver.json_handler('/eats-core-orders-retrieve/orders/retrieve')
    def _eats_core_orders_retrieve(request):
        return mockserver.make_response(status=404)

    environment.mock_orders_retrieve = _eats_core_orders_retrieve

    db_order = get_order(order_id)
    prev_status_updated_at = db_order['status_updated_at']

    await check_response(
        expected_status=404,
        orders_retrieve_called=orders_retrieve_called,
        order_revision_list_called=0,
        order_revision_details_called=0,
        place_assortment_details_called=0,
        retrieve_places_called=0,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
    )

    db_order = get_order(order_id)
    assert db_order['yandex_uid'] == utils.YANDEX_UID
    assert db_order['customer_id'] == utils.CUSTOMER_ID
    assert db_order['status_updated_at'] > prev_status_updated_at


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_no_performer_location_200(
        mockserver,
        environment,
        load_json,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    environment.add_picker_order(picking_status='assigned')

    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _eda_candidates_list_by_ids(request):
        return mockserver.make_response(status=404)

    environment.mock_eda_candidates_list = _eda_candidates_list_by_ids

    @mockserver.json_handler('/eats-core/v1/supply/performer-location')
    def _eats_core_performer_location(request):
        return mockserver.make_response(status=404)

    environment.mock_performer_location = _eats_core_performer_location

    expected_response = load_json(
        'expected_response_no_performer_location.json',
    )
    del expected_response['forwarded_picker_phone']
    del expected_response['forwarded_courier_phone']
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=1,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_forwarding_not_created_200(
        mockserver,
        environment,
        load_json,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order()
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None)
    environment.set_default()
    environment.add_picker_order(picking_status='assigned')

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_api_forwardings(request):
        return mockserver.make_response(status=404)

    environment.mock_vgw_api_forwardings = _vgw_api_forwardings

    expected_response = load_json(
        'expected_response_no_performer_location.json',
    )
    del expected_response['forwarded_picker_phone']
    del expected_response['forwarded_courier_phone']
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@utils.extra_fee_tanker_ids_config3()
@pytest.mark.translations(**utils.TRANSLATIONS)
@utils.synchronizer_config3()
@utils.get_fee_description_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_service_fee(
        load_json,
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    service_fee = 19.99
    service_fee_type = 'service_fee'
    if sync:
        create_order(status_for_customer=None)
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None, status_for_customer=None)
    environment.add_user_order(status='delivered')
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='fees',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer=str(service_fee),
        type_=service_fee_type,
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='1',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='110.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='110.00',
                origin_id='item-0',
                weight=110,
            ),
        ],
    )
    environment.add_place_info(our_picking=False, business='shop')
    expected_response = load_json('expected_response_change_item_type.json')
    expected_response['delivery_cost_for_customer'] = str(service_fee)
    expected_response['total_cost_for_customer'] = str(
        float(expected_response['total_cost_for_customer']) + service_fee,
    )
    expected_response['original_total_cost_for_customer'] = str(
        float(expected_response['original_total_cost_for_customer'])
        + service_fee,
    )
    expected_response['extra_fees'] = [
        {
            'code': service_fee_type,
            'value': str(service_fee),
            'description': 'Сервисный сбор',
        },
    ]
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@utils.get_fee_description_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_last_revision_closed(
        load_json,
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order(status_for_customer=None)
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None, status_for_customer=None)
    environment.add_user_order(status='delivered')
    environment.order_revisions_tags = {'1': ['closed']}
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='1',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='110.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='110.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_order_customer_service(
        revision_id='2',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='0.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='0.00',
                origin_id='item-0',
            ),
        ],
    )
    environment.add_place_info(our_picking=False, business='shop')
    expected_response = load_json(
        'expected_response_last_revision_closed.json',
    )
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.discounts_experiment3(True)
@utils.extra_fee_tanker_ids_config3()
@utils.discount_tanker_ids_config3()
@pytest.mark.translations(**utils.TRANSLATIONS)
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_discounts(
        load_json,
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        get_order_by_order_nr,
        get_order_items,
        sync,
):
    if sync:
        create_order(status_for_customer=None)
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None, status_for_customer=None)
    environment.add_user_order(status='delivered')
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
                discounts=[{'discount_index': 0, 'discount_amount': '42.00'}],
            ),
        ],
        discounts=[
            {
                'discount_amount': '42.00',
                'info': {
                    'code': 'PROMOCODE',
                    'discount_money': '42.00',
                    'discriminator_type': 'eda_core_promocode',
                },
            },
        ],
    )
    environment.add_order_customer_service(
        revision_id='1',
        customer_service_id='retail-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='997.00',
        type_='retail',
        composition_products=[
            environment.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='99.00',
                origin_id='item-0',
                discounts=[
                    {'discount_index': 0, 'discount_amount': '42.00'},
                    {'discount_index': 1, 'discount_amount': '1.00'},
                ],
            ),
            environment.make_composition_product(
                id_='item_111-0',
                name='Груши',
                cost_for_customer='200.00',
                origin_id='item-1',
                discounts=[{'discount_index': 0, 'discount_amount': '24.00'}],
            ),
            environment.make_composition_product(
                id_='item_222-0',
                name='Бананы',
                cost_for_customer='300.00',
                origin_id='item-2',
                discounts=[{'discount_index': 1, 'discount_amount': '99.00'}],
            ),
            environment.make_composition_product(
                id_='item_333-0',
                name='Кокосы',
                cost_for_customer='398.00',
                origin_id='item-3',
                discounts=[
                    {'discount_index': 0, 'discount_amount': '4.00'},
                    {'discount_index': 2, 'discount_amount': '1.00'},
                    {'discount_index': 3, 'discount_amount': '2.00'},
                ],
            ),
        ],
        discounts=[
            {
                'discount_amount': '70.00',
                'info': {
                    'discriminator_type': 'eda_core_promocode',
                    'code': 'PROMOCODE',
                    'discount_money': '70.00',
                    'discount_percents': '10.00',
                    'discount_limit': '5000.00',
                },
            },
            {
                'discount_amount': '100.00',
                'info': {
                    'discriminator_type': 'eda_core_promo',
                    'id': 'discount_id',
                    'discount_type': 'discount_type',
                    'discount_provider': 'place',
                },
            },
            {
                'discount_amount': '1.00',
                'info': {
                    'discriminator_type': 'eda_core_promo',
                    'id': 'discount_id',
                    'discount_type': 'discount_type',
                    'discount_provider': 'place',
                },
            },
            {
                'discount_amount': '2.00',
                'info': {
                    'discriminator_type': 'eats_discount',
                    'discount_type': 'discount_type',
                    'discount_provider': 'place',
                    'id': 'discount_id',
                    'external_id': 'discount_external_id',
                },
            },
        ],
    )
    environment.add_place_info(our_picking=False, business='shop')
    expected_response = load_json('expected_response_discounts.json')
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )

    order = get_order_by_order_nr(utils.ORDER_ID)
    # assert order costs
    assert order['original_cost_for_customer'] == 100
    assert order['original_cost_without_discounts'] == 142
    assert order['final_cost_for_customer'] == 997
    assert order['final_cost_without_discounts'] == 1170

    # assert order discounts
    original_discounts = environment.order_revisions[utils.ORDER_ID]['0'][
        'discounts'
    ]
    final_discounts = environment.order_revisions[utils.ORDER_ID]['1'][
        'discounts'
    ]
    for order_field, discounts in (
            ('original_discounts', original_discounts),
            ('final_discounts', final_discounts),
    ):
        for discount_i, discount in enumerate(discounts):
            order_discount = dict(order[order_field][discount_i]._asdict())
            assert order_discount['discount_amount'] == decimal.Decimal(
                discount['discount_amount'],
            )
            order_discount_info = dict(order_discount['info']._asdict())
            discount_info = discount['info']
            discount_fields = [
                'discriminator_type',
                'code',
                'discount_provider',
                'discount_type',
                'id',
                'external_id',
            ]
            discounts_decimal_fields = [
                'discount_money',
                'discount_percents',
                'discount_limit',
            ]
            for discount_field in discount_fields + discounts_decimal_fields:
                if discount_field in discount_info:
                    value = discount_info[discount_field]
                    if discount_field in discounts_decimal_fields:
                        value = decimal.Decimal(value)
                    assert order_discount_info[discount_field] == value
                else:
                    assert order_discount_info[discount_field] is None

    order_items = get_order_items(order['id'])
    # assert original order items costs
    assert order_items[0]['cost_for_customer'] == 100
    assert order_items[0]['cost_without_discounts'] == 142

    # assert original order items discounts
    composition_products = environment.order_revisions[utils.ORDER_ID]['0'][
        'customer_services'
    ][0]['details']['composition_products']
    for order_item_i, order_item in enumerate(order_items):
        order_item_discounts = order_item['discounts']
        discounts = composition_products[order_item_i]['discounts']
        for discount_i, discount in enumerate(discounts):
            order_item_discount = dict(
                order_item_discounts[discount_i]._asdict(),
            )
            assert (
                order_item_discount['discount_index']
                == discount['discount_index']
            )
            assert order_item_discount['discount_amount'] == decimal.Decimal(
                discount['discount_amount'],
            )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.discounts_experiment3(True)
@utils.extra_fee_tanker_ids_config3()
@utils.discount_tanker_ids_config3()
@utils.synchronizer_config3()
@pytest.mark.parametrize('sync', [False, True])
async def test_order_updater_tanker_error_fallback(
        load_json,
        environment,
        create_order,
        check_response,
        check_response_after_sync,
        sync,
):
    if sync:
        create_order(status_for_customer=None)
        check_response = check_response_after_sync
    else:
        create_order(yandex_uid=None, status_for_customer=None)
    environment.add_user_order(status='delivered')
    for i in range(2):
        environment.add_order_customer_service(
            revision_id=str(i),
            customer_service_id='retail-product',
            customer_service_name='Расходы на исполнение поручений по заказу',
            cost_for_customer='100.00',
            type_='retail',
            composition_products=[
                environment.make_composition_product(
                    id_='item_000-0',
                    name='Яблоки',
                    cost_for_customer='100.00',
                    origin_id='item-0',
                    discounts=[
                        {'discount_index': 0, 'discount_amount': '42.00'},
                        {'discount_index': 1, 'discount_amount': '1.00'},
                        {'discount_index': 2, 'discount_amount': '2.00'},
                    ],
                ),
            ],
            discounts=[
                {
                    'discount_amount': '42.00',
                    'info': {
                        'discriminator_type': 'eda_core_promocode',
                        'code': 'PROMOCODE',
                        'discount_money': '42.00',
                    },
                },
                {
                    'discount_amount': '1.00',
                    'info': {
                        'discriminator_type': 'eda_core_promo',
                        'id': 'discount_id',
                        'discount_type': 'discount_type',
                        'discount_provider': 'place',
                    },
                },
                {
                    'discount_amount': '2.00',
                    'info': {
                        'discriminator_type': 'eats_discount',
                        'discount_type': 'discount_type',
                        'discount_provider': 'place',
                        'id': 'discount_id',
                        'external_id': 'discount_external_id',
                    },
                },
            ],
        )
    environment.add_order_customer_service(
        revision_id='0',
        customer_service_id='fees',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='19.00',
        type_='service_fee',
    )
    environment.add_place_info(our_picking=False, business='shop')
    expected_response = load_json(
        'expected_response_tanker_error_fallback.json',
    )
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'expected_json',
    [
        pytest.param('expected_response_adult.json'),
        pytest.param(
            'expected_response_adult_image.json',
            marks=(
                pytest.mark.config(
                    EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS=(
                        EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS
                    ),
                ),
            ),
        ),
    ],
)
async def test_order_updater_adult(
        environment,
        load_json,
        create_order_from_json,
        check_response_after_sync,
        expected_json,
):
    """
    Тест проверяет что если в ответе eats-nomenclature товары помечены
    признаком adult=True, то это свойство применится к элементам в ответе,
    и что если включен конфиг EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS, то
    все картинки заменятся на плейсхолдеры
    """

    environment.set_default()
    order_data = load_json('db_order_no_diff_no_orig_images.json')
    order_data['order']['last_revision_id'] = list(
        environment.order_revisions[utils.ORDER_ID].keys(),
    )[-1]

    environment.place_assortment = {}
    for i in range(8):
        environment.add_place_product(
            origin_id=f'item-{i}',
            image_urls=[f'https://yandex.ru/item-{i}.jpg'],
            adult=True,
        )

    create_order_from_json(order_data)
    expected_response = load_json(expected_json)
    await check_response_after_sync(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=0,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
        expected_response=expected_response,
    )
