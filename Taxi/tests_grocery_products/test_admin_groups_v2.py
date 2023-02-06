import pytest

from testsuite.utils import ordered_object

from tests_grocery_products import common


# Checks /admin/products/v2/groups POST
# insert new category group into category_group table
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
async def test_groups_post_200(
        taxi_grocery_products, pgsql, alias, tanker_key, meta, status,
):
    json = {
        'alias': alias,
        'title_tanker_key': tanker_key,
        'images': [],
        'meta': meta,
        'status': status,
    }

    response = await taxi_grocery_products.post(
        '/admin/products/v2/groups', json=json,
    )
    assert response.status_code == 200
    response_data = response.json()
    category_group_id = response_data['id']
    common.compare_request_and_response(category_group_id, json, response_data)

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT id, alias, title_tanker_key, meta, status
        FROM products.category_groups
        WHERE id = '{category_group_id}' AND alias = '{alias}';""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == category_group_id
    assert data[0][1] == alias
    assert data[0][2] == tanker_key
    assert data[0][3] == meta
    assert data[0][4] == status

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT id, alias, title_tanker_key, meta, status
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}' AND alias = '{alias}';""",
    )
    assert data == cursor.fetchall()


# Checks /admin/products/v2/groups POST
# insert new values into category_groups_images table
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'images,expected_images',
    [
        (
            [{'id': 'one/image', 'dimensions': {'width': 2, 'height': 2}}],
            '{"(one/image,\\"(2,2)\\")"}',
        ),
        (
            [
                {'id': 'two/images1', 'dimensions': {'width': 4, 'height': 2}},
                {'id': 'two/images2', 'dimensions': {'width': 6, 'height': 2}},
            ],
            '{"(two/images1,\\"(4,2)\\")","(two/images2,\\"(6,2)\\")"}',
        ),
    ],
)
async def test_groups_post_200_with_images(
        taxi_grocery_products, pgsql, images, expected_images,
):
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'test-tanker_key',
        'images': images,
        'meta': '{ "test-meta": "test-meta" }',
        'status': 'active',
    }

    response = await taxi_grocery_products.post(
        '/admin/products/v2/groups', json=json,
    )
    assert response.status_code == 200
    response_data = response.json()
    category_group_id = response_data['id']
    common.compare_request_and_response(category_group_id, json, response_data)

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT image_id, image_dimensions
        FROM products.category_groups_images
        WHERE category_group_id = '{category_group_id}'
        ORDER BY image_id;""",
    )
    data = cursor.fetchall()
    assert len(data) == len(images)
    for i, item in enumerate(data):
        assert item[0] == images[i]['id']
        common.compare_dimensions(item[1], images[i]['dimensions'])

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT images
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}';""",
    )
    ordered_object.assert_eq(expected_images, cursor.fetchall()[0][0], [''])


# Checks /admin/products/v2/groups POST
# insert new category group into category_group with short_title_tanker_key
@pytest.mark.pgsql('grocery_products', files=['refresh_views.sql'])
@pytest.mark.parametrize(
    'alias,tanker_key,short_tanker_key,meta,status',
    [
        (
            'test-alias-active',
            'tanker_key_active',
            'short_tanker_key_1',
            '{ "meta-active": "meta-active" }',
            'active',
        ),
        (
            'test-alias-disabled',
            'tanker_key_disabled',
            'short_tanker_key_1',
            '{ "meta-disabled": "meta-disabled" }',
            'disabled',
        ),
    ],
)
async def test_groups_post_200_with_short_tanker(
        taxi_grocery_products,
        pgsql,
        alias,
        tanker_key,
        short_tanker_key,
        meta,
        status,
):
    json = {
        'alias': alias,
        'title_tanker_key': tanker_key,
        'short_title_tanker_key': short_tanker_key,
        'images': [],
        'meta': meta,
        'status': status,
    }

    response = await taxi_grocery_products.post(
        '/admin/products/v2/groups', json=json,
    )
    assert response.status_code == 200
    response_data = response.json()
    category_group_id = response_data['id']
    common.compare_request_and_response(category_group_id, json, response_data)

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT short_title_tanker_key
        FROM products.category_groups
        WHERE id = '{category_group_id}' AND alias = '{alias}';""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == short_tanker_key

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT short_title_tanker_key
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}' AND alias = '{alias}';""",
    )
    assert data == cursor.fetchall()


# Checks /admin/products/v2/groups POST
# return 409 on alias constraint conflict
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'category_group_id,alias,code,message',
    [
        (
            'ok-id',
            'group-alias-2',
            'CATEGORY_GROUP_ALIAS_ALREADY_EXISTS',
            'Category group with alias "group-alias-2" already exists',
        ),
    ],
)
async def test_groups_post_409(
        taxi_grocery_products, pgsql, category_group_id, alias, code, message,
):
    await taxi_grocery_products.invalidate_caches()
    json = {
        'alias': alias,
        'title_tanker_key': 'tanker_key',
        'images': [],
        'meta': '{ "meta": "meta" }',
        'status': 'active',
    }

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.category_groups""",
    )
    records_before = cursor.fetchall()[0][0]

    response = await taxi_grocery_products.post(
        '/admin/products/v2/groups', json=json,
    )

    assert response.status_code == 409
    assert response.json()['code'] == code
    assert response.json()['message'] == message

    cursor = db.cursor()
    cursor.execute(
        f"""SELECT COUNT(*)
        FROM products.category_groups""",
    )
    assert records_before == cursor.fetchall()[0][0]


# Checks /admin/products/v2/groups PUT
# update existing values in category_groups table
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'category_group_id,alias,tanker_key,meta,status',
    [
        (
            'category-group-1',
            'new-category-group-1-alias',
            'new-category-group-1-tanker-key',
            '{ "new-category-group-1-meta": "new-category-group-1-meta" }',
            'active',
        ),
        (
            'category-group-disabled',
            'new-category-group-disabled-alias',
            'new-category-group-disabled-tanker-key',
            '{ "new-category-group-disabled-meta": '
            '"new-category-group-disabled-meta" }',
            'disabled',
        ),
    ],
)
async def test_groups_put_ok(
        taxi_grocery_products,
        pgsql,
        category_group_id,
        alias,
        tanker_key,
        meta,
        status,
):
    await taxi_grocery_products.invalidate_caches()
    json = {
        'alias': alias,
        'title_tanker_key': tanker_key,
        'images': [],
        'meta': meta,
        'status': status,
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups',
        params={'category_group_id': category_group_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        category_group_id, json, response.json(),
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT id, alias, title_tanker_key, meta, status
        FROM products.category_groups
        WHERE id = '{category_group_id}';""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][1] == alias
    assert data[0][2] == tanker_key
    assert data[0][3] == meta
    assert data[0][4] == status

    # Check that materialized view refreshed after update
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT id, alias, title_tanker_key, meta, status
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}';""",
    )
    assert data == cursor.fetchall()


# Checks /admin/products/v2/groups PUT
# update values in category_groups_images table
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'images,expected_images',
    [
        (
            [{'id': 'one/image', 'dimensions': {'width': 2, 'height': 2}}],
            '{"(one/image,\\"(2,2)\\")"}',
        ),
        (
            [
                {'id': 'two/images1', 'dimensions': {'width': 4, 'height': 2}},
                {'id': 'two/images2', 'dimensions': {'width': 6, 'height': 2}},
            ],
            '{"(two/images1,\\"(4,2)\\")","(two/images2,\\"(6,2)\\")"}',
        ),
        (
            [
                {
                    'id': 'image-group-11',
                    'dimensions': {'width': 4, 'height': 2},
                },
            ],
            '{"(image-group-11,\\"(4,2)\\")"}',
        ),
    ],
)
async def test_groups_put_ok_with_images(
        taxi_grocery_products, pgsql, images, expected_images,
):
    category_group_id = 'category-group-1'
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'test-tanker_key',
        'images': images,
        'meta': '{ "test-meta": "test-meta" }',
        'status': 'active',
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups',
        params={'category_group_id': category_group_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        category_group_id, json, response.json(),
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT image_id, image_dimensions
        FROM products.category_groups_images
        WHERE category_group_id = '{category_group_id}'
        ORDER BY image_id;""",
    )
    data = cursor.fetchall()
    assert len(data) == len(images)
    for i, item in enumerate(data):
        assert item[0] == images[i]['id']
        common.compare_dimensions(item[1], images[i]['dimensions'])

    # Check that materialized view refreshed after insertion
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT images
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}';""",
    )
    ordered_object.assert_eq(expected_images, cursor.fetchall()[0][0], [''])


# Checks /admin/products/v2/groups PUT
# update short_title_tanker_key in category_groups table
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'category_group_id,short_tanker_key',
    [
        ('category-group-1', 'short-tanker-key-1'),
        ('category-group-disabled', 'short-tanker-key-2'),
    ],
)
async def test_groups_put_ok_with_short_tanker(
        taxi_grocery_products, pgsql, category_group_id, short_tanker_key,
):
    await taxi_grocery_products.invalidate_caches()
    json = {
        'alias': 'test-alias',
        'title_tanker_key': 'test-tanker_key',
        'short_title_tanker_key': short_tanker_key,
        'images': [],
        'meta': '{ "test-meta": "test-meta" }',
        'status': 'active',
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups',
        params={'category_group_id': category_group_id},
        json=json,
    )
    assert response.status_code == 200
    common.compare_request_and_response(
        category_group_id, json, response.json(),
    )

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT short_title_tanker_key
        FROM products.category_groups
        WHERE id = '{category_group_id}';""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == short_tanker_key

    # Check that materialized view refreshed after update
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT short_title_tanker_key
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}';""",
    )
    assert data == cursor.fetchall()


# Checks /admin/products/v2/groups PUT
# return 404 when category group not found in cache
# return 409 when new alias is already in use
@pytest.mark.pgsql(
    'grocery_products',
    files=['default.sql', '409error.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'category_group_id,alias,status_code,code,message,status',
    [
        (
            'category-group-not-found',
            'category-group-not-found-alias',
            404,
            'CATEGORY_GROUP_NOT_FOUND',
            'Category group with id "category-group-not-found" not found',
            'active',
        ),
        (
            'category-group-1',
            'group-alias-2',
            409,
            'CATEGORY_GROUP_ALIAS_ALREADY_EXISTS',
            'Category group with alias "group-alias-2" already exists',
            'active',
        ),
        (
            'group-1',
            'alias-group-1',
            409,
            'CANNOT_DISABLE_CATEGORY_GROUP',
            'Category group with id "group-1" cannot be '
            'disabled, as it\'s attached to a layout with id "layout-1"',
            'disabled',
        ),
        (
            'group-2',
            'alias-group-2',
            409,
            'CANNOT_UNBIND_IMAGE',
            'Image with id "image-group-2" can\'t be '
            'Unbound, as it\'s attached to a layout with id "layout-2"',
            'active',
        ),
    ],
)
async def test_groups_put_error(
        taxi_grocery_products,
        pgsql,
        category_group_id,
        alias,
        status_code,
        code,
        message,
        status,
):
    await taxi_grocery_products.invalidate_caches()
    json = {
        'id': category_group_id,
        'alias': alias,
        'title_tanker_key': '',
        'images': [],
        'meta': '{}',
        'status': status,
    }

    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups',
        params={'category_group_id': category_group_id},
        json=json,
    )
    assert response.status_code == status_code
    assert response.json()['code'] == code
    assert response.json()['message'] == message


# Checks /admin/products/v2/groups GET
# Return category group info by id
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'category_group_id,category_group_json',
    [
        pytest.param(
            'category-group-1',
            {
                'id': 'category-group-1',
                'alias': 'group-alias-1',
                'title_tanker_key': 'title_tanker_key-1',
                'images': [
                    {
                        'id': 'image-group-11',
                        'dimensions': {'width': 2, 'height': 2},
                    },
                    {
                        'id': 'image-group-12',
                        'dimensions': {'width': 2, 'height': 6},
                    },
                    {
                        'id': 'image-group-13',
                        'dimensions': {'width': 2, 'height': 4},
                    },
                ],
                'meta': '{ "meta-1": "meta-1" }',
                'status': 'active',
            },
            id='active category group',
        ),
        pytest.param(
            'category-group-disabled',
            {
                'id': 'category-group-disabled',
                'alias': 'group-alias-disabled',
                'title_tanker_key': 'title_tanker_key-disabled',
                'images': [
                    {
                        'id': 'image-group-disabled-1',
                        'dimensions': {'width': 1, 'height': 3},
                    },
                    {
                        'id': 'image-group-disabled-2',
                        'dimensions': {'width': 1, 'height': 4},
                    },
                ],
                'meta': '{ "meta-disabled": "meta-disabled" }',
                'status': 'disabled',
            },
            id='disabled category group',
        ),
        pytest.param(
            'category-group-short-tanker',
            {
                'id': 'category-group-short-tanker',
                'alias': 'group-alias-4',
                'title_tanker_key': 'title_tanker_key-4',
                'short_title_tanker_key': 'short_title_tanker_key-4',
                'images': [],
                'meta': '{ "meta-4": "meta-4" }',
                'status': 'active',
            },
            id='category group with short tanker',
        ),
    ],
)
async def test_groups_get_200(
        taxi_grocery_products, category_group_id, category_group_json,
):
    await taxi_grocery_products.invalidate_caches()

    response = await taxi_grocery_products.get(
        '/admin/products/v2/groups',
        params={'category_group_id': category_group_id},
    )
    assert response.status_code == 200
    assert response.json() == category_group_json


# Checks /admin/products/v2/groups GET
# Return 404 when id not found in cache
async def test_groups_get_404(taxi_grocery_products):
    response = await taxi_grocery_products.get(
        '/admin/products/v2/groups',
        params={'category_group_id': 'category-group-not-found-id'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'CATEGORY_GROUP_NOT_FOUND'
    assert (
        response.json()['message']
        == 'Category group with id "category-group-not-found-id" not found'
    )


# Checks /admin/products/v2/groups/list POST
# get all values from category groups cache
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
async def test_groups_list_post(taxi_grocery_products, load_json):

    response = await taxi_grocery_products.post(
        '/admin/products/v2/groups/list', json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json('groups_list_expected_response.json')


# Checks /admin/products/v2/groups/set-status PUT
# change status of existing category group
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize('status', ['active', 'disabled'])
@pytest.mark.parametrize(
    'category_group_id,category_group_json',
    [
        (
            'category-group-1',
            {
                'id': 'category-group-1',
                'alias': 'group-alias-1',
                'title_tanker_key': 'title_tanker_key-1',
                'images': [
                    {
                        'id': 'image-group-11',
                        'dimensions': {'width': 2, 'height': 2},
                    },
                    {
                        'id': 'image-group-12',
                        'dimensions': {'width': 2, 'height': 6},
                    },
                    {
                        'id': 'image-group-13',
                        'dimensions': {'width': 2, 'height': 4},
                    },
                ],
                'meta': '{ "meta-1": "meta-1" }',
                'status': 'active',
            },
        ),
        (
            'category-group-disabled',
            {
                'id': 'category-group-disabled',
                'alias': 'group-alias-disabled',
                'title_tanker_key': 'title_tanker_key-disabled',
                'images': [
                    {
                        'id': 'image-group-disabled-1',
                        'dimensions': {'width': 1, 'height': 3},
                    },
                    {
                        'id': 'image-group-disabled-2',
                        'dimensions': {'width': 1, 'height': 4},
                    },
                ],
                'meta': '{ "meta-disabled": "meta-disabled" }',
                'status': 'disabled',
            },
        ),
    ],
)
async def test_groups_set_status_put_200(
        taxi_grocery_products,
        pgsql,
        category_group_id,
        category_group_json,
        status,
):
    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups/set-status',
        params={'category_group_id': category_group_id},
        json={'status': status},
    )
    assert response.status_code == 200

    category_group_json['status'] = status
    assert response.json() == category_group_json

    db = pgsql['grocery_products']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT status
        FROM products.category_groups
        WHERE id = '{category_group_id}';""",
    )
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == status

    # Check that materialized view refreshed after status update
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT status
        FROM products.{common.CATEGORY_GROUPS_VIEW_NAME}
        WHERE id = '{category_group_id}';""",
    )
    assert data == cursor.fetchall()


@pytest.mark.pgsql(
    'grocery_products',
    files=['default.sql', '409error.sql', 'refresh_views.sql'],
)
async def test_groups_set_status_put_409(taxi_grocery_products, pgsql):
    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups/set-status',
        params={'category_group_id': 'group-1'},
        json={'status': 'disabled'},
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'CANNOT_DISABLE_CATEGORY_GROUP'
    assert (
        response.json()['message']
        == 'Category group with id "group-1" cannot be '
        'disabled, as it\'s attached to a layout with id "layout-1"'
    )


# Checks /admin/products/v2/groups/set-status PUT
# Return 404 when id not found in cache
async def test_groups_set_status_put_404(taxi_grocery_products):
    response = await taxi_grocery_products.put(
        '/admin/products/v2/groups/set-status',
        params={'category_group_id': 'category-group-not-found-id'},
        json={'status': 'active'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'CATEGORY_GROUP_NOT_FOUND'
    assert (
        response.json()['message']
        == 'Category group with id "category-group-not-found-id" not found'
    )


# Checks /admin/products/v2/groups/unattached/list POST
# get all unattached category groups
@pytest.mark.pgsql(
    'grocery_products', files=['409error.sql', 'refresh_views.sql'],
)
async def test_groups_unattached_list_post(taxi_grocery_products, load_json):

    response = await taxi_grocery_products.post(
        '/admin/products/v2/groups/unattached/list', json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'groups_unattached_list_expected_response.json',
    )


# POST, PUT /admin/products/v2/groups
# Возвращает ошибку с кодом 400 при передаче метаданных в некорректном формате.
#  Под корректным форматом подразумевается JSON-объект.
@pytest.mark.pgsql(
    'grocery_products', files=['default.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'method,params',
    [('POST', {}), ('PUT', {'category_group_id': 'category-group-1'})],
)
@pytest.mark.parametrize(
    'meta', ['{ bad-meta }', '', 'bad-meta', '"{ "bad-meta": "bad-meta" }"'],
)
async def test_groups_request_returns_400_if_bad_meta_format(
        taxi_grocery_products, pgsql, method, params, meta,
):
    response = await taxi_grocery_products.request(
        method,
        '/admin/products/v2/groups',
        params=params,
        json={
            'alias': 'alias-bad-meta',
            'title_tanker_key': 'title_tanker_key-bad-meta',
            'images': [],
            'meta': meta,
            'status': 'active',
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'BAD_META_FORMAT'
