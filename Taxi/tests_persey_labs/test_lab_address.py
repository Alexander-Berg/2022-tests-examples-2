async def test_lab_address_simple(taxi_persey_labs, load_json, fill_labs):
    fill_labs.load_lab_entities(load_json('labs.json'))

    response = await taxi_persey_labs.get(
        f'/internal/v1/lab/address?id=lab_no_employees',
    )
    assert response.status_code == 200
    assert response.json() == {
        'name': 'Никто не пришел на фан-встречу',
        'address': {
            'position': [35.5, 55.5],
            'text': 'Somewhere',
            'locality_id': 2,
            'title': 'some',
            'subtitle': 'where',
            'comment': 'no employees',
        },
    }
    response = await taxi_persey_labs.get(
        f'/internal/v1/lab/address?id=lab_unknown',
    )
    assert response.status_code == 404
