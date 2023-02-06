import pytest


@pytest.mark.now('2021-04-20T00:00:00.000000Z')
async def test_place_rating_happy_path(
        taxi_eats_place_rating, mock_authorizer_allowed,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-rating',
        params={'place_id': '5'},
        headers={'X-YaEda-PartnerId': '1'},
    )

    date = '2021-04-20'
    assert response.status_code == 200
    response = response.json()

    assert response == {
        'cancel_rating': {
            'current_rating': {
                'calculated_at': date,
                'delta': -0.1,
                'place_id': 5,
                'rating': 4.0,
                'show_rating': True,
            },
            'history': [
                {'calculated_at': '2021-04-13', 'rating': 3.8},
                {'calculated_at': '2021-04-14', 'rating': 3.7},
                {'calculated_at': '2021-04-15', 'rating': 3.8},
                {'calculated_at': '2021-04-16', 'rating': 3.7},
                {'calculated_at': '2021-04-17', 'rating': 3.8},
                {'calculated_at': '2021-04-18', 'rating': 3.9},
                {'calculated_at': '2021-04-19', 'rating': 4.0},
            ],
            'cancels': [
                {
                    'calculated_at': '2021-04-13',
                    'cancels_count': 0,
                    'order_count': 140,
                },
                {
                    'calculated_at': '2021-04-14',
                    'cancels_count': 1,
                    'order_count': 160,
                },
                {
                    'calculated_at': '2021-04-15',
                    'cancels_count': 0,
                    'order_count': 180,
                },
                {
                    'calculated_at': '2021-04-16',
                    'cancels_count': 0,
                    'order_count': 200,
                },
                {
                    'calculated_at': '2021-04-17',
                    'cancels_count': 3,
                    'order_count': 200,
                },
                {
                    'calculated_at': '2021-04-18',
                    'cancels_count': 0,
                    'order_count': 200,
                },
                {
                    'calculated_at': '2021-04-19',
                    'cancels_count': 2,
                    'order_count': 220,
                },
            ],
            'tips': [],
        },
        'final_rating': {
            'current_rating': {
                'calculated_at': date,
                'delta': -0.1,
                'place_id': 5,
                'rating': 4.5,
                'show_rating': True,
            },
        },
        'user_rating': {
            'welcome_feedbacks': [
                {'feedback': 5},
                {'feedback': 5},
                {'feedback': 5},
                {'feedback': 5},
            ],
            'improve_rating': {
                'target_rating': 3.6,
                'requirement': {'feedback': 5, 'feedbacks_count': 3},
            },
            'current_rating': {
                'calculated_at': date,
                'delta': 0.0,
                'place_id': 5,
                'rating': 3.5,
                'show_rating': True,
            },
            'feedbacks': [
                {
                    'feedback': 2,
                    'created_at': '2021-04-12',
                    'order_id': '100-100',
                },
                {
                    'feedback': 5,
                    'created_at': '2021-04-13',
                    'order_id': '100-200',
                },
            ],
            'tips': [],
        },
    }


async def test_place_rating_error404(
        taxi_eats_place_rating, mock_authorizer_allowed,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-rating',
        params={'place_id': '4'},
        headers={'X-YaEda-PartnerId': '1'},
    )

    assert response.status_code == 404
    response = response.json()
    assert response == {'code': '404', 'message': 'rating not found'}


@pytest.mark.now('2021-04-20T00:00:00.000000Z')
@pytest.mark.experiments3(filename='exp3_eats_place_rating_tips.json')
@pytest.mark.parametrize(
    ['place_id', 'partner_id', 'user_rating_tips', 'cancel_rating_tips'],
    [
        (
            7,
            '1',
            [{'title': 'Совет по умолчанию'}],
            [{'title': 'Совет по умолчанию'}],
        ),
        (
            8,
            '1',
            [{'title': 'Совет по пользовательскому рейтингу'}],
            [{'title': 'Совет по рейтингу отмен'}],
        ),
        (
            9,
            '1',
            [{'title': 'Совет по place_id'}],
            [{'title': 'Совет по place_id'}],
        ),
        (
            10,
            '1',
            [{'title': 'Совет по статистике predefined_comment'}],
            [{'title': 'Совет по статистике cancel_reason'}],
        ),
    ],
)
async def test_place_rating_tips(
        taxi_eats_place_rating,
        mock_authorizer_allowed,
        place_id,
        partner_id,
        user_rating_tips,
        cancel_rating_tips,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-rating',
        params={'place_id': place_id},
        headers={'X-YaEda-PartnerId': partner_id},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['user_rating']['tips'] == user_rating_tips
    assert response['cancel_rating']['tips'] == cancel_rating_tips
