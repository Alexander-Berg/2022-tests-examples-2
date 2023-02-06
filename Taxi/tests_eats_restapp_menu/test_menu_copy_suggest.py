PARTNER_ID = '777'
TARGET_PLACE_ID = '109151'
NOT_FOUND_PLACE_ID = '888888'
CORE_PLACES_INFO = [
    {
        'id': 1,
        'name': 'name1',
        'available': True,
        'currency': {'code': 'code1', 'sign': 'sign1', 'decimal_places': 1},
        'country_code': 'country_code1',
        'address': {
            'country': 'country1',
            'city': 'city1',
            'street': 'street1',
            'building': 'building1',
            'full': 'country1 city1 street1 building1',
        },
        'region': {'id': 58, 'slug': 'PENZA'},
        'show_shipping_time': True,
        'integration_type': 'native',
        'type': 'marketplace',
        'slug': 'slug1',
        'brand': {'slug': 'brand1', 'business_type': 'some_type'},
    },
    {
        'id': 2,
        'name': 'name2',
        'available': True,
        'currency': {'code': 'code2', 'sign': 'sign2', 'decimal_places': 2},
        'country_code': 'country_code2',
        'address': {
            'country': 'country2',
            'city': 'city2',
            'street': 'street2',
            'building': 'building2',
            'full': 'country2 city2 street2 building2',
        },
        'show_shipping_time': True,
        'integration_type': 'custom',
        'type': 'marketplace',
        'slug': 'slug2',
        'brand': {'slug': 'brand1', 'business_type': 'some_type'},
    },
    {
        'id': 3,
        'name': 'name3',
        'available': False,
        'currency': {'code': 'code3', 'sign': 'sign3', 'decimal_places': 3},
        'country_code': 'country_code3',
        'address': {
            'country': 'country3',
            'city': 'city3',
            'street': 'street3',
            'building': 'building3',
            'full': 'country3 city3 street3 building3',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'type': 'native',
        'slug': 'slug3',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'brand2', 'business_type': 'some_type'},
    },
    {
        'id': 4,
        'name': 'name4',
        'available': False,
        'currency': {'code': 'code4', 'sign': 'sign4', 'decimal_places': 3},
        'country_code': 'country_code4',
        'address': {
            'country': 'country4',
            'city': 'city4',
            'street': 'street4',
            'building': 'building4',
            'full': 'country4 city4 street4 building4',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'type': 'marketplace',
        'slug': 'slug4',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
    },
    {
        'id': int(TARGET_PLACE_ID),
        'name': 'name5',
        'available': False,
        'currency': {'code': 'code5', 'sign': 'sign5', 'decimal_places': 3},
        'country_code': 'country_code5',
        'address': {
            'country': 'country5',
            'city': 'city5',
            'street': 'street5',
            'building': 'building5',
            'full': 'country5 city5 street5 building5',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'type': 'marketplace',
        'slug': 'slug5',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'brand1', 'business_type': 'some_type'},
    },
]


async def test_menu_copy_suggest_post_no_access(taxi_eats_restapp_menu):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy/suggest',
        params={'target_place_id': TARGET_PLACE_ID},
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': '1,2,3',
        },
        json={},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }


async def test_menu_copy_suggest_post_no_target(
        taxi_eats_restapp_menu, mockserver,
):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def mock_places_info(request):
        return {'payload': CORE_PLACES_INFO}

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy/suggest',
        params={'target_place_id': NOT_FOUND_PLACE_ID},
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': '1,2,3,888888',
        },
        json={},
    )

    assert mock_places_info.times_called == 1
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'No target brand'}


async def test_menu_copy_suggest_post_basic(
        taxi_eats_restapp_menu, mockserver,
):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def mock_places_info(request):
        return {'payload': CORE_PLACES_INFO}

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy/suggest',
        params={'target_place_id': TARGET_PLACE_ID},
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': '1,2,3,4,5,109151',
        },
        json={},
    )

    assert mock_places_info.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'payload': [
            {
                'target_place_id': 109151,
                'id': 1,
                'name': 'name1',
                'address': 'country1 city1 street1 building1',
                'type': 'marketplace',
                'can_copy': True,
                'reason': '',
            },
            {
                'target_place_id': 109151,
                'id': 2,
                'name': 'name2',
                'address': 'country2 city2 street2 building2',
                'type': 'marketplace',
                'can_copy': False,
                'reason': 'Заведение на интеграции',
            },
            {
                'target_place_id': 109151,
                'id': 3,
                'name': 'name3',
                'address': 'country3 city3 street3 building3',
                'type': 'native',
                'can_copy': False,
                'reason': 'Разные бренды у заведений',
            },
            {
                'target_place_id': 109151,
                'id': 4,
                'name': 'name4',
                'address': 'country4 city4 street4 building4',
                'type': 'marketplace',
                'can_copy': False,
                'reason': 'Разные бренды у заведений',
            },
        ],
    }
