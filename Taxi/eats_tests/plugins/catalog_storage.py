import datetime
import json
import pathlib
import time
import typing

import pytest
import requests


class CatalogStorageService:
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self):
        self.host = None
        self.headers = {'Content-Type': 'application/json'}

    def set_host(self, host: str):
        self.host = host

    def add_place(self, place_id, place_json) -> None:
        _id = place_id
        start = datetime.datetime.now() - datetime.timedelta(hours=8)
        stop = datetime.datetime.now() + datetime.timedelta(hours=8)
        place_json['working_intervals'][0]['from'] = start.strftime(
            self.TIME_FORMAT,
        )
        place_json['working_intervals'][0]['to'] = stop.strftime(
            self.TIME_FORMAT,
        )
        response = requests.put(
            url=f'{self.host}/internal/eats-catalog-storage/v1/place/{_id}',
            data=json.dumps(place_json),
            headers=self.headers,
        )
        if response.status_code != 200:
            pytest.fail(
                f'Incorrect response for url={response.request.url}:'
                f'\n{response.text}',
            )

    def add_delivery_zone(self, zone_json, zone_id, place_id=None) -> None:
        _id = zone_id
        service_start = datetime.datetime.now() - datetime.timedelta(hours=5)
        service_stop = datetime.datetime.now() + datetime.timedelta(hours=5)
        zone_json['working_intervals'][0]['from'] = service_start.strftime(
            self.TIME_FORMAT,
        )
        zone_json['working_intervals'][0]['to'] = service_stop.strftime(
            self.TIME_FORMAT,
        )
        if place_id is not None:
            zone_json['place_id'] = place_id

        response = requests.put(
            url=f'{self.host}'
                f'/internal/eats-catalog-storage/v1/delivery_zone/{_id}',
            data=json.dumps(zone_json),
            headers=self.headers,
        )
        if response.status_code != 200:
            pytest.fail(
                f'Incorrect response for url={response.request.url}:'
                f'\n{response.text}',
            )

    def get_places_by_slug_name(self, *names) -> typing.Mapping:
        response = requests.post(
            url=f'{self.host}'
            f'/internal/eats-catalog-storage/v1/search/places/list',
            json={'place_slugs': [name for name in names]},
        )
        response.raise_for_status()
        return response.json().get('places', [])

    def get_zone_by_place_ids(self, *place_ids):
        response = requests.post(
            url=(
                f'{self.host}'
                '/internal/eats-catalog-storage/v1/search/delivery-zones/list'
            ),
            json={'place_ids': [_id for _id in place_ids]},
        )
        response.raise_for_status()
        return response.json().get('delivery_zones', [])

    def wait_for_place_cache_updated(self, slug, timeout=5) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            places = self.get_places_by_slug_name(slug)
            if (
                    next(
                        (
                            p
                            for p in places
                            if p.get('place', {}).get('slug') == slug
                        ),
                        None,
                    )
                    is not None
            ):
                return True
            time.sleep(0.5)
        return False

    def wait_for_zone_cache_updated(self, place_id, name, timeout=5):
        start = time.time()
        while time.time() - start < timeout:
            zones = self.get_zone_by_place_ids(place_id)
            if (
                    next(
                        (
                            p
                            for p in zones
                            if p.get('delivery_zone', {}).get('name') == name
                        ),
                        None,
                    )
                    is not None
            ):
                return True
            time.sleep(0.5)
        return False


@pytest.fixture
def catalog_storage():
    return CatalogStorageService()


@pytest.fixture
def restaurants() -> typing.Mapping:
    places = {}
    folder = pathlib.Path('/taxi/integration_tests/places')
    for file in folder.glob('*.json'):
        with open(file, 'r') as json_file:
            content = json.load(json_file)
            places[content.get('slug')] = content
    return places


@pytest.fixture
def delivery_zones() -> typing.Mapping:
    zones = {}
    folder = pathlib.Path('/taxi/integration_tests/delivery_zones')
    for file in folder.glob('*.json'):
        with open(file, 'r') as json_file:
            content = json.load(json_file)
            zones[content.get('name')] = content
    return zones
