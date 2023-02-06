import pytest


PROMO_NO_ENABLED_RESPONSE = {'code': '404'}


async def test_promo_settings_200(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_core,
):
    url = '/4.0/restapp-front/marketing/v1/promo/settings'

    partner_id = 1

    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 200

    response = response.json()

    expected = {
        'configurations': [
            {
                'type': 'discount',
                'discount': {'minimum': 5, 'maximum': 40},
                'item_ids': {'min_items': 3},
            },
            {'type': 'gift'},
            {'type': 'one_plus_one', 'item_ids': {'min_items': 3}},
        ],
        'available': ['discount', 'gift', 'one_plus_one'],
        'enabled': ['discount', 'gift', 'one_plus_one'],
    }

    assert response == expected


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_PROMO_LIST={
        'available': ['discount', 'gift', 'one_plus_one'],
        'enabled': [],
    },
)
async def test_promo_settings_404(
        taxi_eats_restapp_marketing,
        mockserver,
        mock_authorizer_allowed,
        mock_eats_core,
):
    url = '/4.0/restapp-front/marketing/v1/promo/settings'

    partner_id = 1

    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    response = await taxi_eats_restapp_marketing.get(url, **extra)

    assert response.status_code == 404
