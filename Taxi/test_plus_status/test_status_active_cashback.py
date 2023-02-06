import pytest


@pytest.mark.now('2021-08-12T17:38:00.00')
async def test_status_active(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [2, 3]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 2,
                'statuses': [
                    {
                        'starts': '2020-11-25T15:43:00+00:00',
                        'status': 'active',
                        'value': '6',
                    },
                ],
            },
            {
                'place_id': 3,
                'statuses': [
                    {
                        'starts': '2020-11-25T15:43:00+00:00',
                        'status': 'active',
                        'value': '7',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-08-12T17:38:00.00')
async def test_status_active_with_wait_to_start(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1, 2, 3]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 1,
                'statuses': [
                    {
                        'starts': '2020-11-25T15:43:00+00:00',
                        'status': 'active',
                        'value': '5',
                    },
                    {
                        'starts': '2021-09-20T18:43:00+00:00',
                        'status': 'wait_to_start',
                        'value': '10',
                    },
                ],
            },
            {
                'place_id': 2,
                'statuses': [
                    {
                        'starts': '2020-11-25T15:43:00+00:00',
                        'status': 'active',
                        'value': '6',
                    },
                ],
            },
            {
                'place_id': 3,
                'statuses': [
                    {
                        'starts': '2020-11-25T15:43:00+00:00',
                        'status': 'active',
                        'value': '7',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-08-12T17:38:00.00')
async def test_status_only_wait_to_start(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [4]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 4,
                'statuses': [
                    {
                        'starts': '2021-09-20T15:43:00+00:00',
                        'status': 'wait_to_start',
                        'value': '3',
                    },
                ],
            },
        ],
    }
