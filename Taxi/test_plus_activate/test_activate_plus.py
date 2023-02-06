import pytest


@pytest.mark.now('2019-12-10T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_activate_plus_good(
        taxi_eats_restapp_promo, stq, pgsql, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/cashback/activate',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'cashbacks': [
                {
                    'place_id': 1,
                    'cashback': '5',
                    'starts': '2019-12-11T12:00:00+0300',
                },
                {
                    'place_id': 2,
                    'cashback': '4.5',
                    'starts': '2019-12-10T21:00:00+0000',
                },
                {
                    'place_id': 3,
                    'cashback': '10',
                    'starts': '2019-12-11T00:00:00+0300',
                },
            ],
        },
    )

    assert stq.eats_restapp_promo_plus_activation.times_called == 3

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 1,
                'statuses': [
                    {
                        'starts': '2019-12-11T09:00:00+00:00',
                        'status': 'activating',
                        'value': '5',
                    },
                ],
            },
            {
                'place_id': 2,
                'statuses': [
                    {
                        'starts': '2019-12-10T21:00:00+00:00',
                        'status': 'activating',
                        'value': '4.5',
                    },
                ],
            },
            {
                'place_id': 3,
                'statuses': [
                    {
                        'starts': '2019-12-10T21:00:00+00:00',
                        'status': 'activating',
                        'value': '10',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2021-09-09T15:22:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_activate_plus_good_in_diff_timezone(
        taxi_eats_restapp_promo, stq, pgsql, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/cashback/activate',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'cashbacks': [
                {
                    'place_id': 55,
                    'cashback': '5',
                    'starts': '2021-09-09T20:00:00+0000',
                },
            ],
        },
    )

    assert stq.eats_restapp_promo_plus_activation.times_called == 1

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {
                'place_id': 55,
                'statuses': [
                    {
                        'starts': '2021-09-09T20:00:00+00:00',
                        'status': 'activating',
                        'value': '5',
                    },
                ],
            },
        ],
    }


@pytest.mark.now('2019-12-10T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_activate_plus_bad_start_date(
        taxi_eats_restapp_promo, stq, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/cashback/activate',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'cashbacks': [
                {
                    'place_id': 1,
                    'cashback': '1',
                    'starts': '2019-12-10T20:00:00+0000',
                },
            ],
        },
    )

    assert stq.eats_restapp_promo_plus_activation.times_called == 0

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Incorrect start date'}


@pytest.mark.now('2019-12-10T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_activate_plus_bad_and_good_in_one(
        taxi_eats_restapp_promo, stq, mock_authorizer_allowed,
):

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/plus/cashback/activate',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'cashbacks': [
                {
                    'place_id': 1,
                    'cashback': '1',
                    'starts': '2019-12-10T20:00:00+0000',
                },
                {
                    'place_id': 3,
                    'cashback': '10',
                    'starts': '2019-12-11T00:00:00+0300',
                },
            ],
        },
    )

    assert stq.eats_restapp_promo_plus_activation.times_called == 0

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Incorrect start date'}
