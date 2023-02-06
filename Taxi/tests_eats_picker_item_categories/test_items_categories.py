import pytest


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_'
    'picker_categories_priority.json',
)
async def test_items_categories_item_in_local_db(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
        check_category,
):
    # Given: one item in the local database with category
    place_id = 2
    eats_item_id = 'item_id1'
    item_id1 = create_item(place_id, eats_item_id)

    category_public_id = 'public_id'
    category_name = 'name'
    category_id = create_category(category_public_id, category_name)

    create_item_category(item_id1, category_id, 0)

    # When: someone ask us about categories for the item
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code is 200
    assert response.status_code == 200
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    item_category = items_categories[0]
    assert item_category['item_id'] == eats_item_id
    assert len(item_category['categories']) == 1
    check_category(
        item_category['categories'][0],
        category_public_id,
        category_name,
        0,
        0.625,
    )


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_items_categories_item_in_local_db_two_categories(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
):
    place_id = 2
    eats_item_id = 'item_id_0'
    item_id_0 = create_item(place_id, eats_item_id)

    category_public_id_0 = 'public_id_0'
    category_name_0 = 'name_0'
    category_id_0 = create_category(
        category_public_id_0, category_name_0, None,
    )
    create_item_category(item_id_0, category_id_0, 0)

    category_public_id_1 = 'public_id_1'
    category_name_1 = 'name_1'
    category_id_1 = create_category(
        category_public_id_1, category_name_1, category_public_id_0,
    )
    create_item_category(item_id_0, category_id_1, 1)

    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    assert response.status_code == 200
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    item_category = items_categories[0]
    assert item_category == {
        'item_id': eats_item_id,
        'categories': [
            {
                'category_id': category_public_id_0,
                'category_name': category_name_0,
                'category_level': 0,
                'hierarchy_number': 0,
            },
            {
                'category_id': category_public_id_1,
                'category_name': category_name_1,
                'category_level': 1,
                'hierarchy_number': 0,
            },
        ],
    }


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_items_categories_item_in_local_db_two_hierarchies(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
):
    place_id = 2
    eats_item_id = 'item_id_0'
    item_id_0 = create_item(place_id, eats_item_id)

    category_id_0 = create_category('0', '0', None)
    create_item_category(item_id_0, category_id_0, 0, 0)

    category_id_1 = create_category('1', '1', '0')
    create_item_category(item_id_0, category_id_1, 1, 0)

    category_id_2 = create_category('2', '2', None)
    create_item_category(item_id_0, category_id_2, 0, 1)

    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    assert response.status_code == 200
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    item_category = items_categories[0]
    assert item_category == {
        'item_id': eats_item_id,
        'categories': [
            {
                'category_id': '0',
                'category_name': '0',
                'category_level': 0,
                'hierarchy_number': 0,
            },
            {
                'category_id': '1',
                'category_name': '1',
                'category_level': 1,
                'hierarchy_number': 0,
            },
        ],
    }


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_items_categories_item_in_nomenclature_db(
        taxi_eats_picker_item_categories, mockserver,
):
    # Given: one item in the eats_nomenclature database(eats_item_id)
    place_id = 2
    eats_item_id = 'item_id'

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'
    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    # When: our service call /eats-nomenclature/v1/product/categories
    # Then: method should be POST
    # And: query parameter place_id should be equal to the value of place_id
    # And: query parameter include_custom_categories should be false
    # And: json body should contain only one product with origin_id
    # equal to the value of eats_item_id
    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id}]
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    # When: someone ask us about categories for the items
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code should be 200
    # And: we made only one call to nomenclature
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    assert items_categories == [
        {
            'categories': [
                {
                    'category_id': highlevel_category_id,
                    'category_name': highlevel_category_name,
                    'category_level': 0,
                    'hierarchy_number': 0,
                },
                {
                    'category_id': lowest_category_id,
                    'category_name': lowest_category_name,
                    'category_level': 1,
                    'hierarchy_number': 0,
                },
            ],
            'item_id': eats_item_id,
        },
    ]


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_item_categories_no_items_in_both_dbs(
        taxi_eats_picker_item_categories, mockserver,
):
    # Given: no items in local database and no item in nomenclature
    place_id = 2
    eats_item_id = 'item_id'

    # When: our service call /eats-nomenclature/v1/product/categories
    # Then: method should be POST
    # And: query parameter place_id should be equal to the value of place_id
    # And: query parameter include_custom_categories should be false
    # And: json body should contain one product with origin_id
    # equal to the value of eats_item_id
    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        expected_product = {'origin_id': eats_item_id}
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert len(request.json['products']) == 1
        assert request.json['products'][0] == expected_product
        return mockserver.make_response(status=404)

    # When: someone ask us about categories for the items
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code should be 200
    # And: we made only one call to nomenclature
    # And: items_categories should be empty
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert not items_categories


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_item_categories_outdated_item(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
        mockserver,
):
    # Given: one item in the local database with outdated category
    place_id = 2
    eats_item_id = 'item_id1'
    item_id1 = create_item(
        place_id, eats_item_id, '1976-01-19T15:00:27.010000+03:00',
    )

    category_public_id = 'public_id'
    category_name = 'name'
    category_id = create_category(category_public_id, category_name)

    create_item_category(item_id1, category_id, 0)

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id}]
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': 'lowest_id',
                        'name': 'Lowlevel Category',
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    # When: someone ask us about categories for the items
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code should be 200
    # And: we made only one call to nomenclature
    # And: items_categories should not be empty
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    assert len(response.json()['items_categories']) == 1


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_'
    'picker_categories_priority.json',
)
async def test_items_categories_combined_test(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
        mockserver,
        check_category,
):
    # Given: one item in the local database
    # with actual highlevel category(eats_item_id1)
    # And: one item in the eats_nomenclature database(eats_item_id2)
    # And: one item doesn't exist in either local db or outer db(eats_item_id3)
    place_id = 2
    eats_item_id1 = 'item_id1'
    eats_item_id2 = 'item_id2'
    eats_item_id3 = 'item_id3'
    item_id1 = create_item(place_id, eats_item_id1)

    category_id = create_category('public_id', 'name')

    create_item_category(item_id1, category_id, 0)

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'
    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    # When: our service call /eats-nomenclature/v1/product/categories
    # Then: method should be POST
    # And: query parameter place_id should be equal to the value of place_id
    # And: query parameter include_custom_categories should be false
    # And: json body should contain two products
    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert len(request.json['products']) == 2
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id2,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    # When: someone ask us about highlevel categories for the items
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={
            'place_id': place_id,
            'items': [eats_item_id1, eats_item_id2, eats_item_id3],
        },
    )

    # Then: response code should be 200
    # And: we made only one call to nomenclature
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 2
    assert items_categories == [
        {
            'categories': [
                {
                    'category_id': 'public_id',
                    'category_name': 'name',
                    'category_level': 0,
                    'category_priority': 0.625,
                    'hierarchy_number': 0,
                },
            ],
            'item_id': eats_item_id1,
        },
        {
            'categories': [
                {
                    'category_id': highlevel_category_id,
                    'category_name': highlevel_category_name,
                    'category_level': 0,
                    'category_priority': 1.5,
                    'hierarchy_number': 0,
                },
                {
                    'category_id': lowest_category_id,
                    'category_name': lowest_category_name,
                    'category_level': 1,
                    'hierarchy_number': 0,
                },
            ],
            'item_id': eats_item_id2,
        },
    ]


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_items_categories_only_one_call_to_nomenclature(
        taxi_eats_picker_item_categories,
        create_item,
        create_category,
        create_item_category,
        mockserver,
):
    # Given: one outdated item in the local database
    # with two categories
    place_id = 2
    eats_item_id = 'item_id1'
    item_id1 = create_item(
        place_id, eats_item_id, '1976-01-19T15:00:27.010000+03:00',
    )

    category_public_id1 = 'public_id1'
    category_name1 = 'category1'
    category_id1 = create_category(category_public_id1, category_name1)

    category_public_id2 = 'public_id2'
    category_name2 = 'category2'
    category_id2 = create_category(category_public_id2, category_name2)

    create_item_category(item_id1, category_id1, 0)
    create_item_category(item_id1, category_id2, 1)

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'
    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    # When: our service call /eats-nomenclature/v1/product/categories
    # Then: method should be POST
    # And: query parameter place_id should be equal to the value of place_id
    # And: query parameter include_custom_categories should be false
    # And: json body should contain one product
    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert len(request.json['products']) == 1
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    # When: someone ask us about highlevel category for the item
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code is 200
    # And: we made only one call to nomenclature
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    assert items_categories == [
        {
            'categories': [
                {
                    'category_id': highlevel_category_id,
                    'category_name': highlevel_category_name,
                    'category_level': 0,
                    'hierarchy_number': 0,
                },
                {
                    'category_id': lowest_category_id,
                    'category_name': lowest_category_name,
                    'category_level': 1,
                    'hierarchy_number': 0,
                },
            ],
            'item_id': eats_item_id,
        },
    ]

    # When: someone ask us again about highlevel category for the same item
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code is 200
    # And: we didn't do any new calls to nomenclature
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    assert items_categories == [
        {
            'categories': [
                {
                    'category_id': highlevel_category_id,
                    'category_name': highlevel_category_name,
                    'category_level': 0,
                    'hierarchy_number': 0,
                },
                {
                    'category_id': lowest_category_id,
                    'category_name': lowest_category_name,
                    'category_level': 1,
                    'hierarchy_number': 0,
                },
            ],
            'item_id': eats_item_id,
        },
    ]


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_items_categories_nomenclature_timeout(
        taxi_eats_picker_item_categories, mockserver,
):
    eats_item_id = 'item_id1'
    place_id = 5

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert len(request.json['products']) == 1
        return mockserver.make_response(
            json={'code': '500', 'message': 'message'}, status=500,
        )

    # When: someone ask us about highlevel category for the item
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert not items_categories


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_duplicated_items_from_nomenclature(
        taxi_eats_picker_item_categories, mockserver,
):
    place_id = 2
    eats_item_id = 'item_id'

    highlevel_category_id = 'highest_id'
    highlevel_category_name = 'Highlevel Category'
    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    # When: our service call /eats-nomenclature/v1/product/categories
    # Then: method should be POST
    # And: query parameter place_id should be equal to the value of place_id
    # And: query parameter include_custom_categories should be false
    # And: json body should contain only one product with origin_id
    # equal to the value of eats_item_id
    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id}]
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                        'public_parent_id': highlevel_category_id,
                    },
                    {
                        'public_id': highlevel_category_id,
                        'name': highlevel_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['lowest_id'],
                    },
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['lowest_id'],
                    },
                ],
            },
            status=200,
        )

    # When: someone ask us about categories for the items
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code should be 200
    # And: we made only one call to nomenclature
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    item_category = items_categories[0]
    assert item_category['item_id'] == eats_item_id


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_duplicated_categories_from_nomenclature(
        taxi_eats_picker_item_categories, mockserver, get_item_categories,
):
    place_id = 2
    eats_item_id = 'item_id'

    lowest_category_id = 'lowest_id'
    lowest_category_name = 'Lowlevel Category'

    # When: our service call /eats-nomenclature/v1/product/categories
    # Then: method should be POST
    # And: query parameter place_id should be equal to the value of place_id
    # And: query parameter include_custom_categories should be false
    # And: json body should contain only one product with origin_id
    # equal to the value of eats_item_id
    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        assert request.json['products'] == [{'origin_id': eats_item_id}]
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': lowest_category_id,
                        'name': lowest_category_name,
                    },
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['lowest_id', 'lowest_id'],
                    },
                ],
            },
            status=200,
        )

    # When: someone ask us about categories for the items
    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    # Then: response code should be 200
    # And: we made only one call to nomenclature
    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1
    items_categories = response.json()['items_categories']
    assert len(items_categories) == 1
    item_category = items_categories[0]
    assert item_category['item_id'] == eats_item_id
    db_state = get_item_categories(eats_item_id)
    assert len(db_state) == 1
    db_record = db_state[0]
    assert db_record[0] == eats_item_id
    assert db_record[1] == lowest_category_id
    assert db_record[2] == lowest_category_name
    assert db_record[3] is None  # no parent
    assert db_record[4] == 0  # hierarchy_number
    assert db_record[5] == 0  # level


@pytest.mark.experiments3(
    filename='config3_eats_picker_item_categories_item_refresh_delay.json',
)
async def test_two_hierarchies_with_the_same_root(
        taxi_eats_picker_item_categories, mockserver, get_item_categories,
):
    place_id = 2
    eats_item_id = '1000017642'

    @mockserver.json_handler(f'/eats-nomenclature/v1/product/categories')
    def _mock_eats_nomenclature(request):
        assert request.method == 'POST'
        assert int(request.query['place_id']) == place_id
        assert request.query['include_custom_categories'] == 'false'
        return mockserver.make_response(
            json={
                'categories': [
                    {
                        'public_id': '25336',
                        'name': 'Домик в деревне',
                        'public_parent_id': '19280',
                    },
                    {
                        'public_id': '19351',
                        'name': 'Сметана',
                        'public_parent_id': '19280',
                    },
                    {'public_id': '19280', 'name': 'Молоко и яйца'},
                ],
                'products': [
                    {
                        'origin_id': eats_item_id,
                        'category_public_ids': ['25336', '19351'],
                    },
                ],
            },
            status=200,
        )

    response = await taxi_eats_picker_item_categories.post(
        '/api/v1/items/categories',
        json={'place_id': place_id, 'items': [eats_item_id]},
    )

    assert response.status_code == 200
    assert _mock_eats_nomenclature.times_called == 1

    db_state = get_item_categories(eats_item_id)
    assert len(db_state) == 4
