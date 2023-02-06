import pytest


async def test_activate_autorization_403(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_403,
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
            ],
        },
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


async def test_activate_autorization_400(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_400,
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
            ],
        },
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.now('2019-12-10T12:00:00+0300')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
async def test_activate_autorization_200(
        taxi_eats_restapp_promo, mockserver, mock_authorizer_allowed,
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
            ],
        },
    )

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
        ],
    }
