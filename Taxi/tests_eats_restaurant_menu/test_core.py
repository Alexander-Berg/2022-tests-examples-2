from . import util


async def test_menu_from_core(taxi_eats_restaurant_menu, mockserver):
    slug = 'test_slug'

    request_params = {
        'latitude': '1.000000',
        'longitude': '2.000000',
        'deliveryTime': '2021-01-01T10:00:00+00:00',
        'shippingType': 'delivery',
    }

    optionsgroups = [
        {
            'id': 10372250,
            'maxSelected': 2,
            'minSelected': 1,
            'name': 'Соус на выбор',
            'options': [
                {
                    'decimalPrice': '15.98',
                    'id': 1679268432,
                    'multiplier': 2,
                    'name': 'Сметана - 30 гр',
                    'price': 4,
                    'promoPrice': 3,
                    'decimalPromoPrice': '3',
                },
                {
                    'decimalPrice': '10',
                    'id': 1679268437,
                    'multiplier': 2,
                    'name': 'Наршараб - 30 гр',
                    'price': 40,
                },
            ],
            'required': True,
        },
    ]

    menu = {
        'payload': {
            'categories': [
                util.build_category(
                    category_id=5,
                    available=True,
                    items=[util.build_item(2, options_groups=optionsgroups)],
                ),
                util.build_category(
                    category_id=4, available=False, items=[util.build_item(1)],
                ),
                util.build_category(
                    category_id=7, available=False, items=[util.build_item(3)],
                ),
            ],
        },
    }

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def core_menu(request):
        assert dict(request.query) == request_params
        return menu

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params=request_params,
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert core_menu.times_called == 1
    assert response.status_code == 200
    assert response.json() == menu

    headers = response.headers
    assert headers['Cache-Control'] == 'private, max-age=0, no-cache, no-store'
    assert headers['Pragma'] == 'no-cache'


async def test_menu_from_core_error(taxi_eats_restaurant_menu, mockserver):
    slug = 'test_slug'

    request_params = {
        'latitude': '1.000000',
        'longitude': '2.000000',
        'deliveryTime': '2021-01-01T10:00:00+00:00',
        'shippingType': 'delivery',
    }

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def core_menu(_):
        return mockserver.make_response(status=500)

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params=request_params,
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert core_menu.times_called == 1
    assert response.status_code == 500


async def test_menu_from_core_404(taxi_eats_restaurant_menu, mockserver):
    slug = 'test_slug'

    request_params = {'latitude': '1.000000', 'longitude': '2.000000'}
    not_found_response = [
        {
            'code': 'err',
            'title': 'err title',
            'source': {'pointer': 'ptr', 'parameter': 'peram'},
            'meta': {'context': {'key': 'value'}},
        },
    ]

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def core_menu(_):
        return mockserver.make_response(status=404, json=not_found_response)

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params=request_params,
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert response.status_code == 404
    assert core_menu.times_called == 1
    assert response.json() == not_found_response
