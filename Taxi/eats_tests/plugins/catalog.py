import typing

import pytest
import requests


def make_catalog_headers():
    return {
        'x-device-id': 'test_simple',
        'x-platform': 'superapp_taxi_web',
        'x-app-version': '1.12.0',
        'X-Eats-User': 'user_id=123',
        'X-Eats-Session': 'blablabla',
    }


class EatsCatalogService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    def get_slug(
            self,
            slug: str,
            params: typing.Optional[typing.Dict] = None,
    ) -> requests.Response:
        if not params:
            params = {}
        return requests.get(
            url=f'{self.host}/eats-catalog/v1/slug/{slug}',
            params=params,
            headers=make_catalog_headers(),
        )

    def delivery_zones_resolve(
            self,
            place_id: int,
            location: typing.List[float],
            delivery_time: typing.Optional[str] = None,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/internal/v1/delivery-zones/resolve',
            json={
                'place_id': place_id,
                'delivery_time': delivery_time,
                'location': location,
            },
        )


@pytest.fixture
def catalog():
    return EatsCatalogService()
