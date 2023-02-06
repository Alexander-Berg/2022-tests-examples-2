async def test_select_pickers_stores_200(
        taxi_eats_picker_supply, create_picker,
):
    picker_id1 = 'picker1'
    picker_id2 = 'picker2'

    picker1_places = [1, 2, 3]
    picker2_places = [4, 5, 6]

    create_picker()  # unused picker
    create_picker(picker_id=picker_id1, places_ids=picker1_places)
    create_picker(picker_id=picker_id2, places_ids=picker2_places)

    response = await taxi_eats_picker_supply.post(
        '/api/v1/select-pickers-stores',
        json={'picker_ids': [picker_id1, picker_id2]},
    )

    assert response.status == 200
    pickers_stores = response.json()['pickers_stores']
    assert len(pickers_stores) == 2
    assert pickers_stores[0]['picker_id'] in [picker_id1, picker_id2]
    assert pickers_stores[1]['picker_id'] in [picker_id1, picker_id2]
    assert pickers_stores[0]['picker_id'] != pickers_stores[1]['picker_id']

    place_ids0 = pickers_stores[0]['place_ids']
    place_ids1 = pickers_stores[1]['place_ids']
    if pickers_stores[0]['picker_id'] == picker_id1:
        assert sorted(place_ids0) == picker1_places
        assert sorted(place_ids1) == picker2_places
    else:
        assert sorted(place_ids0) == picker2_places
        assert sorted(place_ids1) == picker1_places


async def test_select_pickers_stores_no_pickers_in_db_200(
        taxi_eats_picker_supply,
):
    picker_id1 = 'picker1'
    picker_id2 = 'picker2'

    response = await taxi_eats_picker_supply.post(
        '/api/v1/select-pickers-stores',
        json={'picker_ids': [picker_id1, picker_id2]},
    )

    assert response.status == 200
    pickers_stores = response.json()['pickers_stores']
    assert not pickers_stores


async def test_select_pickers_stores_no_pickers_in_request_200(
        taxi_eats_picker_supply,
):
    response = await taxi_eats_picker_supply.post(
        '/api/v1/select-pickers-stores', json={'picker_ids': []},
    )

    assert response.status == 200
    pickers_stores = response.json()['pickers_stores']
    assert not pickers_stores
