import json

import pytest

from . import conftest
from . import experiments


PIPELINE = 'delivery_price_pipeline_2'
REGION_ID = '2'

DEFAULT_CATALOG_REQUEST = {
    'offer': '2018-08-01T12:59:23.231000+00:00',
    'place_info': {
        'place_id': 1,
        'region_id': int(REGION_ID),
        'brand_id': 3,
        'position': [38, 57],
        'type': 'native',
        'business_type': 'restaurant',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'zone_info': {'zone_type': 'pedestrian'},
}

DEFAULT_CART_REQUEST = {
    'due': '2021-03-30T12:55:00+00:00',
    'offer': '2021-03-30T12:55:00+00:00',
    'place_info': {
        'place_id': '1',
        'region_id': REGION_ID,
        'brand_id': '3',
        'position': [38.0, 57.0],
        'type': 'native',
        'currency': {'sign': '$'},
        'business_type': 'restaurant',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'cart_info': {'subtotal': '250'},
    'zone_info': {'zone_type': 'pedestrian'},
    'shipping_type': 'delivery',
}


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.set_simple_pipeline_file(prefix=PIPELINE)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price(PIPELINE)
async def test_price_statistics_catalog(
        taxi_eda_delivery_price, taxi_eda_delivery_price_monitor, mocked_time,
):
    await taxi_eda_delivery_price.tests_control(reset_metrics=True)
    for _ in range(2):
        response = await taxi_eda_delivery_price.post(
            'v1/calc-delivery-price-surge',
            data=json.dumps(DEFAULT_CATALOG_REQUEST),
        )
        assert response.status_code == 200

    metrics = await taxi_eda_delivery_price_monitor.get_metrics(
        'price-statistics',
    )
    for metric in [
            'max_catalog_delivery_fee_native',
            'max_catalog_delivery_fee_taxi',
    ]:
        assert metrics['price-statistics'][metric] == {
            '$meta': {'solomon_children_labels': 'pipeline'},
            PIPELINE: {
                '$meta': {'solomon_children_labels': 'region_id'},
                REGION_ID: {
                    '$meta': {'solomon_children_labels': 'percentile'},
                    'p0': 0.0,
                    'p50': 0.0,
                    'p90': 0.0,
                    'p95': 0.0,
                    'p100': 0.0,
                },
            },
        }


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.set_simple_pipeline_file(prefix=PIPELINE)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_delivery_price(PIPELINE)
async def test_price_statistics_cart(
        taxi_eda_delivery_price, taxi_eda_delivery_price_monitor, load_json,
):
    await taxi_eda_delivery_price.tests_control(reset_metrics=True)
    for _ in range(2):
        response = await taxi_eda_delivery_price.post(
            'internal/v1/cart-delivery-price-surge',
            data=json.dumps(DEFAULT_CART_REQUEST),
        )
        assert response.status_code == 200

    metrics = await taxi_eda_delivery_price_monitor.get_metrics(
        'price-statistics',
    )
    for metric in [
            'max_cart_delivery_fee_native',
            'max_cart_delivery_fee_taxi',
    ]:
        assert metrics['price-statistics'][metric] == {
            '$meta': {'solomon_children_labels': 'pipeline'},
            PIPELINE: {
                '$meta': {'solomon_children_labels': 'region_id'},
                REGION_ID: {
                    '$meta': {'solomon_children_labels': 'percentile'},
                    'p0': 0.0,
                    'p50': 0.0,
                    'p90': 0.0,
                    'p95': 0.0,
                    'p100': 0.0,
                },
            },
        }
