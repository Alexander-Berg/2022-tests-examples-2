import pytest

from . import experiments


@pytest.mark.skip('FIXME: fix this later')
async def test_position(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': 0.5, 'latitude': 0.5},
    )
    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'payload': {
            'slug': 'lavka_2',
            'hasSurge': True,
            'zoneType': 'pedestrian',
        },
    }
    assert response == expected_response


@pytest.mark.parametrize(
    'lat,lon,zonetype,slug',
    [
        (3.5, 3.5, 'pedestrian', 'lavka_with_detailed_zones'),
        (4.5, 4.5, 'yandex_taxi', 'lavka_with_detailed_zones'),
        # Overlapping zones cases. Pedestrian zone prioritized over taxi
        (3.8, 3.1, 'pedestrian', 'lavka_with_detailed_zones'),
        (4.8, 4.1, 'pedestrian', 'lavka_with_overlapping_zones'),
        (12.5, 12.5, 'pedestrian', 'lavka_with_self_overlapping_zones'),
    ],
)
@experiments.zone_priority_config_default
async def test_detailed_zones(
        taxi_overlord_catalog, lat, lon, zonetype, slug, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots_depots_detailed_zones.json',
        'gdepots_zones_detailed_zones.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': lon, 'latitude': lat},
    )
    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'payload': {'slug': slug, 'hasSurge': True, 'zoneType': zonetype},
    }
    assert response == expected_response


@pytest.mark.parametrize(
    'lat,lon,zonetype,slug',
    [
        (3.5, 3.5, 'pedestrian', 'lavka_with_detailed_zones'),
        (4.5, 4.5, 'yandex_taxi', 'lavka_with_detailed_zones'),
        # Taxi zone prioritized over pedestrian by experiment-config
        (3.8, 3.1, 'yandex_taxi', 'lavka_with_overlapping_zones'),
        (4.8, 4.1, 'yandex_taxi', 'lavka_with_detailed_zones'),
        (12.5, 12.5, 'yandex_taxi', 'lavka_with_self_overlapping_zones'),
    ],
)
@experiments.zone_priority_config_taxi_most_priority
async def test_detailed_zones_zone_priorities_experiment(
        taxi_overlord_catalog, lat, lon, zonetype, slug, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots_depots_detailed_zones.json',
        'gdepots_zones_detailed_zones.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': lon, 'latitude': lat},
    )
    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'payload': {'slug': slug, 'hasSurge': True, 'zoneType': zonetype},
    }
    assert response == expected_response


@pytest.mark.parametrize(
    'lat,lon,zone_type,slug',
    [(2.0, 2.0, 'pedestrian', 'lavka_foot_24h'), (8.0, 2.0, None, None)],
)
@pytest.mark.now('2020-05-15T16:00:00+03:00')  # Friday
async def test_zones_working_hours_friday(
        taxi_overlord_catalog, lat, lon, zone_type, slug, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-wms_detailed_zones.json',
        'gdepots-zones-wms_detailed_zones.json',
    )

    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': lon, 'latitude': lat},
    )
    if zone_type is None:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        response = response.json()
        expected_response = {
            'payload': {'slug': slug, 'hasSurge': True, 'zoneType': zone_type},
        }
        assert response == expected_response


@pytest.mark.parametrize(
    'lat,lon,zone_type,slug',
    [
        (2.0, 2.0, 'pedestrian', 'lavka_foot_24h'),
        (2.0, 8.0, 'yandex_taxi', 'lavka_taxi_monday_10_12'),
    ],
)
@pytest.mark.now('2020-05-11T11:00:00+03:00')  # Monday
async def test_zones_working_hours_monday(
        taxi_overlord_catalog, lat, lon, zone_type, slug, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-wms_detailed_zones.json',
        'gdepots-zones-wms_detailed_zones.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': lon, 'latitude': lat},
    )

    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'payload': {'slug': slug, 'hasSurge': True, 'zoneType': zone_type},
    }
    assert response == expected_response


@pytest.mark.parametrize(
    'lat,lon,zone_type,slug',
    [
        (2.0, 2.0, 'yandex_taxi', 'lavka_taxi_acitve_zone'),
        (20.0, 20.0, 'pedestrian', 'lavka_foot_active_zone'),
    ],
)
async def test_disabled_zones(
        taxi_overlord_catalog, lat, lon, zone_type, slug, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-disabled_zone.json',
        'gdepots-zones-disabled_zone.json',
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': lon, 'latitude': lat},
    )

    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'payload': {'slug': slug, 'hasSurge': True, 'zoneType': zone_type},
    }
    assert response == expected_response


async def test_region(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'regionId': 234},
    )
    assert response.status_code == 404


async def test_404(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get(
        '/v1/catalog-stores', params={'longitude': 90, 'latitude': 90},
    )
    assert response.status_code == 404
