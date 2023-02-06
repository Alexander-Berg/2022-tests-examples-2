async def test_places_rating(
        taxi_eats_place_rating, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/places-rating',
        params={'place_ids': ','.join(['1', '2', '3'])},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places_rating': [
            {
                'calculated_at': '2020-11-25',
                'delta': -0.1,
                'place_id': 1,
                'rating': 4.5,
                'show_rating': True,
            },
            {
                'calculated_at': '2021-03-04',
                'delta': 5.0,
                'place_id': 2,
                'rating': 5.0,
                'show_rating': True,
            },
            {
                'calculated_at': '2021-03-04',
                'delta': 4.0,
                'place_id': 3,
                'rating': 4.0,
                'show_rating': False,
            },
        ],
    }
