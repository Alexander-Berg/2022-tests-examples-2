import pytest

from testsuite.utils import ordered_object

# pylint: disable=too-many-lines

from tests_grocery_products import common


def check_db_single_record(
        pgsql, data_to_check, virtual_category_id, alias=None,
):
    db = pgsql['grocery_products']
    cursor = db.cursor()
    data_to_check = data_to_check.items()
    select_query = ','.join([name for name, _ in data_to_check])
    key_values = [value for _, value in data_to_check]
    # Check that materialized view refreshed
    cursor.execute(
        f"""SELECT {select_query}
        FROM products.{common.VIRTUAL_CATEGORIES_WITH_SUBCATEGORIES_VIEW_NAME}
        WHERE id = '{virtual_category_id}'"""
        + (';' if alias is None else f""" AND alias = '{alias}';"""),
    )

    data = cursor.fetchall()
    assert len(data) == 1
    assert list(data[0]) == key_values


# Checks /admin/products/v3/categories POST
# insert new values into virtual_categories table
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'alias,tanker_key,meta,status',
    [
        (
            'test-alias-active',
            'tanker_key_active',
            '{ "meta-active": "meta-active" }',
            'active',
        ),
        (
            'test-alias-disabled',
            'tanker_key_disabled',
            '{ "meta-disabled": "meta-disabled" }',
            'disabled',
        ),
    ],
)
async def test_categories_post_basic(
        taxi_grocery_products, pgsql, alias, tanker_key, meta, status,
):
    json = {
        'alias': alias,
        'title_tanker_key': tanker_key,
        'subcategories': [],
        'images': [],
        'meta': meta,
        'status': status,
    }

    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories', json=json,
    )
    assert response.status_code == 200

    response_data = response.json()
    virtual_category_id = response_data['id']
    common.compare_request_and_response(
        virtual_category_id, json, response_data,
    )

    check_db_single_record(
        pgsql,
        {
            'id': virtual_category_id,
            'alias': alias,
            'title_tanker_key': tanker_key,
            'meta': meta,
            'status': status,
        },
        virtual_category_id,
        alias,
    )


# Checks /admin/products/v3/categories POST
# insert new values into virtual_categories_subcategories table
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'subcategories,expected_subcategories',
    [
        (['one-sub'], '{"(one-sub,1)"}'),
        (['two-subs-1', 'two-subs-2'], '{"(two-subs-1,1)","(two-subs-2,2)"}'),
        (['z', 'a'], '{"(a,2)","(z,1)"}'),
    ],
)
async def test_categories_post_with_subcategories(
        taxi_grocery_products, pgsql, subcategories, expected_subcategories,
):
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'tanker_key_test',
        'subcategories': subcategories,
        'images': [],
        'meta': '{}',
        'status': 'active',
    }

    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories', json=json,
    )
    assert response.status_code == 200
    response_data = response.json()
    virtual_category_id = response_data['id']
    common.compare_request_and_response(
        virtual_category_id, json, response_data,
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT subcategory_id, rank
        FROM products.virtual_categories_subcategories
        WHERE virtual_category_id = '{virtual_category_id}'
        ORDER BY rank;""",
    )
    data = cursor.fetchall()
    assert len(data) == len(subcategories)
    for i, item in enumerate(data):
        assert item[0] == subcategories[i]
        assert item[1] == i + 1

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT subcategories
        FROM products.{common.VIRTUAL_CATEGORIES_WITH_SUBCATEGORIES_VIEW_NAME}
        WHERE id = '{virtual_category_id}';""",
    )
    assert expected_subcategories == cursor.fetchall()[0][0]


# Checks /admin/products/v3/categories POST
# insert new values into virtual_categories_images table
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'images,db_images,view_images',
    [
        (
            [{'id': 'one/image', 'dimensions': [{'width': 2, 'height': 2}]}],
            [('one/image', '(2,2)')],
            '{"(one/image,\\"(2,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'one/image/multi',
                    'dimensions': [
                        {'width': 2, 'height': 2},
                        {'width': 4, 'height': 2},
                    ],
                },
            ],
            [('one/image/multi', '(2,2)'), ('one/image/multi', '(4,2)')],
            '{"(one/image/multi,\\"(2,2)\\")",'
            '"(one/image/multi,\\"(4,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'two/images1',
                    'dimensions': [{'width': 4, 'height': 2}],
                },
                {
                    'id': 'two/images2',
                    'dimensions': [{'width': 6, 'height': 2}],
                },
            ],
            [('two/images1', '(4,2)'), ('two/images2', '(6,2)')],
            '{"(two/images1,\\"(4,2)\\")","(two/images2,\\"(6,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'two/images1',
                    'dimensions': [{'width': 4, 'height': 2}],
                },
                {
                    'id': 'two/images2/multi',
                    'dimensions': [
                        {'width': 2, 'height': 2},
                        {'width': 6, 'height': 2},
                    ],
                },
            ],
            [
                ('two/images1', '(4,2)'),
                ('two/images2/multi', '(2,2)'),
                ('two/images2/multi', '(6,2)'),
            ],
            '{"(two/images1,\\"(4,2)\\")","(two/images2/multi,\\"(2,2)\\")"'
            ',"(two/images2/multi,\\"(6,2)\\")"}',
        ),
    ],
)
async def test_categories_post_with_images(
        taxi_grocery_products, pgsql, images, db_images, view_images,
):
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'tanker_key_test',
        'subcategories': [],
        'images': images,
        'meta': '{ "meta_test": "meta_test" }',
        'status': 'active',
    }

    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories', json=json,
    )
    assert response.status_code == 200
    response_data = response.json()
    virtual_category_id = response_data['id']
    common.compare_request_and_response(
        virtual_category_id, json, response_data,
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT image_id, image_dimensions
        FROM products.virtual_categories_images
        WHERE virtual_category_id = '{virtual_category_id}'
        ORDER BY image_id, image_dimensions;""",
    )
    data = cursor.fetchall()
    assert data == db_images

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT images
        FROM products.{common.VIRTUAL_CATEGORIES_WITH_SUBCATEGORIES_VIEW_NAME}
        WHERE id = '{virtual_category_id}';""",
    )
    ordered_object.assert_eq(view_images, cursor.fetchall()[0][0], [''])


# Checks /admin/products/v3/categories POST
# return 409 on alias constraint conflict
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'virtual_category_id,alias,code,message',
    [
        (
            'ok-id',
            'alias-2',
            'CATEGORY_ALIAS_ALREADY_EXISTS',
            'Virtual category with alias "alias-2" already exists',
        ),
    ],
)
async def test_categories_post_409(
        taxi_grocery_products,
        pgsql,
        virtual_category_id,
        alias,
        code,
        message,
):
    await taxi_grocery_products.invalidate_caches()
    json = {
        'id': virtual_category_id,
        'alias': alias,
        'title_tanker_key': 'tanker_key',
        'subcategories': [],
        'images': [],
        'meta': '{ "meta": "meta" }',
        'status': 'active',
    }

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.virtual_categories""",
    )
    records_before = cursor.fetchall()[0][0]

    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories', json=json,
    )

    assert response.status_code == 409
    assert response.json()['code'] == code
    assert response.json()['message'] == message

    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.virtual_categories""",
    )
    assert records_before == cursor.fetchall()[0][0]


# Checks /admin/products/v3/categories PUT
# update existing values in virtual_categories table
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'virtual_category_id,alias,tanker_key,meta,status',
    [
        (
            'virtual-category-1',
            'test-alias-active',
            'tanker_key_active',
            '{ "meta_active": "meta_active" }',
            'active',
        ),
        (
            'virtual-category-2',
            'alias-2',
            'tanker_key_ok',
            '{ "meta_ok": "meta_ok" }',
            'active',
        ),
    ],
)
async def test_categories_put_basic(
        taxi_grocery_products,
        pgsql,
        virtual_category_id,
        alias,
        tanker_key,
        meta,
        status,
):
    json = {
        'alias': alias,
        'title_tanker_key': tanker_key,
        'subcategories': [],
        'images': [],
        'meta': meta,
        'status': status,
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories',
        params={'category_id': virtual_category_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        virtual_category_id, json, response.json(),
    )

    check_db_single_record(
        pgsql,
        {
            'alias': alias,
            'title_tanker_key': tanker_key,
            'meta': meta,
            'status': status,
        },
        virtual_category_id,
    )


# Checks /admin/products/v3/categories PUT
# update optional field in category database record
# in which this field is uninitialized
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'test_field',
    [
        pytest.param({'deep_link': 'test_deep_link'}, id='deep link'),
        pytest.param({'is_special_category': True}),
        pytest.param({'short_title_tanker_key': 'short_title_tanker_key-1'}),
        pytest.param({'special_category': 'promo-caas'}),
    ],
)
async def test_categories_put_optional_field(
        taxi_grocery_products, pgsql, test_field,
):
    virtual_category_id = 'virtual-category-1'
    json = {
        'alias': 'alias-1',
        'title_tanker_key': 'title_tanker_key-1',
        'subcategories': [],
        'images': [],
        'meta': '{ "meta-1": "meta-1" }',
        'status': 'active',
        **test_field,
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories',
        params={'category_id': virtual_category_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        virtual_category_id, json, response.json(),
    )
    check_db_single_record(pgsql, test_field, virtual_category_id)


# Checks /admin/products/v3/categories PUT
# return 404 when category not found in cache
# return 409 on category_id edit
@pytest.mark.pgsql(
    'grocery_products',
    files=['default.sql', '409error.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'virtual_category_id,alias,status_code,code,message,status,images',
    [
        (
            'category-not-found',
            'category-not-found-alias',
            404,
            'CATEGORY_NOT_FOUND',
            'Virtual category with id "category-not-found" not found',
            'active',
            [],
        ),
        (
            'virtual-category-1',
            'alias-2',
            409,
            'CATEGORY_ALIAS_ALREADY_EXISTS',
            'Virtual category with alias "alias-2" already exists',
            'active',
            [],
        ),
        (
            'category-11-1',
            'alias-5',
            409,
            'CANNOT_DISABLE_CATEGORY',
            'Virtual category with id "category-11-1" can\'t be '
            'disabled, as it\'s attached to a layout with id "layout-1"',
            'disabled',
            [],
        ),
        (
            'category-11-2',
            'alias-5',
            409,
            'CANNOT_UNBIND_IMAGE',
            'Image "image-category-11-2 2x2" can\'t be '
            'Unbound, as it\'s attached to a layout with id "layout-2"',
            'active',
            [],
        ),
        (
            'category-11-3',
            'alias-7',
            409,
            'CANNOT_UNBIND_IMAGE',
            'Image "image-category-11-3 2x4" can\'t be '
            'Unbound, as it\'s attached to a layout with id "layout-1"',
            'active',
            [
                {
                    'id': 'image-category-11-3',
                    'dimensions': [{'width': 2, 'height': 2}],
                },
            ],
        ),
    ],
)
async def test_categories_put_error(
        taxi_grocery_products,
        pgsql,
        virtual_category_id,
        alias,
        status_code,
        code,
        message,
        status,
        images,
):
    json = {
        'alias': alias,
        'title_tanker_key': '',
        'subcategories': [],
        'images': images,
        'meta': '{}',
        'status': status,
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories',
        params={'category_id': virtual_category_id},
        json=json,
    )
    assert response.status_code == status_code
    assert response.json()['code'] == code
    assert response.json()['message'] == message


# Checks /admin/products/v3/categories PUT
# update new values in virtual_categories_subcategories table
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'subcategories,expected_subcategories',
    [
        (['one-sub'], '{"(one-sub,1)"}'),
        (['two-subs-1', 'two-subs-2'], '{"(two-subs-1,1)","(two-subs-2,2)"}'),
        (['z', 'a'], '{"(a,2)","(z,1)"}'),
    ],
)
async def test_categories_put_with_subcategories(
        taxi_grocery_products, pgsql, subcategories, expected_subcategories,
):
    virtual_category_id = 'virtual-category-1'
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'tanker_key_test',
        'subcategories': subcategories,
        'images': [],
        'meta': '{ "meta_test": "meta_test" }',
        'status': 'active',
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories',
        params={'category_id': virtual_category_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        virtual_category_id, json, response.json(),
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT subcategory_id, rank
        FROM products.virtual_categories_subcategories
        WHERE virtual_category_id = '{virtual_category_id}'
        ORDER BY rank;""",
    )
    data = cursor.fetchall()
    assert len(data) == len(subcategories)
    for i, item in enumerate(data):
        assert item[0] == subcategories[i]
        assert item[1] == i + 1

    # Check that materialized view refreshed after update
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT subcategories
        FROM products.{common.VIRTUAL_CATEGORIES_WITH_SUBCATEGORIES_VIEW_NAME}
        WHERE id = '{virtual_category_id}';""",
    )
    assert expected_subcategories == cursor.fetchall()[0][0]


# Checks /admin/products/v3/categories PUT
# update values in virtual_categories_images table
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'images,db_images,view_images',
    [
        (
            [{'id': 'one/image', 'dimensions': [{'width': 2, 'height': 2}]}],
            [('one/image', '(2,2)')],
            '{"(one/image,\\"(2,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'one/image/multi',
                    'dimensions': [
                        {'width': 2, 'height': 2},
                        {'width': 4, 'height': 2},
                    ],
                },
            ],
            [('one/image/multi', '(2,2)'), ('one/image/multi', '(4,2)')],
            '{"(one/image/multi,\\"(2,2)\\")",'
            '"(one/image/multi,\\"(4,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'two/images1',
                    'dimensions': [{'width': 4, 'height': 2}],
                },
                {
                    'id': 'two/images2',
                    'dimensions': [{'width': 6, 'height': 2}],
                },
            ],
            [('two/images1', '(4,2)'), ('two/images2', '(6,2)')],
            '{"(two/images1,\\"(4,2)\\")","(two/images2,\\"(6,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'two/images1',
                    'dimensions': [{'width': 4, 'height': 2}],
                },
                {
                    'id': 'two/images2/multi',
                    'dimensions': [
                        {'width': 2, 'height': 2},
                        {'width': 6, 'height': 2},
                    ],
                },
            ],
            [
                ('two/images1', '(4,2)'),
                ('two/images2/multi', '(2,2)'),
                ('two/images2/multi', '(6,2)'),
            ],
            '{"(two/images1,\\"(4,2)\\")","(two/images2/multi,\\"(2,2)\\")",'
            '"(two/images2/multi,\\"(6,2)\\")"}',
        ),
    ],
)
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
async def test_categories_put_with_images(
        taxi_grocery_products, pgsql, images, db_images, view_images,
):
    virtual_category_id = 'virtual-category-1'
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'tanker_key_test',
        'subcategories': [],
        'images': images,
        'meta': '{ "meta_test": "meta_test" }',
        'status': 'active',
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories',
        params={'category_id': virtual_category_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        virtual_category_id, json, response.json(),
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT image_id, image_dimensions
        FROM products.virtual_categories_images
        WHERE virtual_category_id = '{virtual_category_id}'
        ORDER BY image_id, image_dimensions;""",
    )
    data = cursor.fetchall()
    assert data == db_images

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT images
        FROM products.{common.VIRTUAL_CATEGORIES_WITH_SUBCATEGORIES_VIEW_NAME}
        WHERE id = '{virtual_category_id}';""",
    )
    ordered_object.assert_eq(view_images, cursor.fetchall()[0][0], [''])


# Checks /admin/products/v3/categories GET
# Return virtual category info by id
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'virtual_category_id,virtual_category_json',
    [
        (
            'virtual-category-1',
            {
                'id': 'virtual-category-1',
                'alias': 'alias-1',
                'title_tanker_key': 'title_tanker_key-1',
                'subcategories': [
                    'subcategory-for-1',
                    'subcategory-for-12',
                    'subcategory-for-123',
                ],
                'images': [
                    {
                        'id': 'image11',
                        'dimensions': [{'width': 2, 'height': 2}],
                    },
                    {
                        'id': 'image12',
                        'dimensions': [{'width': 2, 'height': 6}],
                    },
                    {
                        'id': 'image13',
                        'dimensions': [{'width': 2, 'height': 4}],
                    },
                ],
                'meta': '{ "meta-1": "meta-1" }',
                'status': 'active',
            },
        ),
        (
            'virtual-category-no-subs',
            {
                'id': 'virtual-category-no-subs',
                'alias': 'alias-no-subs',
                'title_tanker_key': 'title_tanker_key-no-subs',
                'subcategories': [],
                'images': [
                    {
                        'id': 'image-for-no-subs-1',
                        'dimensions': [{'width': 3, 'height': 2}],
                    },
                    {
                        'id': 'image-for-no-subs-2',
                        'dimensions': [{'width': 3, 'height': 4}],
                    },
                ],
                'meta': '{ "meta-no-subs": "meta-no-subs" }',
                'status': 'active',
            },
        ),
        (
            'virtual-category-disabled',
            {
                'id': 'virtual-category-disabled',
                'alias': 'alias-disabled',
                'title_tanker_key': 'title_tanker_key-disabled',
                'subcategories': ['subcategory-for-disabled'],
                'images': [
                    {
                        'id': 'image-for-disabled-1',
                        'dimensions': [{'width': 1, 'height': 3}],
                    },
                    {
                        'id': 'image-for-disabled-2',
                        'dimensions': [{'width': 1, 'height': 4}],
                    },
                ],
                'meta': '{ "meta-disabled": "meta-disabled" }',
                'status': 'disabled',
            },
        ),
        (
            'virtual-category-short-tanker',
            {
                'alias': 'alias-4',
                'id': 'virtual-category-short-tanker',
                'title_tanker_key': 'title_tanker_key-4',
                'short_title_tanker_key': 'short_title_tanker_key-4',
                'images': [],
                'meta': '{ "meta-4": "meta-4" }',
                'status': 'active',
                'subcategories': [],
            },
        ),
        (
            'virtual-category-special',
            {
                'alias': 'alias-special',
                'id': 'virtual-category-special',
                'title_tanker_key': 'title_tanker_key-1',
                'is_special_category': True,
                'images': [],
                'meta': '{meta-1}',
                'status': 'active',
                'subcategories': [],
            },
        ),
        (
            'virtual-category-with-deeplink',
            {
                'alias': 'alias-deeplink',
                'id': 'virtual-category-with-deeplink',
                'title_tanker_key': 'title_tanker_key-1',
                'images': [],
                'meta': '{meta-1}',
                'status': 'active',
                'subcategories': [],
                'deep_link': 'category-deep-link',
            },
        ),
        (
            'virtual-category-multi-dimensions',
            {
                'id': 'virtual-category-multi-dimensions',
                'alias': 'alias-multi-dimensions',
                'title_tanker_key': 'title_tanker_key-multi-dimensions',
                'subcategories': [],
                'images': [
                    {
                        'id': 'image-for-md-1',
                        'dimensions': [
                            {'width': 2, 'height': 2},
                            {'width': 4, 'height': 2},
                        ],
                    },
                    {
                        'id': 'image-for-md-2',
                        'dimensions': [{'width': 6, 'height': 2}],
                    },
                ],
                'meta': '{ "meta-multi-dimensions": "meta-multi-dimensions" }',
                'status': 'active',
            },
        ),
        (
            'virtual-category-with-special-category',
            {
                'alias': 'alias-special-category',
                'id': 'virtual-category-with-special-category',
                'title_tanker_key': 'title_tanker_key-1',
                'images': [],
                'meta': '{meta-1}',
                'status': 'active',
                'subcategories': [],
                'special_category': 'promo-caas',
            },
        ),
    ],
)
async def test_categories_get_200(
        taxi_grocery_products, virtual_category_id, virtual_category_json,
):
    await taxi_grocery_products.invalidate_caches()

    response = await taxi_grocery_products.get(
        '/admin/products/v3/categories',
        params={'category_id': virtual_category_id},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), virtual_category_json, ['images'],
    )


# Checks /admin/products/v3/categories GET
# Return 404 when id not found in cache
async def test_categories_get_404(taxi_grocery_products):
    response = await taxi_grocery_products.get(
        '/admin/products/v3/categories',
        params={'category_id': 'category-not-fond-id'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'CATEGORY_NOT_FOUND'
    assert (
        response.json()['message']
        == 'Virtual category with id "category-not-fond-id" not found'
    )


# Checks /admin/products/v3/categories/list POST
# get all values from virtual categories cache
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
async def test_categories_list_post(taxi_grocery_products, load_json):

    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories/list', json={},
    )
    assert response.status_code == 200
    expected = load_json('categories_list_expected_response.json')
    ordered_object.assert_eq(
        response.json(),
        expected,
        ['categories', 'categories.subcategories', 'categories.images'],
    )


# Checks /admin/products/v3/categories/set-status PUT
# change status of existing virtual category
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize('status', ['active', 'disabled'])
@pytest.mark.parametrize(
    'virtual_category_id,virtual_category_json',
    [
        (
            'virtual-category-1',
            {
                'id': 'virtual-category-1',
                'alias': 'alias-1',
                'title_tanker_key': 'title_tanker_key-1',
                'subcategories': [
                    'subcategory-for-1',
                    'subcategory-for-12',
                    'subcategory-for-123',
                ],
                'images': [
                    {
                        'id': 'image11',
                        'dimensions': [{'width': 2, 'height': 2}],
                    },
                    {
                        'id': 'image12',
                        'dimensions': [{'width': 2, 'height': 6}],
                    },
                    {
                        'id': 'image13',
                        'dimensions': [{'width': 2, 'height': 4}],
                    },
                ],
                'meta': '{ "meta-1": "meta-1" }',
                'status': 'active',
            },
        ),
        (
            'virtual-category-disabled',
            {
                'id': 'virtual-category-disabled',
                'alias': 'alias-disabled',
                'title_tanker_key': 'title_tanker_key-disabled',
                'subcategories': ['subcategory-for-disabled'],
                'images': [
                    {
                        'id': 'image-for-disabled-1',
                        'dimensions': [{'width': 1, 'height': 3}],
                    },
                    {
                        'id': 'image-for-disabled-2',
                        'dimensions': [{'width': 1, 'height': 4}],
                    },
                ],
                'meta': '{ "meta-disabled": "meta-disabled" }',
                'status': 'disabled',
            },
        ),
        (
            'virtual-category-multi-dimensions',
            {
                'id': 'virtual-category-multi-dimensions',
                'alias': 'alias-multi-dimensions',
                'title_tanker_key': 'title_tanker_key-multi-dimensions',
                'subcategories': [],
                'images': [
                    {
                        'id': 'image-for-md-1',
                        'dimensions': [
                            {'width': 2, 'height': 2},
                            {'width': 4, 'height': 2},
                        ],
                    },
                    {
                        'id': 'image-for-md-2',
                        'dimensions': [{'width': 6, 'height': 2}],
                    },
                ],
                'meta': '{ "meta-multi-dimensions": "meta-multi-dimensions" }',
                'status': 'active',
            },
        ),
    ],
)
async def test_categories_set_status_put_200(
        taxi_grocery_products,
        pgsql,
        virtual_category_id,
        virtual_category_json,
        status,
):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories/set-status',
        params={'category_id': virtual_category_id},
        json={'status': status},
    )
    assert response.status_code == 200

    virtual_category_json['status'] = status
    ordered_object.assert_eq(
        response.json(), virtual_category_json, ['images'],
    )
    check_db_single_record(pgsql, {'status': status}, virtual_category_id)


@pytest.mark.pgsql(
    'grocery_products',
    files=['default.sql', '409error.sql', 'refresh_views.sql'],
)
async def test_categories_set_status_put_409(taxi_grocery_products, pgsql):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories/set-status',
        params={'category_id': 'category-11-1'},
        json={'status': 'disabled'},
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'CANNOT_DISABLE_CATEGORY'
    assert (
        response.json()['message']
        == 'Virtual category with id "category-11-1" can\'t be '
        'disabled, as it\'s attached to a layout with id "layout-1"'
    )


# Checks /admin/products/v3/categories/set-status PUT
# Return 404 when id not found in cache
async def test_categories_set_status_put_404(taxi_grocery_products):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/categories/set-status',
        params={'category_id': 'category-not-found-id'},
        json={'status': 'active'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'CATEGORY_NOT_FOUND'
    assert (
        response.json()['message']
        == 'Virtual category with id "category-not-found-id" not found'
    )


# Checks /admin/products/v3/categories/unattached/list POST
# get all unattached virtual categories
@pytest.mark.pgsql(
    'grocery_products', files=['409error.sql', 'refresh_views.sql'],
)
async def test_categories_unattached_list_post(
        taxi_grocery_products, load_json,
):
    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories/unattached/list', json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'categories_unattached_list_expected_response.json',
    )


# POST, PUT /admin/products/v3/categories
# Возвращает ошибку с кодом 400 при передаче метаданных в некорректном формате.
#  Под корректным форматом подразумевается JSON-объект.
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'method,params',
    [('POST', {}), ('PUT', {'category_id': 'virtual-category-1'})],
)
@pytest.mark.parametrize(
    'meta', ['{ bad-meta }', '', 'bad-meta', '"{ "bad-meta": "bad-meta" }"'],
)
async def test_categories_request_returns_400_if_bad_meta_format(
        taxi_grocery_products, pgsql, method, params, meta,
):
    response = await taxi_grocery_products.request(
        method,
        '/admin/products/v3/categories',
        params=params,
        json={
            'alias': 'alias-bad-meta',
            'title_tanker_key': 'title_tanker_key-bad-meta',
            'subcategories': [],
            'images': [],
            'meta': meta,
            'status': 'active',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'BAD_META_FORMAT'


# Checks /admin/products/v3/categories POST
# add category with optional field(in param) into database
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'test_field',
    [
        {'deep_link': None},
        {'deep_link': 'test_deep_link'},
        {'is_special_category': None},
        {'is_special_category': True},
        {'is_special_category': False},
        {'short_title_tanker_key': 'short_tanker_key-1'},
        {'special_category': 'promo-caas'},
    ],
)
async def test_categories_post_with_optional_field(
        taxi_grocery_products, pgsql, test_field,
):
    json = {
        'alias': 'alias-default',
        'title_tanker_key': 'tanker_key-default',
        'subcategories': [],
        'images': [],
        'meta': '{}',
        'status': 'active',
        **test_field,
    }
    response = await taxi_grocery_products.post(
        '/admin/products/v3/categories', json=json,
    )
    assert response.status_code == 200

    response_data = response.json()
    virtual_category_id = response_data['id']
    common.compare_request_and_response(
        virtual_category_id, json, response_data,
    )
    check_db_single_record(pgsql, test_field, virtual_category_id)


@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize('handler_type', ['post', 'put'])
async def test_categories_invalid_special_category(
        taxi_grocery_products, pgsql, handler_type,
):
    json = {
        'alias': 'alias-default',
        'title_tanker_key': 'tanker_key-default',
        'subcategories': [],
        'images': [],
        'meta': '{}',
        'status': 'active',
        'special_category': 'invalid-special-category',
    }
    response = None
    if handler_type == 'post':
        response = await taxi_grocery_products.post(
            '/admin/products/v3/categories', json=json,
        )
    elif handler_type == 'put':
        response = await taxi_grocery_products.put(
            '/admin/products/v3/categories',
            json=json,
            params={'category_id': 'virtual-category-with-special-category'},
        )
    assert response.status_code == 400
    assert response.json()['code'] == 'UNSUPPORTED_SPECIAL_CATEGORY'


@pytest.mark.config(
    GROCERY_PRODUCTS_AVAILABLE_SPECIAL_CATEGORIES=[
        'promo-caas',
        'promo-cashback',
    ],
)
async def test_available_special_categories(taxi_grocery_products):
    response = await taxi_grocery_products.get(
        '/admin/products/v1/special-categories/list',
    )
    assert response.status_code == 200
    assert response.json() == ['promo-caas', 'promo-cashback']
