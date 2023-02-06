import pytest

from . import rest_menu_storage
from . import util


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_rest_menu_storage(
        taxi_eats_restaurant_menu, eats_rest_menu_storage, mockserver,
):
    """
    Проверяем отдачу меню из сервиса
    eats_rest_menu_storage
    """

    slug = 'test_slug'
    delivery_time = '2021-01-01T10:00:00+00:00'

    eats_rest_menu_storage.add_category(
        category=rest_menu_storage.Category(
            legacy_id=42, name='Моя категория', available=True,
        ),
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

    @eats_rest_menu_storage.request_assertion
    def _erms_req(request):
        assert request.json['place_id'] == '1'
        assert request.json['shipping_types'] == ['delivery']
        assert request.json['delivery_time'] == delivery_time

    core_dyn_category = util.build_category(
        category_id=None, name='Популярное', items=[util.build_item(10)],
    )

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def core_menu(_):
        return {
            'payload': {
                'categories': [
                    core_dyn_category,
                    util.build_category(
                        category_id=8,
                        name='Этой категории не будет в ответе',
                        items=[
                            util.build_item(
                                12, name='Этого айтема не будет в ответе',
                            ),
                        ],
                    ),
                ],
            },
        }

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params={
            'latitude': '1.000000',
            'longitude': '2.000000',
            'deliveryTime': delivery_time,
            'shippingType': 'delivery',
        },
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert eats_rest_menu_storage.times_called_menu_handler == 1
    assert core_menu.times_called == 1
    assert response.status_code == 200

    categories = response.json()['payload']['categories']

    expected_categories = [
        core_dyn_category,
        util.build_category(
            category_id=42,
            name='Моя категория',
            available=True,
            items=[
                util.build_item(
                    142,
                    public_id='id_1',
                    name='Мой айтем',
                    description='Какое-то описание',
                    price=142,
                    available=True,
                    shipping_type='all',
                    measure={'value': '200', 'measure_unit': 'g'},
                    weight='200 г',
                    picture={
                        'ratio': 1.0,
                        'scale': 'aspect_fit',
                        'uri': 'my_url',
                    },
                    categories_ids=[{'id': 'id_1', 'legacy_id': 42}],
                    options_groups=[
                        {
                            'id': 242,
                            'minSelected': 1,
                            'maxSelected': 10,
                            'name': 'Моя группа опций',
                            'required': False,
                            'options': [
                                {
                                    'id': 342,
                                    'multiplier': 5,
                                    'name': 'Моя опция',
                                    'price': 342,
                                    'decimalPrice': '342',
                                },
                            ],
                        },
                    ],
                ),
                util.build_item(
                    2,
                    public_id='id_1',
                    shipping_type='all',
                    name='Еще айтем',
                    price=2,
                    available=False,
                    categories_ids=[{'id': 'id_1', 'legacy_id': 42}],
                ),
            ],
        ),
    ]

    assert categories == expected_categories


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.config(
    EDA_CORE_NUTRIENTS_SETTINGS={
        'enabled': True,
        'enabled_calories': True,
        'not_duplicate': True,
        'template': (
            'На 100 граммов: '
            'К&thinsp;{calories}, Б&thinsp;{proteins}, '
            'Ж&thinsp;{fats}, У&thinsp;{carbohydrates}'
        ),
    },
)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_rest_menu_storage_nutrients(
        taxi_eats_restaurant_menu, eats_rest_menu_storage, mockserver,
):
    slug = 'test_slug'
    delivery_time = '2021-01-01T10:00:00+00:00'

    eats_rest_menu_storage.add_category(
        category=rest_menu_storage.Category(
            legacy_id=42, name='Моя категория', available=True,
        ),
        items=[
            rest_menu_storage.Item(
                legacy_id=142,
                name='Мой айтем',
                description='Какое-то описание',
                price='142',
                available=True,
                weight_value='100',
                weight_unit='g',
                pictures=[rest_menu_storage.Picture(url='my_url', ratio=1.0)],
                nutrients=rest_menu_storage.ItemNutrients(
                    calories='324', proteins='0', fats='0', carbohydrates='80',
                ),
            ),
        ],
    )

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def core_menu(_):
        return {'payload': {'categories': []}}

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params={
            'latitude': '1.000000',
            'longitude': '2.000000',
            'deliveryTime': delivery_time,
            'shippingType': 'delivery',
        },
        headers={'X-Eats-User': 'user_id=21'},
    )

    item = response.json()['payload']['categories'][0]['items'][0]
    expected_nutrients = {
        'calories': {'unit': 'ккал', 'value': '324'},
        'carbohydrates': {'unit': 'г', 'value': '80'},
        'fats': {'unit': 'г', 'value': '0'},
        'proteins': {'unit': 'г', 'value': '0'},
    }
    expected_description = (
        'Какое-то описание.<br>'
        'На 100 граммов: К&thinsp;324, Б&thinsp;-, Ж&thinsp;-, У&thinsp;80'
    )

    assert core_menu.times_called == 1
    assert item['nutrients'] == expected_nutrients
    assert item['description'] == expected_description


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_rest_menu_storage_error(taxi_eats_restaurant_menu, mockserver):
    """
    Проверяем, что при ошибках rest_menu_storage
    происходит фолбек на кору
    """

    slug = 'test_slug'

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/menu')
    def erms_menu(_):
        return mockserver.make_response(status=500)

    core_response = {
        'payload': {
            'categories': [
                util.build_category(
                    category_id=8,
                    name='Категория',
                    items=[util.build_item(12, name='Айтем')],
                ),
            ],
        },
    }

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def core_menu(_):
        return core_response

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params={'latitude': '1.000000', 'longitude': '2.000000'},
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert erms_menu.times_called == 1
    assert core_menu.times_called == 1
    assert response.status_code == 200

    assert response.json() == core_response


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_rest_menu_storage_choosable(
        taxi_eats_restaurant_menu, eats_rest_menu_storage, mockserver,
):
    """
    Проверяем что не choosable айтем не отображается в выдаче
    """

    slug = 'test_slug'

    eats_rest_menu_storage.add_category(
        category=rest_menu_storage.Category(
            legacy_id=42, name='Моя категория', available=True,
        ),
        items=[
            rest_menu_storage.Item(
                legacy_id=142,
                name='Мой айтем',
                description='Какое-то описание',
                price='142.01',
                available=True,
                choosable=False,
            ),
        ],
    )

    empty_menu = {'payload': {'categories': []}}

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def _core_menu(_):
        return empty_menu

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params={'latitude': '1.000000', 'longitude': '2.000000'},
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert eats_rest_menu_storage.times_called_menu_handler == 1
    assert response.status_code == 200

    assert response.json() == empty_menu


@util.eats_client_menu_use_erms(dry_run=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_rest_menu_storage_compare(
        taxi_eats_restaurant_menu,
        eats_rest_menu_storage,
        mockserver,
        testpoint,
):
    """
    Проверяет что вызывается код сравнения меню
    """

    slug = 'test_slug'

    eats_rest_menu_storage.add_category(
        category=rest_menu_storage.Category(legacy_id=1, name='Бургеры'),
        items=[
            rest_menu_storage.Item(
                legacy_id=10,
                name='Не мой айтем',
                description='Какое-то описание',
                price='10',
            ),
        ],
    )

    core_category = util.build_category(
        category_id=1,
        name='Бургеры',
        items=[
            util.build_item(
                10,
                name='Мой айтем',
                description='Какое-то описание',
                price=10,
                available=True,
                shipping_type='all',
            ),
        ],
    )

    core_menu = {'payload': {'categories': [core_category]}}

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def _core_menu_handler(_):
        return core_menu

    @testpoint('compare-field-called')
    def compare_field_called(arg):
        assert arg == 'name'

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params={'latitude': '1.000000', 'longitude': '2.000000'},
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert eats_rest_menu_storage.times_called_menu_handler == 1
    assert response.status_code == 200
    assert compare_field_called.times_called == 1

    assert response.json() == core_menu


@util.eats_client_menu_use_erms(enabled=True)
@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.translations(
    **{
        'eats-restaurant-menu': {
            'category_schedule.monday': {'ru': 'Пн'},
            'category_schedule.from_until': {'ru': 'с %(from)s до %(to)s'},
            'category_schedule.days_intervals': {
                'ru': '%(days)s %(intervals)s',
            },
        },
    },
)
async def test_rest_menu_storage_category_schedule(
        taxi_eats_restaurant_menu, eats_rest_menu_storage, mockserver,
):
    """
    Проверяет формирование строки с расписание категории
    """

    slug = 'test_slug'

    eats_rest_menu_storage.add_category(
        category=rest_menu_storage.Category(
            id='id_2',
            legacy_id=2,
            name='Категория с расписанием',
            available=False,
            schedule=[{'day': 1, 'from': 8 * 60, 'to': 20 * 60}],  # 8h  # 20h
            sort=1000,
        ),
        items=[
            rest_menu_storage.Item(
                id='id_2',
                legacy_id=2,
                name='Другой айтем',
                price='2',
                available=False,
            ),
        ],
    )

    @mockserver.json_handler(f'/eats-core-menu/api/v2/menu/retrieve/{slug}')
    def _core_menu_handler(_):
        return {'payload': {'categories': []}}

    response = await taxi_eats_restaurant_menu.get(
        f'/api/v2/menu/retrieve/{slug}',
        params={'latitude': '1.000000', 'longitude': '2.000000'},
        headers={'X-Eats-User': 'user_id=21'},
    )

    assert eats_rest_menu_storage.times_called_menu_handler == 1
    assert response.status_code == 200

    schedule = response.json()['payload']['categories'][0]['schedule']
    assert schedule == 'Пн с 08:00 до 20:00'
