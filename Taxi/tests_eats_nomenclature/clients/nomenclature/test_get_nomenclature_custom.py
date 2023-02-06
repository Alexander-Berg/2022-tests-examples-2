import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'custom_categories.sql',
    ],
)
async def test_get_nomenclature_custom(
        taxi_eats_nomenclature, load_json, should_include_pennies_in_price,
):
    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )

    assert response.status == 200

    expected_response = _sorted_response(load_json('response.json'))
    if not should_include_pennies_in_price:
        for category in expected_response['categories']:
            pennies_utils.rounded_price(category, 'items')

    assert _sorted_response(response.json()) == expected_response


def _sorted_response(response):
    response['categories'].sort(key=lambda category: category['id'])
    for category in response['categories']:
        category['items'].sort(key=lambda item: item['id'])
    return response
