import operator


async def test_drivers_lookup(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={
            'park_id': 'park1',
            'text': 'bond007 +79998887766 LICENSE1 driver1 а001мр77',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [{'driver_id': 'driver1', 'rank': 1040}],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_by_too_short_word(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup', json={'park_id': 'park1', 'text': '+a'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_by_incomplete_words(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park1', 'text': 'ond007 +79998887 LICENSE а001мр'},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json['driver_profile_items'].sort(
        key=operator.itemgetter('driver_id'),
    )
    assert response_json == {
        'driver_profile_items': [
            {'driver_id': 'driver1', 'rank': 14},
            {'driver_id': 'driver11', 'rank': 14},
        ],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_need_only_exact_match(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park1', 'text': 'river1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_need_only_one_suffix(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park2', 'text': 'Геннади'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [{'driver_id': 'driver2', 'rank': 1}],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_need_only_one_suffix_empty(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park2', 'text': 'еннадий'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_few_matches(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park1', 'text': 'bond007'},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json['driver_profile_items'].sort(
        key=operator.itemgetter('driver_id'),
    )
    assert response_json == {
        'driver_profile_items': [
            {'driver_id': 'driver1', 'rank': 10},
            {'driver_id': 'driver11', 'rank': 10},
        ],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_no_matches(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park1', 'text': 'text_without_any_matches'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_duplicate_word(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park1', 'text': '+79998887766 +79998887766'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [{'driver_id': 'driver1', 'rank': 10}],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_few_words_for_one_type(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={
            'park_id': 'park1',
            'text': '+79998887766 +7999888776 +799988877',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_word_from_different_caches(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park2', 'text': 'LICENSE2 non_existing_word'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_one_word_for_few_types(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup', json={'park_id': 'park2', 'text': 'YYY'},
    )
    assert response.status_code == 200
    assert response.json() == {
        # 7 for lastname, 4 for firstname, 5 for middlename
        # see rank points in driver_profile_text_filter.hpp
        'driver_profile_items': [{'driver_id': 'driver1', 'rank': 7 + 4 + 5}],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_empty_text(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup', json={'park_id': 'park1', 'text': ''},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'empty',
    }


async def test_drivers_lookup_bad_car_id(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={
            'park_id': 'park2',
            'text': 'bond007 +79998887766 LICENSE1 driver1 а001мр77',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [],
        'filter_status': 'filled',
    }


async def test_drivers_lookup_only_in_dp_bad_car_id(taxi_personal_caches):
    response = await taxi_personal_caches.post(
        '/v1/parks/drivers-lookup',
        json={'park_id': 'park2', 'text': '+79998887766 LICENSE1 driver1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'driver_profile_items': [{'driver_id': 'driver1', 'rank': 1020}],
        'filter_status': 'filled',
    }
