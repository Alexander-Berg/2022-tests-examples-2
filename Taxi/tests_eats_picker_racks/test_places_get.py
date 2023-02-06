async def test_places_get_200(taxi_eats_picker_racks, init_postgresql):
    places_data = {
        'places': [
            {
                'place_id': 1,
                'place_name': 'first place',
                'place_address': 'first address',
            },
            {
                'place_id': 2,
                'place_name': 'second place',
                'place_address': 'second address',
            },
        ],
    }
    response = await taxi_eats_picker_racks.get('/api/v1/places')
    assert response.status == 200
    print(response.json())
    assert response.json() == places_data
