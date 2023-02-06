from typing import Optional

import pytest


@pytest.fixture(name='catalog_for_full_text_search')
def catalog_for_full_text_search(taxi_eats_catalog):
    async def client(
            longitude: Optional[float] = 37.591503,
            latitude: Optional[float] = 55.802998,
            region_id: Optional[int] = None,
            blocks: Optional[list] = None,
            shipping_type: Optional[str] = None,
            delivery_time: Optional[str] = None,
            time_zone: int = 10800,
            platform: str = 'desktop_web',
            version: str = '0.0.0',
            cookie: Optional[str] = None,
            x_request_id: Optional[str] = None,
            x_device_id: Optional[str] = None,
            x_mobile_ifa: Optional[str] = None,
            x_appmetrica_uuid: Optional[str] = None,
            useragent: Optional[str] = None,
    ):

        body: dict = {}

        body['blocks'] = blocks or [{'id': 'any', 'type': 'any'}]

        if longitude is not None and latitude is not None:
            body['longitude'] = float(longitude)
            body['latitude'] = float(latitude)

        if region_id is not None:
            body['region_id'] = int(region_id)

        if delivery_time is not None:
            body['delivery_time'] = {
                'time': str(delivery_time),
                'zone': time_zone,
            }

        if shipping_type is not None:
            body['shipping_type'] = str(shipping_type)

        return await taxi_eats_catalog.post(
            '/internal/v1/catalog-for-full-text-search',
            headers={
                'x-platform': platform,
                'x-app-version': version,
                'cookie': cookie,
                'x-request-id': x_request_id,
                'x-device-id': x_device_id,
                'x-mobile-ifa': x_mobile_ifa,
                'x-appmetrica-uuid': x_appmetrica_uuid,
                'user-agent': useragent,
            },
            json=body,
        )

    return client
