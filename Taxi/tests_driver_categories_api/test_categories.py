import pytest


@pytest.mark.pgsql('driver-categories-api')
async def test_simple_operations(taxi_driver_categories_api, pgsql):
    await taxi_driver_categories_api.invalidate_caches()

    params = {'name': 'econom'}

    response = await taxi_driver_categories_api.get(
        'v1/categories', params=params,
    )
    assert response.status_code == 404

    # add
    params = {}

    response = await taxi_driver_categories_api.post(
        'v1/categories', json=params,
    )
    assert response.status_code == 500

    params = {'name': ''}

    response = await taxi_driver_categories_api.post(
        'v1/categories', json=params,
    )
    assert response.status_code == 400

    params = {
        'name': 'custom',
        'type': 'yandex',
        'jdoc': {'taximeter_value': 1, 'taximeter_sort_order': 1},
    }

    response = await taxi_driver_categories_api.post(
        'v1/categories', json=params,
    )
    assert response.status_code == 200

    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute('SELECT name,type,jdoc::jsonb from categories.categories')
    assert cursor.fetchall() == [
        (
            'custom',
            'yandex',
            {'taximeter_value': 1, 'taximeter_sort_order': 1},
        ),
    ]

    # update
    params = {'name': 'nosuchcategory'}

    data = {}

    response = await taxi_driver_categories_api.put(
        'v1/categories', params=params, json=data,
    )
    assert response.status_code == 404

    params = {'name': 'custom'}

    data = {
        'type': 'new',
        'jdoc': {'taximeter_value': 1, 'taximeter_sort_order': 1},
    }
    response = await taxi_driver_categories_api.put(
        'v1/categories', params=params, json=data,
    )
    assert response.status_code == 200

    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute('SELECT name,type,jdoc::jsonb from categories.categories')
    assert cursor.fetchall() == [
        ('custom', 'new', {'taximeter_value': 1, 'taximeter_sort_order': 1}),
    ]

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(
        'v1/categories', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'type': 'new',
        'name': 'custom',
        'jdoc': {
            'taximeter_name': 'custom',
            'taximeter_value': 1,
            'taximeter_sort_order': 1,
        },
    }


@pytest.mark.pgsql(
    'driver-categories-api',
    queries=[
        # categories
        'INSERT INTO categories.categories(name, type, updated_at,'
        ' jdoc) VALUES(\'business\', \'yandex\', now(),'
        ' \'{"taximeter_name": "bibi", "taximeter_value": 1,'
        ' "taximeter_sort_order": 1}\')',
        'INSERT INTO categories.categories(name, type, updated_at,'
        ' jdoc) VALUES(\'custom\', \'new\', now(),'
        ' \'{"taximeter_name": "cucu", "taximeter_value": 2,'
        ' "taximeter_sort_order": 2}\')',
    ],
)
async def test_bulkdelete(taxi_driver_categories_api, pgsql):
    await taxi_driver_categories_api.invalidate_caches()

    # get bulk
    response = await taxi_driver_categories_api.get('v1/categories')
    assert response.status_code == 200
    assert sorted(response.json(), key=lambda k: k['name']) == [
        {
            'jdoc': {
                'taximeter_name': 'bibi',
                'taximeter_value': 1,
                'taximeter_sort_order': 1,
            },
            'name': 'business',
            'type': 'yandex',
        },
        {
            'jdoc': {
                'taximeter_name': 'cucu',
                'taximeter_value': 2,
                'taximeter_sort_order': 2,
            },
            'name': 'custom',
            'type': 'new',
        },
    ]

    # delete
    params = {'name': 'custom'}
    response = await taxi_driver_categories_api.delete(
        'v1/categories', params=params,
    )
    assert response.status_code == 200

    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute('SELECT name,type,jdoc::jsonb from categories.categories')
    assert cursor.fetchall() == [
        (
            'business',
            'yandex',
            {
                'taximeter_name': 'bibi',
                'taximeter_value': 1,
                'taximeter_sort_order': 1,
            },
        ),
    ]

    # try to update deleted
    params = {'name': 'custom'}

    data = {
        'type': 'new',
        'jdoc': {
            'taximeter_name': 'cucucu',
            'taximeter_value': 3,
            'taximeter_sort_order': 3,
        },
    }
    response = await taxi_driver_categories_api.put(
        'v1/categories', params=params, json=data,
    )
    assert response.status_code == 404

    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute('SELECT name,type,jdoc::jsonb from categories.categories')
    assert cursor.fetchall() == [
        (
            'business',
            'yandex',
            {
                'taximeter_name': 'bibi',
                'taximeter_value': 1,
                'taximeter_sort_order': 1,
            },
        ),
    ]

    params = {
        'name': 'custom',
        'type': 'yandex',
        'jdoc': {
            'taximeter_name': 'cucu',
            'taximeter_value': 2,
            'taximeter_sort_order': 2,
        },
    }

    response = await taxi_driver_categories_api.post(
        'v1/categories', json=params,
    )
    assert response.status_code == 200
    cursor.execute('SELECT name,type,jdoc::jsonb from categories.categories')

    assert cursor.fetchall() == [
        (
            'business',
            'yandex',
            {
                'taximeter_name': 'bibi',
                'taximeter_value': 1,
                'taximeter_sort_order': 1,
            },
        ),
        (
            'custom',
            'yandex',
            {
                'taximeter_name': 'cucu',
                'taximeter_value': 2,
                'taximeter_sort_order': 2,
            },
        ),
    ]
