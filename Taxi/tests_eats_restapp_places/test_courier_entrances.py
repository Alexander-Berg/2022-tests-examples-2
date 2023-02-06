async def test_update_places_courier_entrances_204(
        taxi_eats_restapp_places, get_info_by_place,
):
    place_ids = [111, 222]

    response_before_update = await taxi_eats_restapp_places.get(
        '/internal/places/info?place_id={}'.format(
            ','.join(map(str, place_ids)),
        ),
    )

    assert response_before_update.status_code == 200
    response_before_update_payload = response_before_update.json()
    assert 'places' in response_before_update_payload
    for place_info in response_before_update_payload['places']:
        assert 'place_id' in place_info
        assert 'courier_entrance' in place_info
        assert 'use_courier_entrance' in place_info

    new_courier_entrance = [55.2334, 39.2355]
    response_on_update = await taxi_eats_restapp_places.post(
        '/internal/places/update-courier-entrances?place_id={}'.format(
            place_ids[0],
        ),
        json={
            'places_courier_entrances': [
                {
                    'place_id': place_ids[0],
                    'courier_entrance': new_courier_entrance,
                    'use_courier_entrance': True,
                },
            ],
        },
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response_on_update.status_code == 204

    for place_info_before_update in response_before_update_payload['places']:
        assert place_info_before_update['place_id'] in place_ids

        place_info = get_info_by_place(place_info_before_update['place_id'])
        assert place_info['place_id'] == place_info_before_update['place_id']

        if place_info_before_update['place_id'] == place_ids[0]:
            assert place_info['use_courier_entrance'] is True
            assert place_info['courier_entrance'] == str(
                tuple(new_courier_entrance),
            ).replace(' ', '')
            break

        assert (
            place_info['use_courier_entrance']
            == place_info_before_update['use_courier_entrance']
        )
        assert place_info['courier_entrance'] == str(
            tuple(place_info_before_update['courier_entrance']),
        ).replace(' ', '')


async def test_update_places_courier_entrances_400(taxi_eats_restapp_places):
    place_id = 333
    new_courier_entrance = [55.2334, 39.2355]

    response = await taxi_eats_restapp_places.post(
        '/internal/places/update-courier-entrances',
        json={
            'places_courier_entrances': [
                {
                    'place_id': place_id,
                    'courier_entrance': new_courier_entrance,
                    'use_courier_entrance': True,
                },
            ],
        },
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response.status_code == 400
    response_payload = response.json()
    assert 'code' in response_payload
    assert int(response_payload['code']) == response.status_code
    assert 'message' in response.json()
