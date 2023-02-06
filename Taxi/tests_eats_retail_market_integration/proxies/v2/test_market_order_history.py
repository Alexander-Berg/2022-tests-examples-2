import pytest


HANDLER = '/v2/market/order/history'
ORDER_HISTORY_HANDLER = '/eats/v1/retail-order-history/customer/order/history'
EATER_ID = '1'


@pytest.mark.parametrize(
    'eats_retail_order_history_status', [200, 400, 401, 404, 500],
)
@pytest.mark.parametrize('config_enable', [True, False])
async def test_response(
        taxi_eats_retail_market_integration,
        mockserver,
        pgsql,
        taxi_config,
        load_json,
        eats_retail_order_history_status,
        config_enable,
):
    set_config(taxi_config, config_enable)
    sql_insert_market_brand_places(pgsql)

    eater_orders = [
        ('order_1', EATER_ID),
        ('order_2', EATER_ID),
        ('order_4', EATER_ID),
        ('order_w_unknown_status', EATER_ID),
        ('order_3', '2'),
        ('order_wo_product_mapping', EATER_ID),
    ]
    sql_insert_orders(eater_orders, pgsql)

    @mockserver.json_handler(
        '/eats-products/internal/v2/products/public_id_by_origin_id',
    )
    def _mock_eats_products(request):
        products_mapping = load_json('products_mapping.json')
        place_id = str(request.json['place_id'])
        if place_id not in products_mapping:
            return mockserver.make_response(status=404)
        return {'products_ids': products_mapping[place_id]}

    @mockserver.json_handler(
        '/eats-retail-order-history' + ORDER_HISTORY_HANDLER,
    )
    def _mock_eats_retail_orders_history(request):
        if eats_retail_order_history_status != 200:
            return mockserver.make_response(
                status=eats_retail_order_history_status,
            )
        items = load_json('orders_history_items.json')
        orders = load_json('orders_history_orders.json')
        order_nr = request.query['order_nr']
        return build_orders_history_response(orders[order_nr], items)

    response = await taxi_eats_retail_market_integration.post(
        HANDLER, headers={'X-Eats-User': f'user_id={EATER_ID}'}, json={},
    )

    assert response.status_code == 200
    assert get_sorted_response(response.json()) == get_expected_response(
        eats_retail_order_history_status, config_enable, load_json,
    )


async def test_unauthorized(taxi_eats_retail_market_integration):
    response = await taxi_eats_retail_market_integration.post(HANDLER, json={})
    assert response.status_code == 401


@pytest.mark.parametrize('page_size', [1, 3, 5])
async def test_pagination(
        taxi_eats_retail_market_integration,
        mockserver,
        pgsql,
        taxi_config,
        load_json,
        page_size,
):
    set_config(taxi_config, True)
    sql_insert_market_brand_places(pgsql)

    eater_orders = [
        ('order_1', EATER_ID),
        ('order_2', EATER_ID),
        ('order_4', EATER_ID),
        ('order_w_unknown_status', EATER_ID),
        ('order_3', '2'),
        ('order_wo_product_mapping', EATER_ID),
    ]
    sql_insert_orders(eater_orders, pgsql)

    @mockserver.json_handler(
        '/eats-products/internal/v2/products/public_id_by_origin_id',
    )
    def _mock_eats_products(request):
        products_mapping = load_json('products_mapping.json')
        place_id = str(request.json['place_id'])
        if place_id not in products_mapping:
            return mockserver.make_response(status=404)
        return {'products_ids': products_mapping[place_id]}

    @mockserver.json_handler(
        '/eats-retail-order-history' + ORDER_HISTORY_HANDLER,
    )
    def _mock_eats_retail_orders_history(request):
        items = load_json('orders_history_items.json')
        orders = load_json('orders_history_orders.json')
        order_nr = request.query['order_nr']
        return build_orders_history_response(orders[order_nr], items)

    full_expected_response_orders = get_sorted_response(
        load_json('expected_response.json'),
    )['orders']
    current_page = 1
    pages = []
    expected_pages = []
    while (current_page - 1) * page_size < len(full_expected_response_orders):
        response = await taxi_eats_retail_market_integration.post(
            HANDLER,
            headers={'X-Eats-User': f'user_id={EATER_ID}'},
            json={'cursor': {'page': current_page, 'count': page_size}},
        )

        assert response.status_code == 200
        pages.append(
            [order['order_nr'] for order in response.json()['orders']],
        )
        expected_pages.append(
            [
                order['order_nr']
                for order in full_expected_response_orders[
                    (current_page - 1)
                    * page_size : min(
                        current_page * page_size,
                        len(full_expected_response_orders),
                    )
                ]
            ],
        )
        current_page += 1

    assert pages == expected_pages


async def test_pagination_with_big_page_number(
        taxi_eats_retail_market_integration,
        mockserver,
        pgsql,
        taxi_config,
        load_json,
):
    page_size = 10
    set_config(taxi_config, True)
    sql_insert_market_brand_places(pgsql)

    eater_orders = [
        ('order_1', EATER_ID),
        ('order_2', EATER_ID),
        ('order_4', EATER_ID),
        ('order_w_unknown_status', EATER_ID),
        ('order_3', '2'),
        ('order_wo_product_mapping', EATER_ID),
    ]
    sql_insert_orders(eater_orders, pgsql)

    @mockserver.json_handler(
        '/eats-products/internal/v2/products/public_id_by_origin_id',
    )
    def _mock_eats_products(request):
        products_mapping = load_json('products_mapping.json')
        place_id = str(request.json['place_id'])
        if place_id not in products_mapping:
            return mockserver.make_response(status=404)
        return {'products_ids': products_mapping[place_id]}

    @mockserver.json_handler(
        '/eats-retail-order-history' + ORDER_HISTORY_HANDLER,
    )
    def _mock_eats_retail_orders_history(request):
        items = load_json('orders_history_items.json')
        orders = load_json('orders_history_orders.json')
        order_nr = request.query['order_nr']
        return build_orders_history_response(orders[order_nr], items)

    current_page = 100
    response = await taxi_eats_retail_market_integration.post(
        HANDLER,
        headers={'X-Eats-User': f'user_id={EATER_ID}'},
        json={'cursor': {'page': current_page, 'count': page_size}},
    )
    assert response.status_code == 200
    assert response.json()['orders'] == []


def set_config(taxi_config, config_enable):
    taxi_config.set_values(
        {
            'EATS_RETAIL_MARKET_INTEGRATION_ORDER_HISTORY': {
                'enable': config_enable,
                'display_order_nr_prefix': 'retail-',
                'statuses': {
                    'awaiting_payment': 'Ожидает оплаты',
                    'confirmed': 'Подтвержден',
                    'cooking': 'Собирается',
                    'in_delivery': 'Доставляется',
                    'arrived_to_customer': 'Доставлен',
                    'delivered': 'Доставлен',
                    'cancelled': 'Отменен',
                    'auto_complete': 'Автозаполнение',
                },
            },
        },
    )


def sql_insert_orders(eater_orders, pgsql):
    cursor = pgsql['eats_retail_market_integration'].cursor()
    for order_nr, eater_id in eater_orders:
        cursor.execute(
            f"""
            insert into eats_retail_market_integration.orders
            (order_nr, eater_id)
            values ('{order_nr}', '{eater_id}')
            """,
        )


def build_orders_history_response(order, items):
    order['original_items'] = [
        items[original_item] for original_item in order['original_items']
    ]
    order['diff']['no_changes'] = [
        items[item] for item in order['diff']['no_changes']
    ]
    order['diff']['add'] = [
        items[add_item] for add_item in order['diff']['add']
    ]
    order['diff']['remove'] = [
        items[remove_item] for remove_item in order['diff']['remove']
    ]
    order['diff']['replace'] = [
        {
            'from_item': items[replace_item['from_item']],
            'to_item': items[replace_item['to_item']],
        }
        for replace_item in order['diff']['replace']
    ]
    order['diff']['update'] = [
        {
            'from_item': items[update_item['from_item']],
            'to_item': items[update_item['to_item']],
        }
        for update_item in order['diff']['update']
    ]
    return order


def get_sorted_response(response):
    for order in response['orders']:
        order['items'].sort(key=lambda item: item['name'])
    return response


def get_expected_response(
        eats_retail_order_history_status, config_enable, load_json,
):
    if eats_retail_order_history_status != 200 or not config_enable:
        return {'orders': [], 'total_orders_count': 0}
    expected_response = load_json('expected_response.json')
    return get_sorted_response(expected_response)


def sql_insert_market_brand_places(pgsql):
    cursor = pgsql['eats_retail_market_integration'].cursor()
    cursor.execute(
        """
        insert into eats_retail_market_integration.brands (
            id, slug
        ) values (111, 'brand_slug_111')
        """,
    )

    cursor.execute(
        """
        insert into eats_retail_market_integration.places (
            id, slug, brand_id
        ) values (1, 'place_slug_1', 111),
                 (2, 'place_slug_2', 111),
                 (3, 'place_slug_3', 111)
        """,
    )

    cursor.execute(
        """
        insert into eats_retail_market_integration.market_brand_places (
            brand_id, place_id, business_id, partner_id, feed_id
        ) values (111, 1, 123, 100, 10), (111, 2, 123, 200, 20)
        """,
    )
