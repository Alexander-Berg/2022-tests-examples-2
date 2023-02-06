import pytest


from ... import utils


def sort_response(response):
    response['categories'].sort(key=lambda category: category['id'])
    for category in response['categories']:
        category['items'].sort(key=lambda item: item['id'])
    return response


@pytest.mark.parametrize('use_full_price', [True, False])
@pytest.mark.parametrize(
    'is_catch_weight, measure_in, measure_out',
    [
        pytest.param(
            False,
            {'quantum': 0.5, 'unit': 'GRM', 'value': 1000},
            {'quantum': 0.5, 'unit': 'GRM', 'value': 1000},
            id='no weight items',
        ),
        pytest.param(
            True,
            {'quantum': 0.5, 'unit': 'GRM', 'value': 1000},
            {'quantum': 0.5, 'unit': 'GRM', 'value': 500},
            id='simple weight items',
        ),
        pytest.param(
            True,
            {'quantum': 0, 'unit': 'GRM', 'value': 1000},
            {'quantum': 0, 'unit': 'GRM', 'value': 1000},
            id='zero quantum',
        ),
        pytest.param(
            True,
            {'unit': 'GRM', 'value': 1000},
            {'quantum': 0, 'unit': 'GRM', 'value': 1000},
            id='no quantum',
        ),
    ],
)
@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param('/v1/nomenclature', id='get nomenclature'),
        pytest.param('/v1/products', id='post products'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_weight_products(
        taxi_eats_nomenclature,
        load_json,
        is_catch_weight,
        measure_in,
        measure_out,
        api_handler,
        activate_assortment,
        brand_task_enqueue,
        use_full_price,
):
    request_json = load_json('request.json')
    request_json['items'][0]['is_catch_weight'] = is_catch_weight
    request_json['items'][0]['measure'] = measure_in

    response_json = load_json('response_brand_nomenclature.json')
    response_json['categories'][0]['items'][0][
        'is_catch_weight'
    ] = is_catch_weight
    response_json['categories'][0]['items'][0]['measure'] = measure_out
    full_price = 400
    if use_full_price:
        response_json['categories'][0]['items'][0]['price'] = full_price
        if is_catch_weight:
            response_json['categories'][0]['items'][0]['price'] = (
                response_json['categories'][0]['items'][0]['price']
                * response_json['categories'][0]['items'][0]['measure'][
                    'quantum'
                ]
            )
    place_id = 1
    await brand_task_enqueue(brand_nomenclature=request_json)
    new_availabilities = [{'origin_id': 'item_id_1', 'available': True}]
    new_stocks = [{'origin_id': 'item_id_1', 'stocks': None}]
    if use_full_price:
        new_prices = [
            {
                'origin_id': 'item_id_1',
                'price': '1000',
                'full_price': str(full_price),
                'currency': 'RUB',
            },
        ]
    else:
        new_prices = [
            {'origin_id': 'item_id_1', 'price': '1000', 'currency': 'RUB'},
        ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )
    await taxi_eats_nomenclature.invalidate_caches()

    if api_handler == '/v1/nomenclature':
        response = await taxi_eats_nomenclature.get(
            '/v1/nomenclature?slug=lavka_krasina&category_id=category_2_id',
        )
    else:
        response = await taxi_eats_nomenclature.post(
            '/v1/products?slug=lavka_krasina',
            json={'products': ['item_id_1'], 'withCategories': True},
        )

    actual_response = utils.remove_public_id(response.json())
    assert sort_response(actual_response) == sort_response(response_json)
