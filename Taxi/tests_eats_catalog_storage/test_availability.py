import typing

import pytest

from tests_eats_catalog_storage import sql


@pytest.fixture(name='availability')
def search_places_with_zones(taxi_eats_catalog_storage):
    path = '/internal/eats-catalog-storage/v1/service/availability'

    async def request(lon: float, lat: float):
        return await taxi_eats_catalog_storage.get(
            path, params={'latitude': lat, 'longitude': lon},
        )

    return request


@pytest.mark.parametrize(
    'services',
    [
        pytest.param(
            [
                {'type': 'eats', 'isAvailable': False, 'isExist': True},
                {'type': 'grocery', 'isAvailable': False, 'isExist': False},
                {'type': 'shop', 'isAvailable': False, 'isExist': False},
            ],
            marks=(
                pytest.mark.pgsql(
                    'eats_catalog_storage',
                    files=['insert_only_eats_unavailable.sql'],
                )
            ),
            id='eats exists but not available',
        ),
        pytest.param(
            [
                {'type': 'eats', 'isAvailable': False, 'isExist': True},
                {'type': 'grocery', 'isAvailable': False, 'isExist': True},
                {'type': 'shop', 'isAvailable': False, 'isExist': True},
            ],
            marks=(
                pytest.mark.pgsql(
                    'eats_catalog_storage', files=['insert_all_exists.sql'],
                )
            ),
            id='all exists but not available',
        ),
        pytest.param(
            [
                {'type': 'eats', 'isAvailable': True, 'isExist': True},
                {'type': 'grocery', 'isAvailable': True, 'isExist': True},
                {'type': 'shop', 'isAvailable': True, 'isExist': True},
            ],
            marks=(
                pytest.mark.pgsql(
                    'eats_catalog_storage',
                    files=['insert_all_exists_and_available.sql'],
                )
            ),
            id='all exists and available',
        ),
    ],
)
@pytest.mark.now('2020-10-10T11:00:00+03:00')
async def test_availability(availability, services):

    response = await availability(lon=0.5, lat=0.5)
    assert response.status_code == 200
    assert response.json() == {'payload': {'services': services}}


@pytest.fixture(name='brands_count')
def count_business_brands(taxi_eats_catalog_storage):
    path = '/internal/eats-catalog-storage/v1/brands/count'

    async def request(lon: float, lat: float):
        return await taxi_eats_catalog_storage.post(
            path, json={'position': {'lon': lat, 'lat': lon}},
        )

    return request


def make_place(
        place_id: int, business: sql.Business,
) -> typing.Tuple[sql.Place, sql.DeliverZone]:
    return (
        sql.Place(
            place_id=place_id,
            business=business,
            brand=sql.Brand(brand_id=place_id),
        ),
        sql.DeliverZone(
            zone_id=place_id,
            external_id=str(place_id),
            place_id=place_id,
            polygon=sql.default_polygon(),
        ),
    )


async def test_businsess_count(database, brands_count):
    expected_count = {
        sql.Business.restaurant: 2,
        sql.Business.shop: 10,
        sql.Business.store: 1,
        sql.Business.zapravki: 20,
    }

    place_id: int = 0

    for business, count in expected_count.items():
        for _ in range(0, count):
            place_id += 1
            place, zone = make_place(place_id, business)
            database.insert_place(place)
            database.insert_zone(zone)

    response = await brands_count(lon=0.5, lat=0.5)
    assert response.status_code == 200

    data = response.json()
    assert data['business_count']

    for business_count in data['business_count']:
        business = sql.Business[business_count['business']]
        assert expected_count[business] == business_count['count']
