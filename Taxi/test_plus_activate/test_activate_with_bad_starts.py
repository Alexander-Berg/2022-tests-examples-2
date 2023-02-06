import pytest


@pytest.mark.now('2019-12-10T12:00:00+0300')
async def test_activate_with_bad_starts_date(
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
                    'starts': '2019-12-10T12:00:00+0300',
                },
            ],
        },
    )

    assert response.status_code == 400
