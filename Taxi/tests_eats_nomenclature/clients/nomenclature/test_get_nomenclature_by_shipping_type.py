import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils


def sort_response(response):
    response['categories'].sort(key=lambda category: category['id'])
    for category in response['categories']:
        category['items'].sort(key=lambda item: item['id'])
    return response


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.parametrize('shipping_type', ['all', 'delivery', 'pickup'])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_shipping_all(
        taxi_eats_nomenclature,
        load_json,
        shipping_type,
        should_include_pennies_in_price,
):
    category_id = 'category_1_origin'

    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug=slug&category_id={category_id}'
        f'&shipping_type={shipping_type}',
    )

    assert response.status == 200

    expected_response = filter_by_shipping_type(
        load_json('response.json'), shipping_type,
    )
    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')

    assert sort_response(response.json()) == sort_response(expected_response)


def filter_by_shipping_type(data, shipping_type):
    if shipping_type == 'all':
        return data

    for category in data['categories']:
        category['items'] = [
            i
            for i in category['items']
            if (
                i['shipping_type'] == shipping_type
                or i['shipping_type'] == 'all'
            )
        ]

    return data
