import ast

import pytest

from testsuite.utils import ordered_object

from . import sql_queries


@pytest.mark.pgsql(
    'overlord_catalog', files=['products.sql', 'refresh_wms_views.sql'],
)
@pytest.mark.parametrize('include_options', [None, True, False])
async def test_products_data(pgsql, taxi_overlord_catalog, include_options):
    """ Check /internal/v1/catalog/v1/products-data
    return three products ordered by id """
    expected_product_ids = [
        '88b4b661-aa33-11e9-b7ff-ac1f6b8569b3',
        '89cc6837-cb1e-11e9-b7ff-ac1f6b8569b3',
        'd36ff36d-cb3c-11e9-b7ff-ac1f6b8569b3',
    ]
    expected_products = _get_products_data(
        pgsql, expected_product_ids, include_options,
    )

    request_json = {'limit': 100, 'cursor': 0}
    if include_options is not None:
        request_json['include_options'] = include_options
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data', json=request_json,
    )
    assert response.status_code == 200
    products = response.json()['products']

    ordered_object.assert_eq(
        products, expected_products, ['options.pfc', 'options.storage'],
    )
    assert len(products) == sql_queries.count_products(pgsql)


async def test_products_data_with_master_categories(
        taxi_overlord_catalog, overlord_db, mock_grocery_depots,
):
    products = {}
    with overlord_db as db:
        depot = db.add_depot(depot_id=1, root_category_external_id='master')
        depot.add_category(category_id=3)
        depot.add_category(category_id=2, parent_id=3)
        category = depot.add_category(category_id=1, parent_id=2)
        products[0] = category.add_product(product_id=1)
        mock_grocery_depots.add_depot(depot)

    request_json = {'limit': 100, 'cursor': 0}
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data', json=request_json,
    )
    assert response.status_code == 200
    products = response.json()['products']
    assert products[0]['master_categories'] == [
        '01234567-89ab-cdef-000a-000001000001',
        '01234567-89ab-cdef-000a-000001000002',
        '01234567-89ab-cdef-000a-000001000003',
        '01234567-89ab-cdef-000a-000001000000',
    ]


@pytest.mark.pgsql(
    'overlord_catalog', files=['wms_menu_data.sql', 'refresh_wms_views.sql'],
)
async def test_products_data_chunked(pgsql, taxi_overlord_catalog, load_json):
    """ Check /internal/v1/catalog/v1/products-data
    return four chunks of different products sorted by id """
    response_len = [100, 52, 0]
    products = []
    limit = 100
    cursor = 0
    for length in response_len:
        response = await taxi_overlord_catalog.post(
            '/internal/v1/catalog/v1/products-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['products']) == length
        products.extend(response.json()['products'])

    products_ids_set = set()
    prev_product_id = None
    for item in products:
        product_id = item['product_id']
        products_ids_set.add(product_id)
        if prev_product_id:
            assert product_id > prev_product_id
        prev_product_id = product_id

    assert len(products) == len(products_ids_set)
    assert len(products) == sum(response_len)
    assert len(products) == sql_queries.count_products(pgsql)


@pytest.mark.pgsql(
    'overlord_catalog', files=['products.sql', 'refresh_wms_views.sql'],
)
async def test_products_data_search(pgsql, taxi_overlord_catalog):
    expected_product_ids = [
        '88b4b661-aa33-11e9-b7ff-ac1f6b8569b3',
        '89cc6837-cb1e-11e9-b7ff-ac1f6b8569b3',
        'd36ff36d-cb3c-11e9-b7ff-ac1f6b8569b3',
    ]

    bad_id = 'bad-id'

    expected_product_ids.append(bad_id)

    request_json = {'products': expected_product_ids}

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/selected-products-data', json=request_json,
    )
    assert response.status_code == 200
    products = response.json()['products']
    assert len(expected_product_ids) == len(products)

    for product in products:
        if product['product_info']['product_id'] != bad_id:
            assert product['state'] == 'found'
        else:
            assert product['state'] == 'not_found'


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_country_codes_and_ingredients(
        taxi_overlord_catalog, overlord_db,
):
    country_codes = ['RUS', 'ISR']
    value = 'piece of smth'
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        category.add_product(
            product_id=2,
            country='Fallback',
            country_of_origin=country_codes,
            ingredients={'ingredients': value},
        )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 10, 'cursor': 0, 'include_options': True},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['products'][0]['options']['country_codes'] == country_codes
    assert result['products'][0]['options']['ingredients'] == [
        {'key': 'ingredients', 'value': value},
    ]


def _get_product_options(db, product_id):
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT brand, country, shelf_life_measure_unit, amount,
        amount_unit, legal_restrictions, pfc, shelf_conditions,
        measurements, amount_unit_alias, grades, parent_id,
        important_ingredients, main_allergens,photo_stickers,
        custom_tags, logistic_tags, mark_count_pack, recycling_codes
        FROM catalog_wms.goods
        WHERE product_id = '{product_id}'""",
    )
    data = cursor.fetchall()[0]
    assert data
    options = {}
    if data[0]:
        options['brand'] = data[0]
    if data[1]:
        options['origin_country'] = data[1]
    options['shelf_life_measure_unit'] = data[2]
    options['amount'] = str(data[3]).rstrip('0').rstrip('.')
    options['amount_units'] = data[4]
    if data[5]:
        options['legal_restrictions'] = data[5]
    options['pfc'] = []
    for item in ast.literal_eval(data[6]):
        key, value = item[1:-1].split(',')
        options['pfc'].append({'key': key, 'value': value})
    options['storage'] = []
    for item in ast.literal_eval(data[7]):
        key, value = item[1:-1].split(',')
        options['storage'].append({'key': key, 'value': value.strip('\"')})
    options['country_codes'] = []
    options['ingredients'] = []
    if data[8]:
        options['measurements'] = {}
        for key, value in zip(
                ['width', 'height', 'depth', 'gross_weight', 'net_weight'],
                data[8][1:-1].split(','),
        ):
            if value:
                options['measurements'][key] = int(value)
    if data[9]:
        options['amount_units_alias'] = data[9]
    if data[10]:
        options['grades'] = data[10]
    if data[11]:
        options['parent_id'] = data[11]
    if data[12]:
        options['important_ingredients'] = data[12]
    if data[13]:
        options['main_allergens'] = data[13]
    if data[14]:
        options['photo_stickers'] = data[14]
    if data[15]:
        options['custom_tags'] = data[15]
    if data[16]:
        options['logistic_tags'] = data[16]
    if data[17]:
        options['amount_pack'] = data[17]
    if data[18]:
        options['recycling_codes'] = data[18]
    return options


def _get_products_data(pgsql, product_ids, include_options):
    db = pgsql['overlord_catalog']
    ret = []
    for product_id in product_ids:
        cursor = db.cursor()
        cursor.execute(
            f"""SELECT title,
                       long_title,
                       description,
                       images,
                       status,
                       external_id,
                       barcodes,
                       private_label
            FROM catalog_wms.goods WHERE product_id = '{product_id}'""",
        )
        data = cursor.fetchall()[0]
        assert data
        product = {}
        product['product_id'] = product_id
        product['title'] = data[0]
        product['long_title'] = data[1]
        product['description'] = data[2]
        if data[3]:
            product['image_url_template'] = data[3][0]
            product['image_url_templates'] = data[3]
        if include_options:
            product['options'] = _get_product_options(db, product_id)
        product['status'] = data[4]
        product['external_id'] = data[5]
        product['barcodes'] = data[6]
        product['private_label'] = data[7]
        ret.append(product)
    return ret


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_external_id(taxi_overlord_catalog, overlord_db):
    external_id = '424242'
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        category.add_product(product_id=2, external_id=external_id)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 10, 'cursor': 0, 'include_options': True},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['products'][0]['external_id'] == external_id


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_manufacturer(taxi_overlord_catalog, overlord_db):
    manufacturer = 'some company'
    country_codes = ['RUS', 'ISR']
    value = 'piece of smth'
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        category.add_product(
            product_id=2,
            country='Fallback',
            country_of_origin=country_codes,
            ingredients={'ingridients': value},
            manufacturer=manufacturer,
        )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 10, 'cursor': 0, 'include_options': True},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['products'][0]['options']['manufacturer'] == manufacturer


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_parent_products(taxi_overlord_catalog, overlord_db):
    grades = [['1200g', 'black'], 'M', 33]
    parent_id = 'fec55c4db86630003000100000464039a182c4487ac9'
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        category.add_product(product_id=2, grades=grades, parent_id=parent_id)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 10, 'cursor': 0, 'include_options': True},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['products'][0]['options']['grades'] == {
        'order': 33,
        'size': 'M',
        'values': ['1200g', 'black'],
    }
    assert result['products'][0]['options']['parent_id'] == parent_id


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_barcodes(taxi_overlord_catalog, overlord_db):
    barcode = '4860000001'
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        category.add_product(product_id=2, barcodes=[barcode])

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 10, 'cursor': 0, 'include_options': False},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['products'][0]['barcodes'] == [barcode]


# Проверяет, что выдача /products-data содержит НДС.
@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_vat(taxi_overlord_catalog, overlord_db):
    vat = '5.0'
    with overlord_db as db:
        depot = db.add_depot(depot_id=1)
        category = depot.add_category(category_id=1)
        category.add_product(product_id=2, vat=vat)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 10, 'cursor': 0, 'include_options': False},
    )
    assert response.status_code == 200
    result = response.json()
    assert result['products'][0]['vat'] == vat


# проверка, что products-data и selected-products-data возвращают
# одинаковую информацию о товарах
@pytest.mark.pgsql(
    'overlord_catalog', files=['products.sql', 'refresh_wms_views.sql'],
)
async def test_knobs_similarity(pgsql, taxi_overlord_catalog):
    expected_product_ids = [
        '88b4b661-aa33-11e9-b7ff-ac1f6b8569b3',
        '89cc6837-cb1e-11e9-b7ff-ac1f6b8569b3',
        'd36ff36d-cb3c-11e9-b7ff-ac1f6b8569b3',
    ]

    request_json = {'products': expected_product_ids}

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/selected-products-data', json=request_json,
    )
    assert response.status_code == 200
    selected_products = response.json()['products']
    assert len(expected_product_ids) == len(selected_products)

    for product in selected_products:
        assert product['state'] == 'found'

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/products-data',
        json={'limit': 3, 'include_options': True},
    )
    assert response.status_code == 200
    products = response.json()['products']
    assert len(products) == len(selected_products)

    for i, product in enumerate(products):
        assert product == selected_products[i]['product_info']
