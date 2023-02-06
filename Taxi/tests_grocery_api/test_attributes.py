import pytest

from . import common


@pytest.mark.translations(
    wms_attributes={
        'sahar': {'en': 'shugar'},
        'fish': {'en': 'translated_fish'},
        'myaso(dlya veganov)': {'en': 'meet'},
        'кашерно': {'en': 'kosher'},
        'important_ingredients': {'en': 'i love it'},
    },
)
@pytest.mark.config(GROCERY_LOCALIZATION_ATTRIBUTES_KEYSET='wms_attributes')
@pytest.mark.config(
    GROCERY_API_ATTRIBUTES_ICONS={
        'sahar': {'icon_link': 'sahar_icon'},
        'fish': {'icon_link': 'fish_icon', 'big_icon_link': 'big_fish_icon'},
    },
)
async def test_attributes_all_attributes_in_response(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        load_json,
        empty_upsale,
):
    location = [0, 0]
    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    options = {
        'shelf_life_measure_unit': 'DAY',
        'amount': '1.5',
        'amount_units': 'kg',
        'pfc': [],
        'storage': [],
        'ingredients': [{'key': 'ingredients', 'value': 'piece of something'}],
        'country_codes': ['rus'],
    }
    products_data[1]['options'] = options
    products_data[2]['options'] = options
    products_data[1]['options']['important_ingredients'] = [
        'myaso(dlya veganov)',
    ]
    products_data[2]['options']['custom_tags'] = ['кашерно']
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, products_data,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/attributes/list',
        json={},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'custom_tags': {
            'attributes': [
                {'attribute': 'halal', 'title': 'halal'},
                {'attribute': 'кашерно', 'title': 'kosher'},
            ],
            'title': 'custom_tags',
        },
        'important_ingredients': {
            'attributes': [
                {'attribute': 'myaso(dlya veganov)', 'title': 'meet'},
                {
                    'attribute': 'sahar',
                    'title': 'shugar',
                    'icon_link': 'sahar_icon',
                },
            ],
            'title': 'i love it',
        },
        'main_allergens': {
            'attributes': [
                {
                    'attribute': 'fish',
                    'title': 'translated_fish',
                    'icon_link': 'fish_icon',
                    'big_icon_link': 'big_fish_icon',
                },
            ],
            'title': 'main_allergens',
        },
    }
