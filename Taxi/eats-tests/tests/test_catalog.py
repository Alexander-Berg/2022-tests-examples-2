import time

import pytest


def test_get_restaurant(catalog):
    catalog.set_host('http://eats-catalog.eda.yandex.net')
    response = catalog.get_slug(slug='coffee_boy_novodmitrovskaya_2k6')
    assert response.status_code == 200, response.text


def test_delivery_zones_resolve(catalog):
    catalog.set_host('http://eats-catalog.eda.yandex.net')
    response = catalog.delivery_zones_resolve(
        place_id=1,
        location=[37.622333, 55.766491],
    )
    assert response.status_code == 200, response.text


def test_delivery(catalog, catalog_storage, restaurants, delivery_zones):
    slug_name = 'magnit'
    zone_name = 'delivery_zone_sample'
    zone_id = 999
    place_id = 100

    catalog.set_host('http://eats-catalog.eda.yandex.net')
    catalog_storage.set_host('http://eats-catalog-storage.eda.yandex.net')
    catalog_storage.add_place(place_id, restaurants[slug_name])
    catalog_storage.add_delivery_zone(
        delivery_zones[zone_name], zone_id, place_id=place_id,
    )
    updated = catalog_storage.wait_for_place_cache_updated(slug_name)
    if not updated:
        pytest.fail(
            f'Restaurant with slug name {slug_name} is not '
            f'found in catalog storage',
        )
    updated = catalog_storage.wait_for_zone_cache_updated(place_id, zone_name)
    if not updated:
        pytest.fail(
            f'Zone with name {zone_name} is not added to catalog storage',
        )

    time.sleep(1)
    response = catalog.delivery_zones_resolve(
        place_id=place_id, location=[37.593179, 55.655806],
    )
    assert response.status_code == 200, response.text
