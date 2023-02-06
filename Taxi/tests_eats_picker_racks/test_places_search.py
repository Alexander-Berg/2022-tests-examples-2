import pytest


def create_places(create_place):
    places = [
        (0, 'name0', 'address0', 0, 'brand0'),
        (1, 'name1', 'address1', 0, 'brand0'),
        (2, 'name2', 'address2', 1, 'brand1'),
        (3, 'name3', 'address3', 1, 'brand1'),
        (4, 'name4', 'address4'),
        (5, 'name5', 'address5'),
        (6, 'name6', '???'),
        (7, '???', '???'),
        (8, 'NaMe8', 'addRESS8'),
    ]
    for place in places:
        create_place(*place)
    return places


@pytest.mark.parametrize(
    'params, expected',
    [
        ({'place_id': 0}, [0]),
        ({'place_id': 1, 'name': 'name1'}, [1]),
        ({'brand_id': 1}, [2, 3]),
        ({'name': 'name'}, [0, 1, 2, 3, 4, 5, 6, 8]),
        ({'name': 'NAME'}, [0, 1, 2, 3, 4, 5, 6, 8]),
        ({'address': 'address'}, [0, 1, 2, 3, 4, 5, 8]),
        ({'address': 'AdDrEsS'}, [0, 1, 2, 3, 4, 5, 8]),
        ({'brand_name': 'and0'}, [0, 1]),
    ],
)
async def test_places_search_200(
        taxi_eats_picker_racks, create_place, params, expected,
):
    places = create_places(create_place)

    response = await taxi_eats_picker_racks.get(
        '/api/v1/places/search', params=params,
    )
    assert response.status == 200

    actual_places = response.json()['places']
    assert len(actual_places) == len(expected)
    for actual_place, expected_place_i in zip(actual_places, expected):
        assert actual_place['place_id'] == places[expected_place_i][0]


@pytest.mark.parametrize(
    'params',
    [
        {'place_id': 100},
        {'name': 'unknown_name'},
        {'address': 'unknown_address'},
        {'brand_id': 100},
        {'brand_name': 'unknown_brand_name'},
        {'place_id': 0, 'name': 'name1'},
        {'place_id': 0, 'name': 'name0', 'address': 'unknown_address'},
    ],
)
async def test_places_search_empty_200(
        taxi_eats_picker_racks, create_place, params,
):
    create_places(create_place)

    response = await taxi_eats_picker_racks.get(
        '/api/v1/places/search', params=params,
    )
    assert response.status == 200

    actual_places = response.json()['places']
    assert not actual_places


async def test_places_search_400(taxi_eats_picker_racks, create_place):
    create_places(create_place)

    response = await taxi_eats_picker_racks.get(
        '/api/v1/places/search', params={},
    )
    assert response.status == 400
