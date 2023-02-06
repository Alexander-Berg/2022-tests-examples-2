import pytest

from tests_contractor_merch import util

HEADERS = util.get_headers('park_id', 'driver_id')

MUTABLE = 'by-offer-id'
IMMUTABLE = 'by-immutable-id'
FETCH_BY_IDS = {
    MUTABLE: '/feeds/v1/fetch_by_id',
    IMMUTABLE: '/feeds/v1/fetch_by_package_id',
}
HANDLERS_BY_IDS = {
    MUTABLE: '/driver/v1/contractor-merch/v1/offer/feed-id-1',
    IMMUTABLE: (
        '/driver/v1/contractor-merch/v1/'
        'offer-by-immutable-id/feeds-admin-id-1'
    ),
}


def _get_price(response_json):
    return {
        'price': response_json['offer']['price'],
        'price_with_currency': response_json['offer']['price_with_currency'],
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=util.ERROR_TRANSLATIONS,
)
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    ['money'],
    [
        pytest.param(
            {'value': '199.99', 'currency': 'RUB', 'formatted': '199.99 ₽'},
            id='RUB',
        ),
        pytest.param(
            {'value': '200', 'currency': 'USD', 'formatted': '200 $'},
            id='USD',
        ),
        pytest.param(
            {'value': '159.28', 'currency': 'EUR', 'formatted': '159.28 €'},
            id='EUR',
        ),
    ],
)
async def test_offer_currencies(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        mock_umlaas_contractors,
        localizations,
        load_json,
        offer_id_type,
        money,
):
    currency = money['currency']

    mock_feeds.set_response(
        load_json('responses/feeds_responses_with_currency.json')[currency],
    )
    mock_billing_replication.set_currency(currency)

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200
    assert _get_price(response.json()) == {
        'price': money['value'],
        'price_with_currency': money,
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=util.ERROR_TRANSLATIONS,
)
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_invalid_currency(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        mock_umlaas_contractors,
        localizations,
        load_json,
        offer_id_type,
):
    mock_feeds.set_response(
        load_json('responses/feeds_responses_with_currency.json')['RUB'],
    )
    mock_billing_replication.set_currency('USD')

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'Offer not found',
        'problem_description': {
            'code': 'offer_changed_or_expired',
            'localized_message': 'offer_changed_or_expired-tr',
        },
    }
