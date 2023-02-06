# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest

from .static import test_offers


@pytest.mark.experiments3(filename='use_nordstream_false_on_configs.json')
async def test_offer_debug(taxi_market_offers_http):
    response = await taxi_market_offers_http.get(
        '/market-offers/v1/offer?business_id=0&yabs_id=0&shop_id=0&warehouse_id=0&debug=true&user_region=213',
    )
    assert response.status_code == 200
    assert response.json()['debug']['version'] == '0.0.0'
    assert 'nordstream_version' not in response.json()['debug']


@pytest.mark.experiments3(filename='use_nordstream_true_on_configs.json')
async def test_offer_debug(taxi_market_offers_http):
    response = await taxi_market_offers_http.get(
        '/market-offers/v1/offer?business_id=0&yabs_id=0&shop_id=0&warehouse_id=0&debug=true&user_region=213',
    )
    assert response.status_code == 200
    assert response.json()['debug']['version'] == '0.0.0'
    # Прокидывается, как статический ресурс из config_vars.user.testsuite
    assert response.json()['debug']['nordstream_version'] == '1.0.0'


async def test_offer_trivial(taxi_market_offers_http, mockserver):
    @mockserver.json_handler('/market-hide-offers-rt/v1/offers/check_status')
    def _mock_hider(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        assert len(request.json['items']) == 1
        assert request.json['items'][0]['business_id'] == 123

        return {
            'items': [
                {
                    'yabs_id': 'string',
                    'business_id': 123,
                    'service_offers': [
                        {
                            'id': {
                                'shop_id': 0,
                                'warehouse_id': 0,
                                'feed_id': 0,
                                'features': ['string'],
                            },
                            'status': 'allowed',
                        },
                    ],
                },
            ],
        }

    response = await taxi_market_offers_http.get(
        '/market-offers/v1/offer?business_id=123&yabs_id=0&shop_id=0&warehouse_id=0&user_region=213',
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='use_nordstream_false_on_configs.json')
async def test_offer_nordstream_off(taxi_market_offers_http):
    response = await taxi_market_offers_http.get(
        f"/market-offers/v1/offer?offer_sid={test_offers.MAP_OFFER_SID['offer_large']}&user_region=213&debug=true",
    )
    assert response.status_code == 200
    assert (
        response.json()['offers'][0]['offer_sid']
        == test_offers.MAP_OFFER_SID['offer_large']
    )
    assert 'hidden_offers' not in response.json()['debug']


@pytest.mark.experiments3(filename='use_nordstream_true_on_configs.json')
async def test_offer_nordstream_on(taxi_market_offers_http):
    response = await taxi_market_offers_http.get(
        f"/market-offers/v1/offer?offer_sid={test_offers.MAP_OFFER_SID['offer_large']}&user_region=213&debug=true",
    )
    assert response.status_code == 200
    assert response.json()['offers'] == []
    assert (
        response.json()['debug']['hidden_offers'][0]['offer_sid']
        == test_offers.MAP_OFFER_SID['offer_large']
    )
