async def test_places_rating_info(taxi_eats_place_rating):
    response = await taxi_eats_place_rating.get(
        '/eats/v1/eats-place-rating/v1/places-rating-info',
        params={'place_ids': ','.join(['1', '2', '3'])},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places_rating_info': [
            {
                'calculated_at': '2020-11-25',
                'place_id': 1,
                'average_rating': 4.5,
                'average_rating_delta': -0.1,
                'cancel_rating': 3.1,
                'cancel_rating_delta': -0.1,
                'user_rating': 5.0,
                'user_rating_delta': 0.0,
                'show_rating': True,
                'feedbacks_count': 6,
            },
            {
                'calculated_at': '2021-03-04',
                'place_id': 2,
                'average_rating': 5.0,
                'average_rating_delta': 5.0,
                'cancel_rating': 5.0,
                'cancel_rating_delta': 5.0,
                'user_rating': 5.0,
                'user_rating_delta': 5.0,
                'show_rating': True,
                'feedbacks_count': 7,
            },
            {
                'calculated_at': '2021-03-04',
                'place_id': 3,
                'average_rating': 4.0,
                'average_rating_delta': 4.0,
                'cancel_rating': 4.0,
                'cancel_rating_delta': 4.0,
                'user_rating': 4.0,
                'user_rating_delta': 4.0,
                'show_rating': False,
            },
        ],
    }
