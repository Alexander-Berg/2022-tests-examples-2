def build_place(revision: int, brand: dict) -> dict:
    return {
        'revision': revision,
        'slug': 'Holly-Food-by-Bryan',
        'type': 'native',
        'business': 'restaurant',
        'enabled': True,
        'name': 'Holly Food by Bryan',
        'brand': brand,
        'address': {'city': 'Москва', 'short': 'Красная площадь'},
        'address_comment': 'test_comment',
        'allowed_couriers_types': ['yandex_rover'],
        'assembly_cost': 100,
        'categories': [{'id': 9, 'name': 'пицца'}],
        'contacts': [
            {
                'extension': '123',
                'personal_phone_id': '123',
                'type': 'official',
            },
        ],
        'country': {
            'code': 'RU',
            'currency': {'code': 'RUB', 'sign': '₽'},
            'id': 35,
            'name': 'Россия',
        },
        'extra_info': {
            'footer_description': '123',
            'legal_info_description': '321',
        },
        'features': {
            'availability_strategy': 'burger_king',
            'brand_ui_backgrounds': [
                {'color': '#1f1f1F', 'theme': 'light'},
                {'color': '#1f1f1F', 'theme': 'dark'},
            ],
            'brand_ui_logos': [
                {'size': 'small', 'theme': 'light', 'url': 'testsuite'},
                {'size': 'medium', 'theme': 'light', 'url': 'testsuite'},
            ],
            'constraints': [
                {'code': 'max_order_cost', 'value': 10000},
                {'code': 'max_order_weight', 'value': 15},
            ],
            'eco_package': True,
            'editorial_description': 'Безумный фалафель',
            'editorial_verdict': 'Рекомендую',
            'fast_food': True,
            'ignore_surge': False,
            'shop_picking_type': 'our_picking',
            'supports_preordering': False,
            'visibility_mode': 'on',
        },
        'gallery': [
            {
                'template': 'testsuite',
                'type': 'picture',
                'url': 'testsuite',
                'weight': 0,
            },
            {'type': 'video', 'url': 'https://video.url', 'weight': 1},
        ],
        'launched_at': '2015-12-14T00:00:00+03:00',
        'location': {'geo_point': [55.741, 37.627]},
        'payment_methods': ['cash', 'taxi', 'cardPostPayment'],
        'price_category': {'id': 2, 'name': '₽', 'value': 0.5},
        'quick_filters': {
            'general': [{'id': 22, 'slug': 'slug22'}],
            'wizard': [{'id': 23, 'slug': 'slug23'}],
        },
        'rating': {'admin': 1, 'count': 1, 'shown': 0, 'users': 0},
        'region': {
            'geobase_ids': [213, 216],
            'id': 1,
            'name': 'region_name',
            'time_zone': 'Europe/Moscow',
        },
        'sorting': {'popular': 10, 'weight': 100, 'wizard': 1},
        'timing': {
            'average_preparation': 450,
            'extra_preparation': 600,
            'preparation': 3600,
        },
        'working_intervals': [
            {
                'from': '2020-01-01T10:00:00+03:00',
                'to': '2120-01-01T18:00:00+03:00',
            },
        ],
        'origin_id': 'id-1',
    }


async def search_places_by_ids(
        taxi_eats_catalog_storage, place_id: int,
) -> list:
    response = await taxi_eats_catalog_storage.post(
        '/internal/eats-catalog-storage/v1/search/places/list',
        json={'place_ids': [place_id]},
    )
    assert response.status_code == 200
    return response.json()['places']


async def test_update_place_brand_picture_scale_type(
        taxi_eats_catalog_storage,
):
    """
    EDACAT-1848: check that place updates changes brand picture scale type.
    """

    brand: dict = {
        'id': 1,
        'name': 'Testsuite',
        'slug': 'testsuite',
        'picture_scale_type': 'aspect_fit',
    }

    place_id: int = 1
    revision: int = 0
    response = await taxi_eats_catalog_storage.put(
        f'/internal/eats-catalog-storage/v1/place/{place_id}',
        json=build_place(revision, brand),
    )
    assert response.status_code == 200
    revision = response.json()['revision']

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)

    places = await search_places_by_ids(taxi_eats_catalog_storage, place_id)
    assert places

    place = places.pop(0)
    assert place['place']['brand']['picture_scale_type'] == 'aspect_fit'

    brand['picture_scale_type'] = 'aspect_fill'
    response = await taxi_eats_catalog_storage.put(
        f'/internal/eats-catalog-storage/v1/place/{place_id}',
        json=build_place(revision, brand),
    )
    assert response.status_code == 200
    revision = response.json()['revision']

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)

    places = await search_places_by_ids(taxi_eats_catalog_storage, place_id)
    assert places

    place = places.pop(0)
    assert place['place']['brand']['picture_scale_type'] == 'aspect_fill'

    brand['picture_scale_type'] = 'unknown'

    response = await taxi_eats_catalog_storage.put(
        f'/internal/eats-catalog-storage/v1/place/{place_id}',
        json=build_place(revision, brand),
    )
    assert response.status_code == 200

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)

    places = await search_places_by_ids(taxi_eats_catalog_storage, place_id)
    assert places

    place = places.pop(0)
    assert place['place']['brand']['picture_scale_type'] == 'aspect_fit'
