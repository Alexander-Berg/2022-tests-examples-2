import pytest

from . import rest_menu_storage
from . import util


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@util.discounts_applicator_menu()
@util.dynamic_prices(100)
@pytest.mark.smart_prices_cache({'1': 10})
async def test_get_items_from_erms(
        taxi_eats_restaurant_menu,
        eats_rest_menu_storage,
        eats_discounts_applicator,
        load_json,
):
    """
    Проверяем отдачу айтемов из сервиса eats_rest_menu_storage
    с применением скидок и умной цены
    """

    slug = 'test_slug'
    place_id = 1
    delivery_time = '2021-01-01T10:00:00+00:00'
    eats_rest_menu_storage.place_id = str(place_id)
    eats_rest_menu_storage.place_slug = slug

    request = {
        'shipping_types': ['delivery'],
        'legacy_ids': [142, 2],
        'delivery_time': delivery_time,
    }
    eats_rest_menu_storage.add_items(
        category_id='Моя категория',
        category_legacy_id=1,
        items=[
            rest_menu_storage.Item(
                legacy_id=142,
                name='Мой айтем',
                description='Какое-то описание',
                price='142',
                available=True,
                weight_value='200',
                weight_unit='g',
                pictures=[rest_menu_storage.Picture(url='my_url', ratio=1.0)],
                options_groups=[
                    rest_menu_storage.OptionGroup(
                        legacy_id=242,
                        name='Моя группа опций',
                        min_selected_options=1,
                        max_selected_options=10,
                        options=[
                            rest_menu_storage.Option(
                                legacy_id=342,
                                name='Моя опция',
                                price='342',
                                multiplier=5,
                            ),
                        ],
                    ),
                ],
            ),
            rest_menu_storage.Item(
                legacy_id=2, name='Еще айтем', price='2', available=False,
            ),
        ],
    )

    eats_discounts_applicator.add_menu_discount(
        item_id='2',
        discount_id='1',
        value_type='fraction',
        value='10',
        name='Скидка деньгами',
        description='item discount',
        picture_uri='some_uri',
    )

    response = await taxi_eats_restaurant_menu.post(
        '/internal/v1/menu/get-items',
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert response.status_code == 200
    assert eats_rest_menu_storage.times_called_get_items_handler == 1

    data = response.json()
    expected_response = load_json('get_items_response.json')
    for elem in data['place_menu_items']:
        del elem['in_stock']
    del data['place_menu_items'][0]['weight']
    assert data == expected_response


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_get_items_from_erms_error(
        taxi_eats_restaurant_menu, eats_rest_menu_storage, mockserver,
):
    """
    Ошибка при отдаче айтемов из сервиса eats_rest_menu_storage,
    нет такого плейса
    """

    slug = 'test_slug'
    delivery_time = '2021-01-01T10:00:00+00:00'
    eats_rest_menu_storage.place_slug = slug

    request = {
        'shipping_types': ['delivery'],
        'legacy_ids': [142, 2],
        'delivery_time': delivery_time,
    }

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/get-items')
    def erms_get_items(_):
        return mockserver.make_response('place not found', status=404)

    response = await taxi_eats_restaurant_menu.post(
        '/internal/v1/menu/get-items',
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert erms_get_items.times_called == 1
    assert response.status_code == 400
    assert response.json() == {
        'error': 'not_found_place',
        'message': 'Place not found for requsted items',
    }
