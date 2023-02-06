async def test_get_fridge_and_freezer_info(
        taxi_eats_picker_racks, create_rack, create_place,
):
    place_ids = [1, 2, 3]
    for i in range(0, 2):
        create_place(place_id=place_ids[i])
        create_rack(place_id=place_ids[i], has_fridge=True, has_freezer=False)
        create_rack(
            place_id=place_ids[i],
            name='second',
            has_fridge=False,
            has_freezer=(i == 0),
        )

    response = await taxi_eats_picker_racks.post(
        '/api/v1/fridge_and_freezer_info', json={'place_ids': place_ids},
    )
    assert response.status == 200
    assert 'places_info' in response.json()
    places_info = response.json()['places_info']
    assert len(places_info) == 2
    places_info = sorted(places_info, key=lambda info: info['place_id'])
    for i in range(0, 2):
        assert places_info[i]['place_id'] == place_ids[i]
        assert places_info[i]['has_fridge']
        if i == 0:
            assert places_info[i]['has_freezer']
        else:
            assert not places_info[i]['has_freezer']
