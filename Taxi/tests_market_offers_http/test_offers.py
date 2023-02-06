# flake8: noqa
# pylint: disable=import-error,wildcard-import

import pytest

from .static import test_offers


def to_dict(offers):
    return dict([(elem['offer_sid'], elem) for elem in offers])


async def test_offers_trivial(taxi_market_offers_http):
    response = await taxi_market_offers_http.post(
        '/market-offers/v1/offers', {'offers': [], 'user_region': 213},
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='use_nordstream_false_on_configs.json')
async def test_offers_nordstream_off(taxi_market_offers_http):
    response = await taxi_market_offers_http.post(
        '/market-offers/v1/offers',
        {
            'offers': list(test_offers.MAP_OFFER_SID.values()),
            'user_region': 213,
            'debug': True,
        },
    )
    assert response.status_code == 200
    offers = to_dict(response.json()['offers'])
    hidden_offers = to_dict(response.json()['debug']['hidden_offers'])
    assert {
        test_offers.MAP_OFFER_SID['offer_no_parcel'],
        test_offers.MAP_OFFER_SID['offer_small'],
        test_offers.MAP_OFFER_SID['offer_medium'],
        test_offers.MAP_OFFER_SID['offer_large'],
        test_offers.MAP_OFFER_SID['offer_prohibited_cargo'],
    } == offers.keys()
    assert {} == hidden_offers


@pytest.mark.experiments3(filename='use_nordstream_true_on_configs.json')
async def test_offers_nordstream_on(taxi_market_offers_http):
    info_delivery = {
        'use_yaml_delivery': False,
        'pickup': False,
        'store': False,
        'delivery': True,
    }
    info_pickup_delivery = {
        'use_yaml_delivery': False,
        'pickup': True,
        'store': False,
        'delivery': True,
    }

    response = await taxi_market_offers_http.post(
        '/market-offers/v1/offers',
        {
            'offers': list(test_offers.MAP_OFFER_SID.values()),
            'user_region': 213,
            'debug': True,
        },
    )
    assert response.status_code == 200
    offers = to_dict(response.json()['offers'])
    hidden_offers = to_dict(response.json()['debug']['hidden_offers'])
    assert {
        test_offers.MAP_OFFER_SID['offer_small'],
        test_offers.MAP_OFFER_SID['offer_medium'],
    } == offers.keys()
    assert {
        test_offers.MAP_OFFER_SID['offer_no_parcel'],
        test_offers.MAP_OFFER_SID['offer_large'],
        test_offers.MAP_OFFER_SID['offer_prohibited_cargo'],
    } == hidden_offers.keys()
    assert (
        offers[test_offers.MAP_OFFER_SID['offer_small']]['delivery_info']
        == info_delivery
    )
    assert (
        offers[test_offers.MAP_OFFER_SID['offer_medium']]['delivery_info']
        == info_delivery
    )

    response = await taxi_market_offers_http.post(
        '/market-offers/v1/offers',
        {
            'offers': list(test_offers.MAP_OFFER_SID.values()),
            'user_region': 20490,
            'debug': True,
        },
    )
    assert response.status_code == 200
    offers = to_dict(response.json()['offers'])
    hidden_offers = to_dict(response.json()['debug']['hidden_offers'])
    assert {
        test_offers.MAP_OFFER_SID['offer_small'],
        test_offers.MAP_OFFER_SID['offer_medium'],
        test_offers.MAP_OFFER_SID['offer_large'],
    } == offers.keys()
    assert {
        test_offers.MAP_OFFER_SID['offer_no_parcel'],
        test_offers.MAP_OFFER_SID['offer_prohibited_cargo'],
    } == hidden_offers.keys()
    assert (
        offers[test_offers.MAP_OFFER_SID['offer_small']]['delivery_info']
        == info_pickup_delivery
    )
    assert (
        offers[test_offers.MAP_OFFER_SID['offer_medium']]['delivery_info']
        == info_pickup_delivery
    )
    assert (
        offers[test_offers.MAP_OFFER_SID['offer_large']]['delivery_info']
        == info_pickup_delivery
    )

    response = await taxi_market_offers_http.post(
        '/market-offers/v1/offers',
        {
            'offers': list(test_offers.MAP_OFFER_SID.values()),
            'user_region': 1928,
            'debug': True,
        },
    )
    assert response.status_code == 200
    offers = to_dict(response.json()['offers'])
    hidden_offers = to_dict(response.json()['debug']['hidden_offers'])
    assert {} == offers
    assert {
        test_offers.MAP_OFFER_SID['offer_no_parcel'],
        test_offers.MAP_OFFER_SID['offer_small'],
        test_offers.MAP_OFFER_SID['offer_medium'],
        test_offers.MAP_OFFER_SID['offer_large'],
        test_offers.MAP_OFFER_SID['offer_prohibited_cargo'],
    } == hidden_offers.keys()
    assert (
        hidden_offers[test_offers.MAP_OFFER_SID['offer_no_parcel']]['reason']
        == 'nordstream_no_parcel'
    )
    assert (
        hidden_offers[test_offers.MAP_OFFER_SID['offer_small']]['reason']
        == 'nordstream_no_delivery'
    )
