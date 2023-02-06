import copy
import unicodedata

import pytest

from . import utils

ALL_CACHES = [
    'product-cache',
    'product-barcodes-cache',
    'product-pictures-cache',
    'picture-cache',
    'barcode-cache',
    'place-cache',
    'place-assortment-cache',
]


S3_PATH = '/some/path/availabilities.json'


def remove_categories(data):
    data['categories'] = []
    return data


def remove_items(data):
    for cat in data['categories']:
        cat['items'] = []
    return data


def remove_barcodes(data):
    for cat in data['categories']:
        for item in cat['items']:
            item.pop('barcode', None)
            item['barcodes'] = []
    return data


def remove_images(data):
    for cat in data['categories']:
        cat['images'] = []
        for item in cat['items']:
            item['images'] = []
    return data


def sort_response(response):
    response['categories'].sort(key=lambda category: category['id'])
    for category in response['categories']:
        category['items'].sort(key=lambda item: item['id'])
    return response


@pytest.mark.parametrize(
    'cache_name, data_filter',
    [
        ('product-cache', remove_items),
        ('picture-cache', remove_images),
        ('barcode-cache', remove_barcodes),
        ('place-assortment-cache', remove_categories),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_store_and_load_nomenclature(
        taxi_eats_nomenclature,
        load_json,
        cache_name,
        data_filter,
        activate_assortment,
        brand_task_enqueue,
):
    request_json = load_json('request.json')

    place_id = 1
    await brand_task_enqueue(brand_nomenclature=request_json)
    new_availabilities = [{'origin_id': 'item_id_1', 'available': True}]
    new_stocks = [{'origin_id': 'item_id_1', 'stocks': None}]
    new_prices = [
        {'origin_id': 'item_id_1', 'price': '1000', 'currency': 'RUB'},
    ]

    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    query = '/v1/nomenclature?slug=lavka_krasina&category_id=category_2_id'
    full_response = load_json('response_brand_nomenclature.json')
    assert cache_name in ALL_CACHES

    # Load all caches except the one we are testing

    await taxi_eats_nomenclature.invalidate_caches(
        clean_update=False,
        cache_names=[c for c in ALL_CACHES if c is not cache_name],
    )
    response = await taxi_eats_nomenclature.get(query)
    response_json = utils.remove_public_id(response.json())
    assert sort_response(response_json) == sort_response(
        data_filter(copy.deepcopy(full_response)),
    )

    # Load the tested cache
    await taxi_eats_nomenclature.invalidate_caches(
        clean_update=False, cache_names=[cache_name],
    )
    response = await taxi_eats_nomenclature.get(query)
    response_json = utils.remove_public_id(response.json())
    assert sort_response(response_json) == sort_response(full_response)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_categories_public_id.sql'],
)
async def test_categories_public_id(
        taxi_eats_nomenclature,
        pgsql,
        load_json,
        activate_assortment,
        brand_task_enqueue,
):
    categories_dictionary_by_key = {
        (row[1], row[2]): row[0] for row in get_categories_dictionary(pgsql)
    }
    assert set(categories_dictionary_by_key.keys()) == {
        ('молочные изделия', None),
        ('молочные изделия 5', None),
        ('сыр', 222),
        ('зелёное молоко', 555),
    }

    request = load_json('request_categories_public_id.json')

    # Normalize last category name to NFD form
    # Do it here because storing plain NFD text in JSON is error-prone and
    # 'files-comparer' check prohibits using '\uXXXX' in JSON
    last_cat = request['categories'][-1]
    last_cat_name_decomp = unicodedata.normalize('NFD', last_cat['name'])
    assert last_cat_name_decomp != last_cat['name']
    last_cat['name'] = last_cat_name_decomp

    place_id = 1
    await brand_task_enqueue(brand_nomenclature=request)

    new_availabilities = [{'origin_id': 'item_id_1', 'available': True}]
    new_stocks = [{'origin_id': 'item_id_1', 'stocks': None}]
    new_prices = [
        {
            'origin_id': 'item_id_1',
            'price': '1000',
            'old_price': '1000',
            'currency': 'RUB',
            'vat': '10',
        },
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    await taxi_eats_nomenclature.invalidate_caches(
        clean_update=False, cache_names=[c for c in ALL_CACHES],
    )

    categories_dictionary_by_key = {
        (row[1], row[2]): row[0] for row in get_categories_dictionary(pgsql)
    }

    assert set(categories_dictionary_by_key.keys()) == {
        ('молочные изделия', None),
        ('молочные изделия 5', None),
        ('молоко', 222),
        ('test', 222),
        ('сыр', 222),
        ('кефир', 555),
        ('сыр', 555),
        ('зелёное молоко', 555),
    }

    expected_categories_by_root = {}
    root_category_id_by_id = {}
    categories_added = True
    while categories_added:
        categories_added = False
        # This simple iteration has O(n^2) time complexity for n categories
        # but for tests its fine
        for category in request['categories']:
            category_id = category['origin_id']
            if category_id in root_category_id_by_id:
                continue
            [parent_id] = category.get('parent_origin_ids', [None])
            if parent_id is None:
                expected_categories_by_root[category_id] = {}
                root_category_id = category_id
            else:
                if parent_id not in root_category_id_by_id:
                    continue
                root_category_id = root_category_id_by_id[parent_id]
            root_category_id_by_id[category_id] = root_category_id
            expected_categories = expected_categories_by_root[root_category_id]

            norm_lower_name = unicodedata.normalize(
                'NFC', category['name'].lower(),
            )
            parent_public_id = (
                expected_categories[parent_id]['public_id']
                if parent_id is not None
                else None
            )
            public_id = categories_dictionary_by_key[
                (norm_lower_name, parent_public_id)
            ]

            expected_category = {
                'id': category_id,
                'public_id': public_id,
                'name': category['name'],
                'sort_order': category['sort_order'],
                'parent_id': parent_id,
                'parent_public_id': parent_public_id,
            }

            expected_categories[category_id] = expected_category
            categories_added = True
    assert len(root_category_id_by_id) == len(request['categories'])

    for root_category_id, expected_categories in sorted(
            expected_categories_by_root.items(),
    ):
        query = (
            '/v1/nomenclature?slug=lavka_krasina&category_id='
            + root_category_id
        )
        response = await taxi_eats_nomenclature.get(query)

        response_categories = {}
        for category in response.json()['categories']:
            response_category = {
                'id': category['id'],
                'public_id': category['public_id'],
                'name': category['name'],
                'sort_order': category['sort_order'],
                'parent_id': None,
                'parent_public_id': None,
            }
            if 'parent_id' in category:
                response_category['parent_id'] = category['parent_id']
            if 'parent_public_id' in category:
                response_category['parent_public_id'] = category[
                    'parent_public_id'
                ]
            response_categories[category['id']] = response_category
        assert response_categories == expected_categories


def get_categories_dictionary(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id, name, parent_id from eats_nomenclature.categories_dictionary
        order by id
        """,
    )

    return list(cursor)
