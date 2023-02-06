import pytest

# from .plugins import mock_personal


YANDEX_COMPANIES = pytest.mark.config(
    OVERLORD_CATALOG_YANDEX_COMPANY_TITLES=['Yandex'],
)


@pytest.mark.pgsql(
    'grocery_depots',
    files=['insert_zones.sql', 'insert_zones_without_timetable.sql'],
)
async def test_all(taxi_grocery_depots):
    await taxi_grocery_depots.invalidate_caches()
    response = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/zones', json={'legacy_depot_ids': []},
    )
    response_zones = response.json()['zones']
    zones_ids = sorted([x['zone_id'] for x in response_zones])
    assert (
        sorted(
            [
                'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_old',
                'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_new',
                'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_remote',
                'zone_id_112',
            ],
        )
        == zones_ids
    )

    assert len(response_zones[0]['geozone']) == 2
    zone_112 = [
        zone for zone in response_zones if zone['zone_id'] == 'zone_id_112'
    ][0]
    assert (
        pytest.approx({'lat': 55.73788714050709, 'lon': 37.64817237854004})
        == zone_112['geozone']['coordinates'][0][0][0]
    )


@pytest.mark.pgsql('grocery_depots', files=['insert_zones_with_invalid.sql'])
async def test_basic(taxi_grocery_depots):
    await taxi_grocery_depots.invalidate_caches()
    response = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/zones', json={'legacy_depot_ids': ['111']},
    )
    zones_ids = sorted([x['zone_id'] for x in response.json()['zones']])
    print(zones_ids)

    assert (
        sorted(
            [
                'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_old',
                'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_new',
                'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_remote',
            ],
        )
        == zones_ids
    )
