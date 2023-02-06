import pytest

from testsuite.utils import ordered_object

# pylint: disable=too-many-lines

from tests_grocery_products import layout_utils


# Checks /admin/products/v3/layouts GET
# Return 404 when id not found in cache
async def test_layouts_get_404(taxi_grocery_products):
    response = await taxi_grocery_products.get(
        '/admin/products/v3/layouts',
        params={'layout_id': 'layout-not-found-id'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'LAYOUT_NOT_FOUND'
    assert (
        response.json()['message']
        == 'Layout with id "layout-not-found-id" not found'
    )


# Checks /admin/products/v3/layouts GET
# get layout with structure by layout_id
# we should recieve layout even with empy structure
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'layout-structureless.sql',
        'refresh_views.sql',
    ],
)
async def test_layouts_get_structureless_layout(taxi_grocery_products, pgsql):
    response = await taxi_grocery_products.get(
        '/admin/products/v3/layouts',
        params={'layout_id': 'layout-structureless'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'layout': {
            'alias': 'layout-alias-structureless',
            'id': 'layout-structureless',
            'meta': '{ "meta-structureless": "meta-structureless" }',
            'status': 'active',
        },
        'structure': {'groups': []},
    }


# Checks /admin/products/v3/layouts/list POST
# get all values from category layouts cache
@pytest.mark.pgsql(
    'grocery_products',
    files=['dimensions.sql', 'layouts.sql', 'refresh_views.sql'],
)
async def test_layouts_list_post(taxi_grocery_products, load_json):

    response = await taxi_grocery_products.post(
        '/admin/products/v3/layouts/list', json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json('layouts_list_expected_response.json')


# Checks /admin/products/v3/layouts GET
# get layout with structure by layout_id
@pytest.mark.parametrize(
    'layout_id,expected_response',
    [
        ('layout-1', 'layouts_structure_expected_response.json'),
        ('layout-2', 'layouts_structure_expected_response_2.json'),
    ],
)
@pytest.mark.pgsql(
    'grocery_products',
    files=['dimensions.sql', 'layouts.sql', 'refresh_views.sql'],
)
async def test_layouts_get_200(
        taxi_grocery_products, load_json, layout_id, expected_response,
):
    response = await taxi_grocery_products.get(
        '/admin/products/v3/layouts', params={'layout_id': layout_id},
    )
    assert response.status_code == 200
    expected = load_json(expected_response)
    ordered_object.assert_eq(
        response.json(),
        expected,
        ['structure.groups', 'structure.groups.categories'],
    )


# Checks /admin/products/v3/layouts POST
# return 409 on alias constraint conflict
@pytest.mark.pgsql(
    'grocery_products',
    files=['dimensions.sql', 'layouts.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'alias,code', [('layout-alias-2', 'LAYOUT_ALIAS_ALREADY_EXISTS')],
)
async def test_layouts_post_409(taxi_grocery_products, pgsql, alias, code):
    records_before = layout_utils.get_layouts_count(pgsql['grocery_products'])
    response = await taxi_grocery_products.post(
        '/admin/products/v3/layouts',
        json={
            'layout': {
                'alias': alias,
                'meta': '{ "meta": "meta" }',
                'status': 'active',
            },
            'structure': {'groups': []},
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == code
    layout_utils.check_layouts_count(pgsql['grocery_products'], records_before)


# Checks /admin/products/v3/layouts PUT
# return 404 when layout not found in cache
# return 409 when new alias is already in use
@pytest.mark.pgsql(
    'grocery_products',
    files=['dimensions.sql', 'layouts.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize(
    'layout_id,alias,status_code,code',
    [
        (
            'layout-not-found',
            'layout-not-found-alias',
            404,
            'LAYOUT_NOT_FOUND',
        ),
        ('layout-1', 'layout-alias-2', 409, 'LAYOUT_ALIAS_ALREADY_EXISTS'),
    ],
)
async def test_layouts_put_error(
        taxi_grocery_products, pgsql, layout_id, alias, status_code, code,
):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/layouts',
        params={'layout_id': layout_id},
        json={
            'layout': {'alias': alias, 'meta': '{}', 'status': 'active'},
            'structure': {'groups': []},
        },
    )
    assert response.status_code == status_code
    assert response.json()['code'] == code


# Checks /admin/products/v3/layouts/set-status PUT
# change status of existing layout
@pytest.mark.pgsql(
    'grocery_products',
    files=['dimensions.sql', 'layouts.sql', 'refresh_views.sql'],
)
@pytest.mark.parametrize('status', ['active', 'disabled'])
@pytest.mark.parametrize(
    'layout_id,layout_json',
    [
        (
            'layout-1',
            {
                'id': 'layout-1',
                'alias': 'layout-alias-1',
                'meta': '{ "meta-1": "meta-1" }',
                'status': 'active',
            },
        ),
        (
            'layout-disabled',
            {
                'id': 'layout-disabled',
                'alias': 'layout-alias-disabled',
                'meta': '{ "meta-disabled": "meta-disabled" }',
                'status': 'disabled',
            },
        ),
    ],
)
async def test_layouts_set_status_put_200(
        taxi_grocery_products, pgsql, layout_id, layout_json, status,
):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/layouts/set-status',
        params={'layout_id': layout_id},
        json={'status': status},
    )
    assert response.status_code == 200
    assert response.json()['status'] == status
    layout_utils.check_status(pgsql['grocery_products'], layout_id, status)


# Checks /admin/products/v3/layouts/set-status PUT
# Return 404 when id not found in cache
async def test_layouts_set_status_put_404(taxi_grocery_products):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/layouts/set-status',
        params={'layout_id': 'layout-not-found-id'},
        json={'status': 'active'},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'LAYOUT_NOT_FOUND'


# Checks /admin/products/v3/layouts POST
# insert new values in layouts, layout_category_groups
# and layout_virtual_categories tables
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
@pytest.mark.parametrize(
    'layout_id,layouts_request',
    [
        (
            'layout-1',
            {
                'layout': {
                    'alias': 'layout-new',
                    'meta': '{ "layout-new": "layout-new" }',
                    'status': 'active',
                },
                'structure': {
                    'groups': [
                        {
                            'group_id': 'group-1',
                            'image_id': 'group-1-image-1',
                            'meta': '{ "group-1-meta": "group-1-meta" }',
                            'order': 1,
                            'categories': [
                                {
                                    'category_id': 'category-11-1',
                                    'images': [
                                        {
                                            'id': 'category-11-1-image-1',
                                            'dimensions': [
                                                {'width': 5, 'height': 5},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "category-11-1-meta": '
                                        '"category-11-1-meta" }'
                                    ),
                                    'order': 1,
                                },
                                {
                                    'category_id': 'category-11-2',
                                    'images': [
                                        {
                                            'id': 'category-11-2-image-1',
                                            'dimensions': [
                                                {'width': 5, 'height': 5},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "new-category-meta-2": '
                                        '"new-category-meta-2" }'
                                    ),
                                    'order': 2,
                                },
                            ],
                        },
                        {
                            'group_id': 'group-12',
                            'image_id': 'group-12-image-1',
                            'meta': '{ "group-12-meta": "group-12-meta" }',
                            'order': 999,
                            'categories': [
                                {
                                    'category_id': 'category-112-1',
                                    'images': [
                                        {
                                            'id': 'category-112-1-image-1',
                                            'dimensions': [
                                                {'width': 9, 'height': 9},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "new-category-meta-1": '
                                        '"new-category-meta-1" }'
                                    ),
                                    'order': 123456,
                                },
                            ],
                        },
                    ],
                },
            },
        ),
        (
            'layout-disabled',
            {
                'layout': {
                    'alias': 'layout-alias-disabled-new',
                    'meta': '{ "meta-disabled-new": "meta-disabled-new" }',
                    'status': 'disabled',
                },
                'structure': {'groups': []},
            },
        ),
        (
            'layout-with-title',
            {
                'layout': {
                    'alias': 'layout-with-title-alias',
                    'meta': '{ "meta": "meta" }',
                    'status': 'active',
                    'title_tanker_key': 'layout-tanker-key',
                },
                'structure': {'groups': []},
            },
        ),
        (
            'layout-with-multi-dimensions',
            {
                'layout': {
                    'alias': 'layout-with-multi-dimensions',
                    'meta': '{ "meta": "meta" }',
                    'status': 'active',
                },
                'structure': {
                    'groups': [
                        {
                            'group_id': 'group-1',
                            'image_id': 'group-1-image-1',
                            'meta': '{ "group-1-meta": "group-1-meta" }',
                            'order': 1,
                            'categories': [
                                {
                                    'category_id': 'category-11-1',
                                    'images': [
                                        {
                                            'id': 'category-11-1-image-1',
                                            'dimensions': [
                                                {'width': 5, 'height': 5},
                                                {'width': 2, 'height': 2},
                                            ],
                                        },
                                        {
                                            'id': 'category-11-1-image-2',
                                            'dimensions': [
                                                {'width': 7, 'height': 7},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "category-11-1-meta": '
                                        '"category-11-1-meta" }'
                                    ),
                                    'order': 1,
                                },
                            ],
                        },
                    ],
                },
            },
        ),
    ],
)
async def test_layouts_post(
        taxi_grocery_products, pgsql, layout_id, layouts_request,
):
    db = pgsql['grocery_products']
    expected_recs_count = layout_utils.get_expected_recs_count(
        db, layouts_request['structure']['groups'],
    )
    response = await taxi_grocery_products.post(
        '/admin/products/v3/layouts', json=layouts_request,
    )
    assert response.status_code == 200
    layout_utils.check_layouts_response(
        db,
        response.json()['layout']['id'],
        layouts_request,
        response.json(),
        expected_recs_count,
        layout_version='v3',
    )


@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups_and_categories_for_layout.sql',
        'refresh_views.sql',
    ],
)
async def test_layouts_post_409_not_suitable_categories_or_groups(
        taxi_grocery_products, pgsql,
):
    response = await taxi_grocery_products.post(
        '/admin/products/v3/layouts',
        json={
            'layout': {
                'alias': 'layout-new',
                'meta': '{ "layout-new": "layout-new" }',
                'status': 'active',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'group-1-image-1',
                        'meta': '{ "group-1-meta": "group-1-meta" }',
                        'order': 1,
                        'categories': [
                            {
                                'category_id': 'category-11-1',
                                'images': [
                                    {
                                        'id': 'category-11-1-image-1',
                                        'dimensions': [
                                            {'width': 5, 'height': 5},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "category-11-1-meta": '
                                    '"category-11-1-meta" }'
                                ),
                                'order': 1,
                            },
                            {
                                'category_id': 'category-11-2',
                                'images': [
                                    {
                                        'id': 'category-11-2-image-1',
                                        'dimensions': [
                                            {'width': 5, 'height': 5},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "new-category-meta-2": '
                                    '"new-category-meta-2" }'
                                ),
                                'order': 2,
                            },
                        ],
                    },
                    {
                        'group_id': 'group-12',
                        'image_id': 'group-12-image-1',
                        'meta': '{ "group-12-meta": "group-12-meta" }',
                        'order': 999,
                        'categories': [
                            {
                                'category_id': 'category-112-1',
                                'images': [
                                    {
                                        'id': 'category-112-1-image-1',
                                        'dimensions': [
                                            {'width': 9, 'height': 9},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "new-category-meta-1": '
                                    '"new-category-meta-1" }'
                                ),
                                'order': 123456,
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'UNSUITABLE_GROUPS_OR_CATEGORIES'


@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups_and_categories_for_layout.sql',
        'refresh_views.sql',
    ],
)
async def test_layouts_put_409_not_suitable_categories_or_groups(
        taxi_grocery_products, pgsql,
):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/layouts',
        params={'layout_id': 'layout-1'},
        json={
            'layout': {
                'alias': 'layout-1',
                'meta': '{ "layout-1": "layout-1" }',
                'status': 'active',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'group-1-image-1',
                        'meta': '{ "group-1-meta": "group-1-meta" }',
                        'order': 1,
                        'categories': [
                            {
                                'category_id': 'category-11-1',
                                'images': [
                                    {
                                        'id': 'category-11-1-image-1',
                                        'dimensions': [
                                            {'width': 5, 'height': 5},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "category-11-1-meta": '
                                    '"category-11-1-meta" }'
                                ),
                                'order': 1,
                            },
                            {
                                'category_id': 'category-11-2',
                                'images': [
                                    {
                                        'id': 'category-11-2-image-1',
                                        'dimensions': [
                                            {'width': 5, 'height': 5},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "new-category-meta-2": '
                                    '"new-category-meta-2" }'
                                ),
                                'order': 2,
                            },
                        ],
                    },
                    {
                        'group_id': 'group-12',
                        'image_id': 'group-12-image-1',
                        'meta': '{ "group-12-meta": "group-12-meta" }',
                        'order': 999,
                        'categories': [
                            {
                                'category_id': 'category-112-1',
                                'images': [
                                    {
                                        'id': 'category-112-1-image-1',
                                        'dimensions': [
                                            {'width': 9, 'height': 9},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "new-category-meta-1": '
                                    '"new-category-meta-1" }'
                                ),
                                'order': 123456,
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'UNSUITABLE_GROUPS_OR_CATEGORIES'


# PUT /admin/products/v3/layouts
# Возвращает 409, если имеет место попытка
# создать плитку недопустимого размера.
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
async def test_put_returns_409_if_not_allowed_layout_dimensions(
        taxi_grocery_products,
):
    response = await taxi_grocery_products.put(
        '/admin/products/v3/layouts',
        params={'layout_id': 'layout-1'},
        json={
            'layout': {
                'alias': 'layou-1',
                'meta': '{ "meta-disabled-new": "meta-disabled-new" }',
                'status': 'disabled',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'group-1-image-1',
                        'meta': (
                            '{ "updated-group-meta": "updated-group-meta" }'
                        ),
                        'order': 1,
                        'categories': [
                            {
                                'category_id': 'category-11-1',
                                'images': [
                                    {
                                        'id': 'category-11-1-image-1',
                                        'dimensions': [
                                            {'width': 10, 'height': 10},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "updated-category-meta": '
                                    '"updated-category-meta" }'
                                ),
                                'order': 123,
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'NOT_ALLOWED_LAYOUT_ITEM_DIMENSIONS'


# Checks /admin/products/v3/layouts PUT
# update values in layouts, layout_category_groups
# and layout_virtual_categories tables
@pytest.mark.parametrize(
    'layout_id,layouts_request',
    [
        (
            'layout-1',
            {
                'layout': {
                    'alias': 'layout-1-updated',
                    'meta': '{ "layout-1-updated": "layout-1-updated" }',
                    'status': 'active',
                },
                'structure': {
                    'groups': [
                        {
                            'group_id': 'group-1',
                            'image_id': 'group-1-image-1',
                            'meta': (
                                '{ "updated-group-meta": '
                                '"updated-group-meta" }'
                            ),
                            'order': 1,
                            'categories': [
                                {
                                    'category_id': 'category-11-1',
                                    'images': [
                                        {
                                            'id': 'category-11-1-image-1',
                                            'dimensions': [
                                                {'width': 5, 'height': 5},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "updated-category-meta": '
                                        '"updated-category-meta" }'
                                    ),
                                    'order': 123,
                                },
                                {
                                    'category_id': 'category-11-2',
                                    'images': [
                                        {
                                            'id': 'category-11-2-image-1',
                                            'dimensions': [
                                                {'width': 5, 'height': 5},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "new-category-meta": '
                                        '"new-category-meta" }'
                                    ),
                                    'order': 456,
                                },
                            ],
                        },
                        {
                            'group_id': 'group-12',
                            'image_id': 'group-12-image-1',
                            'meta': '{ "meta-new": "meta-new" }',
                            'order': 999,
                            'categories': [
                                {
                                    'category_id': 'category-112-1',
                                    'images': [
                                        {
                                            'id': 'category-112-1-image-1',
                                            'dimensions': [
                                                {'width': 9, 'height': 9},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "meta-inner-category-new": '
                                        '"meta-inner-category-new" }'
                                    ),
                                    'order': 123456,
                                },
                            ],
                        },
                    ],
                },
            },
        ),
        (
            'layout-disabled',
            {
                'layout': {
                    'alias': 'layout-alias-disabled-updated',
                    'meta': (
                        '{ "meta-disabled-updated": "meta-disabled-updated" }'
                    ),
                    'status': 'disabled',
                },
                'structure': {'groups': []},
            },
        ),
        pytest.param(
            'layout-disabled',
            {
                'layout': {
                    'alias': 'layout-alias-disabled-updated',
                    'meta': (
                        '{ "meta-disabled-updated": "meta-disabled-updated" }'
                    ),
                    'status': 'disabled',
                    'title_tanker_key': 'layout-tanker-key',
                },
                'structure': {'groups': []},
            },
            id='update title_tanker_key',
        ),
        pytest.param(
            'layout-1',
            {
                'layout': {
                    'alias': 'layout-with-multi-dimensions',
                    'meta': '{ "meta": "meta" }',
                    'status': 'active',
                },
                'structure': {
                    'groups': [
                        {
                            'group_id': 'group-1',
                            'image_id': 'group-1-image-1',
                            'meta': '{ "group-1-meta": "group-1-meta" }',
                            'order': 1,
                            'categories': [
                                {
                                    'category_id': 'category-11-1',
                                    'images': [
                                        {
                                            'id': 'category-11-1-image-1',
                                            'dimensions': [
                                                {'width': 5, 'height': 5},
                                                {'width': 2, 'height': 2},
                                            ],
                                        },
                                        {
                                            'id': 'category-11-1-image-2',
                                            'dimensions': [
                                                {'width': 7, 'height': 7},
                                            ],
                                        },
                                    ],
                                    'meta': (
                                        '{ "category-11-1-meta": '
                                        '"category-11-1-meta" }'
                                    ),
                                    'order': 1,
                                },
                            ],
                        },
                    ],
                },
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
async def test_layouts_put(
        taxi_grocery_products, pgsql, layout_id, layouts_request,
):
    db = pgsql['grocery_products']
    expected_recs_count = layout_utils.get_expected_recs_count(
        db, layouts_request['structure']['groups'], layout_id,
    )
    response = await taxi_grocery_products.put(
        '/admin/products/v3/layouts',
        params={'layout_id': layout_id},
        json=layouts_request,
    )
    assert response.status_code == 200
    layout_utils.check_layouts_response(
        db,
        layout_id,
        layouts_request,
        response.json(),
        expected_recs_count,
        layout_version='v3',
    )


# PUT, POST /admin/products/v3/layouts
# Возвращают 409, если имеет место попытка
# прикрепить некорректную картинку к группе.
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
@pytest.mark.parametrize(
    'method,params', [('POST', {}), ('PUT', {'layout_id': 'layout-1'})],
)
async def test_layouts_request_returns_409_if_group_cannot_use_image(
        taxi_grocery_products, method, params,
):
    response = await taxi_grocery_products.request(
        method,
        '/admin/products/v3/layouts',
        params=params,
        json={
            'layout': {
                'alias': 'layout-1',
                'meta': '{ "meta-disabled-new": "meta-disabled-new" }',
                'status': 'disabled',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'image-101',
                        'meta': '{ "new-group-meta-1": "new-group-meta-1" }',
                        'order': 1,
                        'categories': [],
                    },
                ],
            },
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'GROUP_CANNOT_USE_THIS_IMAGE'


# POST, PUT /admin/products/v3/layouts
# Возвращают 409, если имеет место попытка
# прикрепить некорректную картинку для категории.
@pytest.mark.parametrize(
    'method,params', [('POST', {}), ('PUT', {'layout_id': 'layout-1'})],
)
@pytest.mark.parametrize(
    'image_id,image_dimensions',
    [
        pytest.param(
            'category-image-false',
            [{'width': 9, 'height': 9}],
            id='unknown image',
        ),
        pytest.param(
            'category-11-1-image-1',
            [{'width': 9, 'height': 9}],
            id='wrong dimensions',
        ),
    ],
)
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
async def test_layouts_request_returns_409_if_category_cannot_use_image(
        taxi_grocery_products, method, params, image_id, image_dimensions,
):
    response = await taxi_grocery_products.request(
        method,
        '/admin/products/v3/layouts',
        params=params,
        json={
            'layout': {
                'alias': 'layou-1',
                'meta': '{ "meta-disabled-new": "meta-disabled-new" }',
                'status': 'disabled',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'group-1-image-1',
                        'meta': '{ "new-group-meta-1": "new-group-meta-1" }',
                        'order': 1,
                        'categories': [
                            {
                                'category_id': 'category-11-1',
                                'images': [
                                    {
                                        'id': image_id,
                                        'dimensions': image_dimensions,
                                    },
                                ],
                                'meta': (
                                    '{ "category-11-1-meta": '
                                    '"category-11-1-meta" }'
                                ),
                                'order': 123456,
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'CATEGORY_CANNOT_USE_THIS_IMAGE'


# POST /admin/products/v3/layouts
# Возвращает 409, если имеет место попытка
# создать плитку недопустимого размера.
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
async def test_post_returns_409_if_not_allowed_layout_dimensions(
        taxi_grocery_products,
):
    response = await taxi_grocery_products.post(
        '/admin/products/v3/layouts',
        json={
            'layout': {
                'alias': 'layou-1',
                'meta': '{ "meta-disabled-new": "meta-disabled-new" }',
                'status': 'disabled',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'group-1-image-1',
                        'meta': '{ "new-group-meta-1": "new-group-meta-1" }',
                        'order': 1,
                        'categories': [
                            {
                                'category_id': 'category-11-1',
                                'images': [
                                    {
                                        'id': 'category-11-1-image-1',
                                        'dimensions': [
                                            {'width': 10, 'height': 10},
                                        ],
                                    },
                                ],
                                'meta': (
                                    '{ "category-11-1-meta": '
                                    '"category-11-1-meta" }'
                                ),
                                'order': 123456,
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'NOT_ALLOWED_LAYOUT_ITEM_DIMENSIONS'


# PUT, POST /admin/products/v3/layouts
# Запросы на создание и изменение сетки возвращают ошибку с кодом 400 при
#  передаче метаданных для самой сетки в некорректном формате. Под корректным
#  форматом подразумевается JSON-объект.
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
@pytest.mark.parametrize(
    'method,params', [('POST', {}), ('PUT', {'layout_id': 'layout-1'})],
)
@pytest.mark.parametrize(
    'meta', ['{ bad-meta }', '', 'bad-meta', '"{ "bad-meta": "bad-meta" }"'],
)
async def test_layouts_request_returns_400_if_layout_bad_meta_format(
        taxi_grocery_products, pgsql, method, params, meta,
):
    response = await taxi_grocery_products.request(
        method,
        '/admin/products/v3/layouts',
        params=params,
        json={
            'layout': {'alias': 'layou-1', 'meta': meta, 'status': 'disabled'},
            'structure': {'groups': []},
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'BAD_META_FORMAT'


# PUT, POST /admin/products/v3/layouts
# Запросы на создание и изменение сетки возвращают ошибку с кодом 400 при
#  передаче метаданных для категорий или групп в сетке в некорректном формате.
#  Под корректным форматом подразумевается JSON-объект.
@pytest.mark.pgsql(
    'grocery_products',
    files=[
        'dimensions.sql',
        'layouts.sql',
        'groups.sql',
        'categories.sql',
        'refresh_views.sql',
    ],
)
@pytest.mark.parametrize(
    'method,params', [('POST', {}), ('PUT', {'layout_id': 'layout-1'})],
)
@pytest.mark.parametrize(
    'group_meta,category_meta',
    [
        ('{ bad-meta }', '{}'),
        ('', '{}'),
        ('"{ "bad-meta": "bad-meta" }"', '{}'),
        ('{}', '{ bad-meta }'),
        ('{}', ''),
        ('{}', '"{ "bad-meta": "bad-meta" }"'),
    ],
)
async def test_layouts_request_returns_400_if_nested_bad_meta_format(
        taxi_grocery_products,
        pgsql,
        method,
        params,
        group_meta,
        category_meta,
):
    response = await taxi_grocery_products.request(
        method,
        '/admin/products/v3/layouts',
        params=params,
        json={
            'layout': {
                'alias': 'layou-1',
                'meta': '{ "bad-meta": "bad-meta" }',
                'status': 'disabled',
            },
            'structure': {
                'groups': [
                    {
                        'group_id': 'group-1',
                        'image_id': 'group-1-image-1',
                        'meta': group_meta,
                        'order': 1,
                        'categories': [
                            {
                                'category_id': 'category-11-1',
                                'images': [
                                    {
                                        'id': 'category-11-1-image-1',
                                        'dimensions': [
                                            {'width': 2, 'height': 2},
                                        ],
                                    },
                                ],
                                'meta': category_meta,
                                'order': 2,
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'BAD_META_FORMAT'
