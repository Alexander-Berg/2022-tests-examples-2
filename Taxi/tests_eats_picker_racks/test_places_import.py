async def test_places_import_200(
        taxi_eats_picker_racks,
        init_postgresql,
        mockserver,
        load_json,
        get_place,
):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/search/places/list',
    )
    def _mock_catalog_storage(request):
        return mockserver.make_response(
            status=200, json=load_json('catalog_storage_response.json'),
        )

    response = await taxi_eats_picker_racks.post(
        '/api/v1/places/import', json={'place_ids': [1, 2, 3]},
    )
    assert response.status == 200
    assert response.json() == {'not_found_place_ids': [2, 3]}
    place = get_place(1)
    expected_place = load_json('expected_place.json')
    compare_db_with_expected_data(place, expected_place)


async def test_places_import_500(
        taxi_eats_picker_racks,
        init_postgresql,
        mockserver,
        load_json,
        get_place,
):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal'
        '/eats-catalog-storage/v1/search/places/list',
    )
    def _mock_catalog_storage(request):
        return mockserver.make_response(status=500)

    response = await taxi_eats_picker_racks.post(
        '/api/v1/places/import', json={'place_ids': [1, 2, 3]},
    )
    assert response.status == 500
    assert response.json() == {
        'errors': [{'code': 500, 'description': 'eats-catalog-storage error'}],
    }


def compare_db_with_expected_data(db_data, expected_data):
    for key, value in expected_data.items():
        assert db_data[key] == value
