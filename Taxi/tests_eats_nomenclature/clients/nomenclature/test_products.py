import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils


EMPTY_REQUEST_WITH_CATEGORIES: dict = {'products': [], 'withCategories': True}
EMPTY_REQUEST_WITHOUT_CATEGORIES: dict = {
    'products': [],
    'withCategories': False,
}
EMPTY_REQUEST: dict = {'products': [], 'withCategories': True}
EMPTY_RESPONSE: dict = {'categories': []}
HANDLER = '/v1/products'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_unknown_slug(taxi_eats_nomenclature, load_json):
    # Тест проверяет, что если на вход передать неизвестный slug,
    # то ручка вернет 404.
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=unknown_slug', json=EMPTY_REQUEST,
    )

    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_empty_request(taxi_eats_nomenclature, load_json):
    # Тест проверяет, что если на вход передать
    # пустой набор id товаров, то ответ будет пустым с кодом 200
    # (вне зависимости от параметра withCategories).
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=EMPTY_REQUEST_WITH_CATEGORIES,
    )
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE

    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=EMPTY_REQUEST_WITHOUT_CATEGORIES,
    )
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE

    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=EMPTY_REQUEST,
    )
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'products_additional_data.sql',
    ],
)
async def test_unknown_products(taxi_eats_nomenclature, load_json):
    # Тест проверяет, что ручка не возвращает никакие данные
    # по товарам, которых нет в текущем ассортименте магазина
    # или нет вообще в магазине (вне зависимости от параметра
    # withCategories).
    request = {
        'products': [
            'item_origin_10',
            'item_origin_unknown_1',
            'item_origin_unknown_2',
        ],
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE

    request['withCategories'] = False
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE

    request['withCategories'] = True
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_products_and_categories(taxi_eats_nomenclature):
    # Тест проверяет, что ручка возвращает данные по запрошенным товарам,
    # включая категории, в которых эти товары находятся,
    # если параметр withCategories = true.
    request = {
        'products': [
            'item_origin_1_avail_null',
            'item_origin_2_avail_now',
            'item_origin_3_avail_past',
        ],
        'withCategories': True,
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )

    assert response.status == 200

    assert 'categories' in response.json()
    categories = response.json()['categories']
    assert len(response.json()['categories']) == 3
    categories = dict()
    for category in response.json()['categories']:
        categories[category['id']] = []
        for item in category['items']:
            categories[category['id']].append(item['id'])
    assert 'category_1_origin' in categories
    assert 'item_origin_1_avail_null' in categories['category_1_origin']
    assert 'item_origin_2_avail_now' in categories['category_1_origin']

    assert 'category_2_origin' in categories
    assert 'item_origin_3_avail_past' in categories['category_2_origin']

    assert 'category_4_origin' in categories
    assert categories['category_4_origin'] == []


@pytest.mark.parametrize(
    'get_default_assortment_from, trait_id, assortment_id',
    [
        ('place_default_assortments', 1, 1),
        ('brand_default_assortments', 2, 3),
        (None, None, 4),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_default_assortment(
        taxi_eats_nomenclature,
        testpoint,
        sql_del_default_assortments,
        sql_set_place_default_assortment,
        sql_set_brand_default_assortment,
        get_default_assortment_from,
        trait_id,
        assortment_id,
):
    sql_del_default_assortments()
    if get_default_assortment_from == 'place_default_assortments':
        sql_set_place_default_assortment(trait_id=trait_id)
    elif get_default_assortment_from == 'brand_default_assortments':
        sql_set_brand_default_assortment(trait_id=trait_id)

    @testpoint('v1-products-assortment')
    def _assortment(arg):
        assert arg['assortment_id'] == assortment_id

    request = {
        'products': [
            'item_origin_1_avail_null',
            'item_origin_2_avail_now',
            'item_origin_3_avail_past',
        ],
        'withCategories': True,
    }
    await taxi_eats_nomenclature.post(HANDLER + '?slug=slug', json=request)

    assert _assortment.has_calls


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_response_content_with_categories(
        taxi_eats_nomenclature, load_json, should_include_pennies_in_price,
):
    # Тест проверяет содержимое ответа ручки в случае withCategories = true.
    request = {
        'products': [
            'item_origin_1_avail_null',
            'item_origin_2_avail_now',
            'item_origin_3_avail_past',
            'item_origin_4_avail_future',
            'item_origin_5_avail_past_zero_stock',
            'item_origin_6_avail_past_null_stock',
            'item_origin_7_zero_price',
            'item_origin_8_null_price',
            'item_origin_12_force_unavailable',
        ],
        'withCategories': True,
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )

    assert response.status == 200
    assert 'categories' in response.json()
    response_json = response.json()
    response_json['categories'].sort(key=lambda category: category['id'])
    for category in response_json['categories']:
        category['items'].sort(key=lambda item: item['id'])

    expected_response = load_json('response_with_categories.json')
    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')

    assert response_json == expected_response


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_response_content_without_categories(
        taxi_eats_nomenclature, load_json, should_include_pennies_in_price,
):
    # Тест проверяет содержимое ответа ручки в случае withCategories = false.
    request = {
        'products': [
            'item_origin_1_avail_null',
            'item_origin_2_avail_now',
            'item_origin_3_avail_past',
            'item_origin_4_avail_future',
            'item_origin_5_avail_past_zero_stock',
            'item_origin_6_avail_past_null_stock',
            'item_origin_7_zero_price',
            'item_origin_8_null_price',
            'item_origin_11_zero_old_price',
            'item_origin_12_force_unavailable',
        ],
        'withCategories': False,
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )

    assert response.status == 200
    response_json = response.json()
    assert 'categories' in response_json
    assert len(response_json['categories']) == 1
    response_json['categories'][0]['items'].sort(key=lambda item: item['id'])

    expected_response = load_json('response_without_categories.json')
    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')
    assert response_json == expected_response


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_response_content(
        taxi_eats_nomenclature, load_json, should_include_pennies_in_price,
):
    # Тест проверяет содержимое ответа ручки, когда не задан
    # параметр withCategories. В этом случае ответ должен быть
    # таким же, как и при withCategories = false.
    request = {
        'products': [
            'item_origin_1_avail_null',
            'item_origin_2_avail_now',
            'item_origin_3_avail_past',
            'item_origin_4_avail_future',
            'item_origin_5_avail_past_zero_stock',
            'item_origin_6_avail_past_null_stock',
            'item_origin_7_zero_price',
            'item_origin_8_null_price',
            'item_origin_11_zero_old_price',
            'item_origin_12_force_unavailable',
        ],
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )

    assert response.status == 200
    response_json = response.json()
    assert 'categories' in response_json
    assert len(response_json['categories']) == 1
    response_json['categories'][0]['items'].sort(key=lambda item: item['id'])

    expected_response = load_json('response_without_categories.json')
    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')
    assert response_json == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'products_with_similar_origin_id2.sql',
    ],
)
async def test_products_with_same_origin_id2(
        taxi_eats_nomenclature,
        load_json,
        brand_task_enqueue,
        activate_assortment,
):
    """
    Тест проверяет, что ручка возвращает правильные товары,
    когда у разных заведений есть товары с одинаковым origin_id.
    """

    # original values for for these products are 20 and 300
    expected_measure_values = {'item_origin_10': 30, 'item_origin_20': 310}

    async def upload_data(brand_nomenclature, place_id=1):
        await brand_task_enqueue(
            brand_id='1',
            brand_nomenclature=brand_nomenclature,
            place_ids=[str(place_id)],
        )
        new_availabilities = [
            {'origin_id': 'item_origin_10', 'available': True},
            {'origin_id': 'item_origin_20', 'available': True},
        ]
        new_stocks = [
            {'origin_id': 'item_origin_10', 'stocks': None},
            {'origin_id': 'item_origin_20', 'stocks': None},
        ]
        new_prices = [
            {
                'origin_id': 'item_origin_10',
                'price': '1000',
                'currency': 'RUB',
            },
            {
                'origin_id': 'item_origin_20',
                'price': '1000',
                'currency': 'RUB',
            },
        ]

        await taxi_eats_nomenclature.invalidate_caches()
        await activate_assortment(
            new_availabilities,
            new_stocks,
            new_prices,
            place_id,
            '1',
            trait_id=1,
        )
        await taxi_eats_nomenclature.invalidate_caches()

    data_to_upload = load_json('s3_brand_nomenclature.json')
    await upload_data(data_to_upload)

    # upload products with the same origin_ids but different measure value.
    # since place brand is the same, the data should be overwritten
    # for the products with the same origin_id
    for item in data_to_upload['items']:
        item['measure']['value'] += 10
    await upload_data(data_to_upload, place_id=2)

    for slug in ['slug', 'slug2']:
        request = {'products': ['item_origin_10', 'item_origin_20']}
        response = await taxi_eats_nomenclature.post(
            HANDLER + f'?slug={slug}', json=request,
        )

        assert response.status == 200
        response_json = response.json()
        assert 'categories' in response_json
        assert len(response_json['categories']) == 1
        for product in response_json['categories'][0]['items']:
            assert product['id'] in expected_measure_values
            assert (
                product['measure']['value']
                == expected_measure_values[product['id']]
            )


@pytest.mark.parametrize(
    'experiment', ['enabled', 'enabled_with_excluded_brands', 'disabled'],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'products_for_sku_exp.sql',
    ],
)
async def test_sku_experiment(
        taxi_eats_nomenclature, load_json, experiments3, experiment,
):
    experiment_data = load_json('use_sku_experiment.json')
    if experiment == 'enabled':
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'true'
    elif experiment == 'enabled_with_excluded_brands':
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'true'
        experiment_data['experiments'][0]['clauses'][0]['value'][
            'excluded_brand_ids'
        ] = ['1']
    elif experiment == 'disabled':
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'false'
    experiments3.add_experiments_json(experiment_data)

    request = {
        'products': ['item_origin_1_avail_null', 'item_origin_2_avail_now'],
    }
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?slug=slug', json=request,
    )

    assert response.status == 200
    response_json = response.json()
    assert 'categories' in response_json
    assert len(response_json['categories']) == 1
    response_json['categories'][0]['items'].sort(key=lambda item: item['id'])

    if experiment == 'enabled':
        expected_json = load_json('response_with_sku.json')
        assert response_json == expected_json
    else:
        expected_json = load_json('response_without_sku.json')
        assert response_json == expected_json
