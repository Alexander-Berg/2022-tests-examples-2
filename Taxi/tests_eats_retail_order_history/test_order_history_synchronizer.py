# pylint: disable=too-many-lines

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


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_synchronize_order_history_200(
        environment, load_json, create_order, check_response,
):
    create_order()
    environment.set_default()
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
        expected_response=load_json('expected_response.json'),
    )


@pytest.mark.now('2021-08-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'status_for_customer, final_status',
    [
        ['confirmed', 'auto_complete'],
        ['arrived_to_customer', 'auto_complete'],
        ['delivered', 'delivered'],
        ['cancelled', 'cancelled'],
    ],
)
async def test_synchronize_order_history_auto_complete_200(
        environment,
        now,
        load_json,
        create_order_from_json,
        check_response,
        status_for_customer,
        final_status,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    order_data = load_json('db_order.json')
    order_data['order']['status_updated_at'] = now - datetime.timedelta(
        seconds=4000,
    )
    order_data['order']['status_for_customer'] = status_for_customer
    create_order_from_json(order_data)
    environment.set_default()
    expected_response = load_json('expected_response.json')
    expected_response['status_for_customer'] = final_status
    await check_response(
        expected_status=200,
        orders_retrieve_called=0,
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
        expected_response=expected_response,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3(auto_complete_batch_size=1, sync_duration=3600)
async def test_synchronize_order_history_batch_auto_complete_200(
        taxi_eats_retail_order_history,
        mocked_time,
        now,
        testpoint,
        environment,
        load_json,
        create_order_from_json,
        get_order,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    order_data = load_json('db_order.json')
    status_for_customer = 'in_delivery'
    order_data['order']['status_for_customer'] = status_for_customer
    order_ids = []
    for i in range(10, -2, -1):
        order_data['order']['order_nr'] = str(len(order_ids))
        order_data['order']['status_updated_at'] = now - datetime.timedelta(
            seconds=i * 1000,
        )
        order_ids.append(create_order_from_json(order_data))
    environment.set_default()

    @testpoint('eats-retail-order-history::autocomplete')
    def order_autocomplete(arg):
        mocked_time.sleep(3600)

    await taxi_eats_retail_order_history.run_distlock_task(
        'order-history-synchronizer',
    )

    assert order_autocomplete.times_called == 8
    for idx, order_id in enumerate(order_ids):
        order = get_order(order_id)
        assert order['status_for_customer'] == (
            'auto_complete' if idx < 7 else status_for_customer
        )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'status_for_customer, final_status',
    [
        ['confirmed', 'auto_complete'],
        ['arrived_to_customer', 'auto_complete'],
        ['delivered', 'delivered'],
        ['cancelled', 'cancelled'],
    ],
)
async def test_synchronize_order_history_auto_complete_missing_fields_404(
        environment,
        now,
        create_order,
        get_order,
        check_response,
        status_for_customer,
        final_status,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    order_id = create_order(
        status_updated_at=now - datetime.timedelta(seconds=4000),
        status_for_customer=status_for_customer,
    )
    environment.set_default()
    await check_response(
        expected_status=404,
        orders_retrieve_called=0,
        order_revision_list_called=0,
        order_revision_details_called=0,
        place_assortment_details_called=0,
        retrieve_places_called=0,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        cargo_driver_voiceforwardings_called=0,
        vgw_api_forwardings_called=0,
    )
    assert get_order(order_id)['status_for_customer'] == final_status


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_synchronize_order_history_order_retrieved_200(
        environment, load_json, create_order, check_response, now,
):
    create_order(
        status_for_customer='awaiting_payment',
        order_created_at=now,
        delivery_address='ул. Пушкина, д. Колотушкина',
        delivery_point={'latitude': 59.93507, 'longitude': 30.33811},
    )
    environment.set_default()
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
        expected_response=load_json('expected_response.json'),
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_synchronize_order_history_first_revision_fetched_no_images_200(
        environment,
        load_json,
        create_order,
        create_order_item,
        check_response,
        now,
):
    order_id = create_order(
        status_for_customer='arrived_to_customer',
        order_created_at=now,
        delivery_address='ул. Пушкина, д. Колотушкина',
        delivery_point={'latitude': 59.93507, 'longitude': 30.33811},
        place_id=utils.PLACE_ID,
        currency_code='RUB',
        original_cost_for_customer=780,
    )
    create_order_item(
        order_id=order_id,
        name='Макароны',
        origin_id='item-0',
        count=1,
        cost_for_customer=50,
    )
    create_order_item(
        order_id=order_id,
        name='Дырка от бублика',
        origin_id='item-1',
        count=2,
        cost_for_customer=300,
    )
    create_order_item(
        order_id=order_id,
        name='Виноград',
        origin_id='item-2',
        weight=(500, 'GRM'),
        cost_for_customer=100,
    )
    create_order_item(
        order_id=order_id,
        name='Малина',
        origin_id='item-3',
        weight=(600, 'GRM'),
        cost_for_customer=120,
    )
    create_order_item(
        order_id=order_id,
        name='Сыр',
        origin_id='item-4',
        weight=(200, 'GRM'),
        cost_for_customer=200,
    )
    create_order_item(
        order_id=order_id,
        name='Спички',
        origin_id='item-7',
        count=1,
        cost_for_customer=10,
    )
    environment.set_default()
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=1,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=load_json('expected_response.json'),
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_synchronize_order_history_first_revision_fetched_200(
        environment,
        load_json,
        create_order,
        create_order_item,
        check_response,
        now,
):
    order_id = create_order(
        status_for_customer='arrived_to_customer',
        order_created_at=now,
        delivery_address='ул. Пушкина, д. Колотушкина',
        delivery_point={'latitude': 59.93507, 'longitude': 30.33811},
        place_id=utils.PLACE_ID,
        currency_code='RUB',
        original_cost_for_customer=780,
    )
    create_order_item(
        order_id=order_id,
        name='Макароны',
        origin_id='item-0',
        images=['https://yandex.ru/item-0.jpg'],
        count=1,
        cost_for_customer=50,
    )
    create_order_item(
        order_id=order_id,
        name='Дырка от бублика',
        origin_id='item-1',
        images=['https://yandex.ru/item-1.jpg'],
        count=2,
        cost_for_customer=300,
    )
    create_order_item(
        order_id=order_id,
        name='Виноград',
        origin_id='item-2',
        images=['https://yandex.ru/item-2.jpg'],
        weight=(500, 'GRM'),
        cost_for_customer=100,
    )
    create_order_item(
        order_id=order_id,
        name='Малина',
        origin_id='item-3',
        images=['https://yandex.ru/item-3.jpg'],
        weight=(600, 'GRM'),
        cost_for_customer=120,
    )
    create_order_item(
        order_id=order_id,
        name='Сыр',
        origin_id='item-4',
        images=['https://yandex.ru/item-4.jpg'],
        weight=(200, 'GRM'),
        cost_for_customer=200,
    )
    create_order_item(
        order_id=order_id,
        name='Спички',
        origin_id='item-7',
        images=['https://yandex.ru/item-7.jpg'],
        count=1,
        cost_for_customer=10,
    )
    environment.set_default()
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
        expected_response=load_json('expected_response.json'),
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_synchronize_order_history_place_info_fetched_200(
        environment,
        load_json,
        create_order,
        create_order_item,
        check_response,
        now,
):
    order_id = create_order(
        status_for_customer='arrived_to_customer',
        order_created_at=now,
        delivery_address='ул. Пушкина, д. Колотушкина',
        delivery_point=(59.93507, 30.33811),
        place_id=utils.PLACE_ID,
        place_slug=utils.PLACE_SLUG,
        place_name=utils.PLACE_NAME,
        is_marketplace=True,
        city=utils.CITY,
        place_address=utils.PLACE_ADDRESS,
        currency_code='RUB',
        original_cost_for_customer=780,
        brand_id=1,
        brand_slug=utils.BRAND_SLUG,
        brand_name='Магнит',
        place_business='shop',
        our_picking=True,
        region_id=str(utils.REGION_ID_RU),
    )
    create_order_item(
        order_id=order_id,
        name='Макароны',
        origin_id='item-0',
        images=['https://yandex.ru/item-0.jpg'],
        count=1,
        cost_for_customer=50,
    )
    create_order_item(
        order_id=order_id,
        name='Дырка от бублика',
        origin_id='item-1',
        images=['https://yandex.ru/item-1.jpg'],
        count=2,
        cost_for_customer=300,
    )
    create_order_item(
        order_id=order_id,
        name='Виноград',
        origin_id='item-2',
        images=['https://yandex.ru/item-2.jpg'],
        weight=(500, 'GRM'),
        cost_for_customer=100,
    )
    create_order_item(
        order_id=order_id,
        name='Малина',
        origin_id='item-3',
        images=['https://yandex.ru/item-3.jpg'],
        weight=(600, 'GRM'),
        cost_for_customer=120,
    )
    create_order_item(
        order_id=order_id,
        name='Сыр',
        origin_id='item-4',
        images=['https://yandex.ru/item-4.jpg'],
        weight=(200, 'GRM'),
        cost_for_customer=200,
    )
    create_order_item(
        order_id=order_id,
        name='Спички',
        origin_id='item-7',
        images=['https://yandex.ru/item-7.jpg'],
        count=1,
        cost_for_customer=10,
    )
    environment.set_default()
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=1,
        place_assortment_details_called=1,
        retrieve_places_called=0,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=load_json('expected_response.json'),
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_synchronize_order_history_no_yandex_uid(
        taxi_eats_retail_order_history,
        environment,
        load_json,
        create_order_from_json,
        get_order,
):
    order_data = load_json('db_order_only_retail_info.json')
    order_id = create_order_from_json(order_data)
    environment.set_default()

    db_order = get_order(order_id)
    assert db_order['yandex_uid'] is None
    prev_status_updated_at = db_order['status_updated_at']

    await taxi_eats_retail_order_history.run_distlock_task(
        'order-history-synchronizer',
    )
    assert environment.mock_orders_retrieve.times_called == 0
    assert environment.mock_order_revision_list.times_called == 0
    assert environment.mock_order_revision_details.times_called == 0
    assert environment.mock_place_assortment_details.times_called == 0
    assert environment.mock_retrieve_places.times_called == 0
    assert environment.mock_get_picker_order.times_called == 0
    assert environment.mock_eda_candidates_list.times_called == 0
    assert environment.mock_performer_location.times_called == 0
    assert environment.mock_vgw_api_forwardings.times_called == 0
    assert environment.mock_cargo_voiceforwarding.times_called == 0
    assert environment.mock_cart_diff.times_called == 0

    db_order = get_order(order_id)
    assert db_order['yandex_uid'] is None
    assert db_order['status_updated_at'] == prev_status_updated_at


@pytest.mark.now('2021-08-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'status_for_customer',
    ['confirmed', 'arrived_to_customer', 'delivered', 'cancelled'],
)
async def test_synchronize_order_history_auto_complete_no_yandex_uid(
        environment,
        taxi_eats_retail_order_history,
        now,
        get_order,
        load_json,
        create_order_from_json,
        status_for_customer,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    order_data = load_json('db_order.json')
    order_data['order']['yandex_uid'] = None
    order_data['order']['status_updated_at'] = now - datetime.timedelta(
        seconds=4000,
    )
    order_data['order']['status_for_customer'] = status_for_customer
    order_id = create_order_from_json(order_data)
    environment.set_default()
    await taxi_eats_retail_order_history.run_distlock_task(
        'order-history-synchronizer',
    )
    db_order = get_order(order_id)
    assert db_order['yandex_uid'] is None
    assert db_order['status_for_customer'] == status_for_customer


@pytest.mark.now('2021-09-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
@pytest.mark.parametrize(
    'picking_status, do_call_by_picking_status',
    [
        (None, False),
        ('new', False),
        ('picking', True),
        ('paid', True),
        ('cancelled', False),
        ('complete', True),
    ],
)
@pytest.mark.parametrize(
    'last_notification_type, do_call_by_last_notification',
    [
        (None, True),
        ('first_retail_order_changes', False),
        ('order_in_delivery', True),
    ],
)
async def test_synchronize_order_history_track_changes(
        taxi_eats_retail_order_history,
        stq,
        environment,
        create_order,
        create_customer_notification,
        now,
        picking_status,
        do_call_by_picking_status,
        last_notification_type,
        do_call_by_last_notification,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    create_order()
    environment.set_default()
    environment.add_picker_order(picking_status=picking_status)

    if last_notification_type is not None:
        create_customer_notification(
            notification_type_v2=last_notification_type,
            idempotency_token=f'{utils.ORDER_ID}_{last_notification_type}',
            status_for_customer='in_delivery',
        )

    await taxi_eats_retail_order_history.run_distlock_task(
        'order-history-synchronizer',
    )

    do_call = do_call_by_picking_status and do_call_by_last_notification
    assert stq.eats_retail_order_history_notify_customer.times_called == int(
        do_call,
    )

    if not do_call:
        return

    task_info = stq.eats_retail_order_history_notify_customer.next_call()
    del task_info['kwargs']['log_extra']
    events = task_info['kwargs'].pop('retail_order_changes')
    notification_type = 'first_retail_order_changes'
    assert task_info['kwargs'] == {
        'notification_type': notification_type,
        'idempotency_token': f'{utils.ORDER_ID}_{notification_type}',
        'time': now.isoformat(),
        'level': 'INFO',
        'order_nr': utils.ORDER_ID,
    }

    expected_events = {
        'add': sorted(
            [
                {'id': 'item-6', 'name': 'Клубника'},
                {'id': 'item-5', 'name': 'Сливы'},
            ],
            key=lambda x: x['id'],
        ),
    }
    if utils.PickingStatus[picking_status] >= utils.PickingStatus.paid:
        expected_events['remove'] = sorted(
            [
                {'id': 'item-7', 'name': 'Спички'},
                {'id': 'item-3', 'name': 'Малина'},
                {'id': 'item-2', 'name': 'Виноград'},
            ],
            key=lambda x: x['id'],
        )
    assert sorted(events, key=lambda x: x) == sorted(
        expected_events, key=lambda x: x,
    )
