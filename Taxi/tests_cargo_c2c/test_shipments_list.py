import pytest


REQUEST_ID = 'b1fe01ddc30247279f806e6c5e210a9f'


async def fetch_shipment_shipment_list(taxi_cargo_c2c, default_pa_headers):
    response = await taxi_cargo_c2c.post(
        '/4.0/pickup-points/v1/shipment/list',
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    if not response.json()['shipments']:
        return None
    shipment = response.json()['shipments'][0]
    shipment.pop('meta')
    return shipment


async def fetch_shipment_deliveries(taxi_cargo_c2c, default_pa_headers):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    if not response.json()['shipments']:
        return None
    shipment = response.json()['shipments'][0]
    shipment.pop('meta')
    return shipment


# delivery interval '2020-11-28T14:00:00+03:00' - '2020-11-28T19:33:20+03:00'
# station work hour
# пн(00:00-21:00), вт(12:00-23:59), ср(00:00-23:59), чт-сб(7:12-23:57), вс -


@pytest.mark.now('2020-11-27T14:00:00+03:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_delivery_interval(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['DEFERRED_COURIER']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert shipment == {
        'id': REQUEST_ID,
        'title': 'завтра с 14:00 до 19:33',
        'description': 'R&G · №100',
        'multiorder': {
            'postpone_button': {'title': 'Хорошо'},
            'receive_button': {
                'title': 'Получить сейчас',
                'subtitle': 'За 15 минут · 0 ₽',
            },
            'visible': True,
        },
        'checkout': {
            'type': 'lavka',
            'service': 'grocery',
            'relative_path': (
                '/hour-slots-checkout/?shipmentOrder=100&vendor=beru&token=%s'
                % REQUEST_ID
            ),
        },
        'icon': {'image_tag': 'delivery_market_icon_for_delivery_state'},
        'closed': False,
        'service': 'lavka',
        'closed_description': {
            'title': 'Склад Яндекс.Go сейчас закрыт :(',
            'message': 'Получить заказ за 15 минут можно с 7:12 до 23:57',
            'close_button': 'Закрыть',
        },
        'dashboard_carousel': {
            'button': {
                'enabled': True,
                'metrica_label': (
                    'SuperApp.Delivery.PultOrder.OrderStatusPreview.DeliverNow'
                ),
                'title': 'Доставить сейчас',
                'subtitle': 'За 15-20 минут',
            },
            'meta': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_number': 1,
                'scenario': 'timeslot',
            },
            'metrica_label': 'SuperApp.Delivery.PultOrder.OrderStatusPreview',
            'timeline': {
                'horizontal': [
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_accepted',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_accepted'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'in_stock',
                        'image_tag': 'delivery_timeline_delivery_in_stock',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_in_stock'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_delivering',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_delivering'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_finished',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_finished'
                        ),
                        'status': 'pending',
                    },
                ],
            },
        },
    }


@pytest.mark.now('2020-11-29T14:00:00+03:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_delivery_interval_overdue_station_close_sun(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['DEFERRED_COURIER']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert shipment == {
        'id': REQUEST_ID,
        'title': 'Получите заказ с 0:00',
        'description': 'R&G · №100',
        'multiorder': {
            'postpone_button': {'title': 'Хорошо'},
            'receive_button': {'title': 'Закрыто'},
            'visible': True,
        },
        'checkout': {
            'type': 'lavka',
            'service': 'grocery',
            'relative_path': (
                '/hour-slots-checkout/?shipmentOrder=100&vendor=beru&token=%s'
                % REQUEST_ID
            ),
        },
        'icon': {'image_tag': 'delivery_market_icon_for_delivery_state'},
        'closed': False,
        'service': 'lavka',
        'closed_description': {
            'title': 'Склад Яндекс.Go сейчас закрыт :(',
            'message': 'Получить заказ за 15 минут можно с 0:00 до 21:00',
            'close_button': 'Закрыть',
        },
        'dashboard_carousel': {
            'button': {
                'enabled': False,
                'metrica_label': (
                    'SuperApp.Delivery.PultOrder.OrderStatusPreview.DeliverNow'
                ),
                'title': 'Станция временно закрыта',
            },
            'meta': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_number': 1,
                'scenario': 'timeslot',
            },
            'metrica_label': 'SuperApp.Delivery.PultOrder.OrderStatusPreview',
            'timeline': {
                'horizontal': [
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_accepted',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_accepted'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'in_stock',
                        'image_tag': 'delivery_timeline_delivery_in_stock',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_in_stock'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_delivering',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_delivering'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_finished',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_finished'
                        ),
                        'status': 'pending',
                    },
                ],
            },
        },
    }


@pytest.mark.now('2020-11-30T22:00:00+00:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_delivery_interval_overdue_station_close_mon(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['DEFERRED_COURIER']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert shipment == {
        'id': REQUEST_ID,
        'title': 'Получите заказ с 12:00',
        'description': 'R&G · №100',
        'multiorder': {
            'postpone_button': {'title': 'Хорошо'},
            'receive_button': {'title': 'Закрыто'},
            'visible': True,
        },
        'checkout': {
            'type': 'lavka',
            'service': 'grocery',
            'relative_path': (
                '/hour-slots-checkout/?shipmentOrder=100&vendor=beru&token=%s'
                % REQUEST_ID
            ),
        },
        'icon': {'image_tag': 'delivery_market_icon_for_delivery_state'},
        'closed': False,
        'service': 'lavka',
        'closed_description': {
            'title': 'Склад Яндекс.Go сейчас закрыт :(',
            'message': 'Получить заказ за 15 минут можно с 12:00 до 23:59',
            'close_button': 'Закрыть',
        },
        'dashboard_carousel': {
            'button': {
                'enabled': False,
                'metrica_label': (
                    'SuperApp.Delivery.PultOrder.OrderStatusPreview.DeliverNow'
                ),
                'title': 'Станция временно закрыта',
            },
            'meta': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_number': 1,
                'scenario': 'timeslot',
            },
            'metrica_label': 'SuperApp.Delivery.PultOrder.OrderStatusPreview',
            'timeline': {
                'horizontal': [
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_accepted',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_accepted'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'in_stock',
                        'image_tag': 'delivery_timeline_delivery_in_stock',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_in_stock'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_delivering',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_delivering'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_finished',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_finished'
                        ),
                        'status': 'pending',
                    },
                ],
            },
        },
    }


@pytest.mark.now('2020-11-30T18:00:00+03:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_delivery_interval_overdue_station_open(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['DEFERRED_COURIER']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert shipment == {
        'id': REQUEST_ID,
        'title': 'Получите заказ',
        'description': 'R&G · №100',
        'multiorder': {
            'postpone_button': {'title': 'Хорошо'},
            'receive_button': {
                'title': 'Получить сейчас',
                'subtitle': 'За 15 минут · 0 ₽',
            },
            'visible': True,
        },
        'checkout': {
            'type': 'lavka',
            'service': 'grocery',
            'relative_path': (
                '/hour-slots-checkout/?shipmentOrder=100&vendor=beru&token=%s'
                % REQUEST_ID
            ),
        },
        'icon': {'image_tag': 'delivery_market_icon_for_delivery_state'},
        'closed': False,
        'service': 'lavka',
        'closed_description': {
            'title': 'Склад Яндекс.Go сейчас закрыт :(',
            'message': 'Получить заказ за 15 минут можно с 0:00 до 21:00',
            'close_button': 'Закрыть',
        },
        'dashboard_carousel': {
            'button': {
                'enabled': True,
                'metrica_label': (
                    'SuperApp.Delivery.PultOrder.OrderStatusPreview.DeliverNow'
                ),
                'title': 'Доставить сейчас',
                'subtitle': 'За 15-20 минут',
            },
            'meta': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_number': 1,
                'scenario': 'timeslot',
            },
            'metrica_label': 'SuperApp.Delivery.PultOrder.OrderStatusPreview',
            'timeline': {
                'horizontal': [
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_accepted',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_accepted'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'in_stock',
                        'image_tag': 'delivery_timeline_delivery_in_stock',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_in_stock'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_delivering',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_delivering'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_finished',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_finished'
                        ),
                        'status': 'pending',
                    },
                ],
            },
        },
    }


@pytest.mark.now('2020-11-26T12:00:00+03:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_on_demand_station_opened(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['ON_DEMAND']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert shipment == {
        'id': REQUEST_ID,
        'title': 'Получите заказ',
        'description': 'R&G · №100',
        'multiorder': {
            'postpone_button': {'title': 'Позже'},
            'receive_button': {'title': 'Получить', 'subtitle': 'За 15 минут'},
            'visible': True,
        },
        'checkout': {
            'type': 'lavka',
            'service': 'grocery',
            'relative_path': (
                '/one-click-checkout/?shipmentOrder=100&vendor=beru&token=%s'
                % REQUEST_ID
            ),
        },
        'icon': {'image_tag': 'delivery_market_icon_for_delivery_state'},
        'closed': False,
        'service': 'lavka',
        'closed_description': {
            'title': 'Склад Яндекс.Go сейчас закрыт :(',
            'message': 'Получить заказ за 15 минут можно с 7:12 до 23:57',
            'close_button': 'Закрыть',
        },
        'dashboard_carousel': {
            'button': {
                'enabled': True,
                'metrica_label': (
                    'SuperApp.Delivery.PultOrder.OrderStatusPreview.DeliverNow'
                ),
                'title': 'Доставить сейчас',
                'subtitle': 'За 15-20 минут',
            },
            'meta': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_number': 1,
                'scenario': 'k2',
            },
            'metrica_label': 'SuperApp.Delivery.PultOrder.OrderStatusPreview',
            'timeline': {
                'horizontal': [
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_accepted',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_accepted'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'in_stock',
                        'image_tag': 'delivery_timeline_delivery_in_stock',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_in_stock'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_delivering',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_delivering'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_finished',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_finished'
                        ),
                        'status': 'pending',
                    },
                ],
            },
        },
    }


@pytest.mark.now('2020-11-24T11:00:00+03:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_on_demand_station_closed(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_order_created.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['ON_DEMAND']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert shipment == {
        'id': REQUEST_ID,
        'title': 'Получите заказ с 12:00',
        'description': 'R&G · №100',
        'multiorder': {
            'postpone_button': {'title': 'Хорошо'},
            'receive_button': {'title': 'Закрыто'},
            'visible': True,
        },
        'checkout': {
            'type': 'lavka',
            'service': 'grocery',
            'relative_path': (
                '/one-click-checkout/?shipmentOrder=100&vendor=beru&token=%s'
                % REQUEST_ID
            ),
        },
        'icon': {'image_tag': 'delivery_market_icon_for_delivery_state'},
        'closed': False,
        'service': 'lavka',
        'closed_description': {
            'title': 'Склад Яндекс.Go сейчас закрыт :(',
            'message': 'Получить заказ за 15 минут можно с 12:00 до 23:59',
            'close_button': 'Закрыть',
        },
        'dashboard_carousel': {
            'button': {
                'enabled': False,
                'metrica_label': (
                    'SuperApp.Delivery.PultOrder.OrderStatusPreview.DeliverNow'
                ),
                'title': 'Станция временно закрыта',
            },
            'meta': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_number': 1,
                'scenario': 'k2',
            },
            'metrica_label': 'SuperApp.Delivery.PultOrder.OrderStatusPreview',
            'timeline': {
                'horizontal': [
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_accepted',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_accepted'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'in_stock',
                        'image_tag': 'delivery_timeline_delivery_in_stock',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_in_stock'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_delivering',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_delivering'
                        ),
                        'status': 'pending',
                    },
                    {
                        'id': 'accepted',
                        'image_tag': 'delivery_timeline_delivery_finished',
                        'image_tag_dark': (
                            'delivery_timeline_delivery_finished'
                        ),
                        'status': 'pending',
                    },
                ],
            },
        },
    }


@pytest.mark.now('2020-11-24T11:00:00+03:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'fetch_shipment',
    [fetch_shipment_shipment_list, fetch_shipment_deliveries],
)
async def test_shipment_terminated(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        fetch_shipment,
):
    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'shipment_ordered.json'
    mock_logistic_platform.file_name = 'shipment.json'
    mock_logistic_platform.request_tags = ['ON_DEMAND']

    shipment = await fetch_shipment(taxi_cargo_c2c, default_pa_headers)
    assert not shipment
