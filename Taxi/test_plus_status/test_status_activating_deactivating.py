import pytest


@pytest.mark.now('2021-08-12T17:38:00.00')
async def test_status_activating(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [1]},
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
                        'status': 'activating',
                        'value': '5',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-08-12T17:38:00.00')
async def test_status_deactivating(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/status',
        headers={'X-YaEda-PartnerId': '1'},
        json={'place_ids': [2]},
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
                        'status': 'deactivating',
                        'value': '4.4',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-08-12T17:38:00.00')
async def test_status_activating_deactivating_active(
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
                        'status': 'activating',
                        'value': '5',
                    },
                ],
            },
            {
                'place_id': 2,
                'statuses': [
                    {
                        'starts': '2020-11-25T15:43:00+00:00',
                        'status': 'deactivating',
                        'value': '4.4',
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
                    {
                        'starts': '2021-12-25T15:43:00+00:00',
                        'status': 'deactivating',
                        'value': '1',
                    },
                ],
            },
        ],
    }
