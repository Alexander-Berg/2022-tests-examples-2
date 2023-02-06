async def test_proxies_grocery_api_service_info(
        taxi_grocery_market_gw, mockserver,
):
    """ Проксирует ответ от grocery-api:/service-info """

    # Где-то в Москве
    lat = 55.70
    lon = 37.50

    position = {'location': [lon, lat], 'uri': 'some-uri'}
    offer_id = 'offer-id'
    payment_method = {'type': 'card', 'id': 'card-xxx'}
    delivery_cost = 150
    depot_id = '12345'

    json_to_proxy = {
        'service_metadata': {
            'delivery_type': 'pedestrian',
            'legal_entities': [
                {'description': 'Описание', 'type': 'service_partner'},
            ],
            'links': [
                {
                    'type': 'help_page',
                    'href': 'http://taxi.yandex.ru/webview/help/ru_RU',
                },
            ],
            'service_name': 'Яндекс.Лавка',
            'status': 'open',
            'switch_time': '2021-10-12T17:01:00+00:00',
            'traits': [
                {'type': 'eta', 'value': '3-7 мин.'},
                {'type': 'address', 'value': 'depot address'},
            ],
        },
        'pricing_conditions': {
            'service_fee_template': f'{delivery_cost} $SIGN$$CURRENCY$',
            'minimal_cart_price_template': '0 $SIGN$$CURRENCY$',
            'minimal_cart_price_value': '0',
        },
        'depot_id': depot_id,
        'is_surge': True,
        'currency': 'RUB',
        'currency_sign': '₽',
        'l10n': {
            'delivery_min_cart_subtitle': (
                'Поэтому можно сделать заказ только '
                'от 1500 $SIGN$$CURRENCY$'
            ),
            'delivery_min_cart_title': 'Сейчас слишком много заказов',
            'delivery_min_order': 'Заказ от 1500 $SIGN$$CURRENCY$',
            'delivery_min_cart_button_text': 'Понятно!',
            'delivery_conditions': [
                {
                    'delivery_cost_template': 'Delivery: $SIGN$10$CURRENCY$',
                    'order_cost_template': (
                        'For orders under $SIGN$25$CURRENCY$'
                    ),
                },
                {
                    'delivery_cost_template': 'Delivery: $SIGN$5$CURRENCY$',
                    'order_cost_template': (
                        'For orders from $SIGN$25$CURRENCY$'
                        ' to $SIGN$50$CURRENCY$'
                    ),
                },
                {
                    'delivery_cost_template': 'Free delivery',
                    'order_cost_template': (
                        'For orders over $SIGN$50$CURRENCY$'
                    ),
                },
            ],
        },
        'cashback': {
            'balance': '100',
            'payment_available': True,
            'annihilation_info': {
                'annihilation_date': '2021-10-12T17:01:00+00:00',
                'balance_to_annihilate': '50',
            },
        },
        'offer_id': offer_id,
        'informers': [
            {
                'name': 'test_informer',
                'picture': 'some_url',
                'text': 'hello',
                'show_in_root': True,
                'text_color': 'blue',
                'background_color': 'blue',
                'category_ids': ['category-1', 'category-2'],
                'category_group_ids': ['some_category_group'],
                'product_ids': ['product-1', 'product-2'],
                'modal': {
                    'text': 'hello',
                    'text_color': 'blue',
                    'background_color': 'blue',
                    'picture': 'some_picture',
                    'title': 'some_title',
                    'buttons': [
                        {
                            'variant': 'default',
                            'text': 'button',
                            'text_color': 'blue',
                            'background_color': 'blue',
                            'link': 'some_link',
                        },
                        {'variant': 'default', 'text': 'button too'},
                    ],
                },
            },
        ],
        'reward_block': [
            {
                'type': 'min_cart',
                'cart_cost_threshold': '50 $SIGN$$CURRENCY$',
                'reward_value': 'Минимальная корзина',
            },
            {
                'type': 'delivery',
                'cart_cost_threshold': 'От 50 $SIGN$$CURRENCY$',
                'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
            },
        ],
    }

    @mockserver.json_handler('/grocery-api/lavka/v1/api/v1/service-info')
    def _mock_grocery_api_service_info(request):
        assert request.json['position'] == position
        assert request.json['offer_id'] == offer_id
        assert request.json['current_payment_method'] == payment_method

        return mockserver.make_response(
            json=json_to_proxy,
            headers={},
            content_type='application/json',
            status=200,
        )

    response = await taxi_grocery_market_gw.post(
        '/lavka/v1/market-gw/v1/service-info',
        json={
            'position': position,
            'offer_id': offer_id,
            'current_payment_method': payment_method,
        },
        headers={},
    )

    assert _mock_grocery_api_service_info.times_called == 1

    del json_to_proxy['service_metadata']['delivery_type']
    del json_to_proxy['informers'][0]['modal']['buttons'][0]['variant']
    del json_to_proxy['informers'][0]['modal']['buttons'][1]['variant']
    assert response.json() == json_to_proxy
