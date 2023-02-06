async def test_place_rating_history(
        taxi_eats_place_rating, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-rating/history',
        params={'place_id': '1', 'from': '2020-11-24', 'to': '2020-11-25'},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'history': [
            {'calculated_at': '2020-11-24', 'rating': 4.6},
            {'calculated_at': '2020-11-25', 'rating': 4.5},
        ],
    }
