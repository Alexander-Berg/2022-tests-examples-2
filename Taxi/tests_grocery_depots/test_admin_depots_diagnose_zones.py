import pytest

from testsuite.utils import ordered_object


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_ok(taxi_grocery_depots):
    response = await taxi_grocery_depots.post(
        '/admin/depots/v1/depots/diagnose_zones', json={},
    )
    expected_result = {
        'depots': [
            {'depot_id': 'id-99999901'},
            {'depot_id': 'id-99999902'},
            {'depot_id': 'id-99999907'},
        ],
    }

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_result, ['depots'])


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_ok_by_ids(taxi_grocery_depots):
    response = await taxi_grocery_depots.post(
        '/admin/depots/v1/depots/diagnose_zones',
        json={'depot_ids': ['id-99999907', 'id-99999901']},
    )

    assert response.status_code == 200
    assert response.json() == {
        'depots': [{'depot_id': 'id-99999907'}, {'depot_id': 'id-99999901'}],
    }


@pytest.mark.pgsql(
    'grocery_depots',
    files=[
        'gdepots-depots-default.sql',
        'gdepots-depots-zone_intersection.sql',
        'gdepots-zones-default.sql',
        'gdepots-zones-zone_intersection.sql',
    ],
)
async def test_depots_zone_intersection(taxi_grocery_depots):
    response = await taxi_grocery_depots.post(
        '/admin/depots/v1/depots/diagnose_zones', json={},
    )

    expected_result = {
        'depots': [
            {
                'depot_id': 'zone-intersection-depot',
                'issues': ['zone_overlapping'],
                'zone_overlapping_info': [
                    {
                        'depot_id': 'id-99999901',
                        'location': {'lat': 2.0, 'lon': 2.0},
                        'zone_type': 'yandex_taxi',
                    },
                ],
            },
            {'depot_id': 'id-99999901'},
            {
                'depot_id': 'id-99999902',
                'issues': ['zone_overlapping'],
                'zone_overlapping_info': [
                    {
                        'depot_id': 'zone-intersection-depot',
                        'location': {'lat': 20.0, 'lon': 20.0},
                        'zone_type': 'yandex_taxi_remote',
                    },
                ],
            },
            {'depot_id': 'id-99999907'},
        ],
    }

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_result, ['depots'])


@pytest.mark.pgsql(
    'grocery_depots',
    files=[
        'gdepots-depots-default.sql',
        'gdepots-zones-default.sql',
        'gdepots-depots-zones_disabled.sql',
        'gdepots-zones-zones_disabled.sql',
    ],
)
async def test_depots_all_zones_diabled(taxi_grocery_depots):
    response = await taxi_grocery_depots.post(
        '/admin/depots/v1/depots/diagnose_zones', json={},
    )

    expected_result = {
        'depots': [
            {'depot_id': 'id-99999901'},
            {'depot_id': 'id-99999902'},
            {'depot_id': 'id-99999907'},
            {
                'depot_id': 'all-zones-disabled-depot',
                'issues': ['all_zones_disabled'],
            },
        ],
    }

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_result, ['depots'])


@pytest.mark.pgsql(
    'grocery_depots',
    files=[
        'gdepots-depots-timezones_overlapping.sql',
        'gdepots-zones-timezones_overlapping.sql',
    ],
)
async def test_depots_same_timezones_overlapping(taxi_grocery_depots):
    response = await taxi_grocery_depots.post(
        '/admin/depots/v1/depots/diagnose_zones', json={},
    )
    expected_result = {
        'depots': [
            {'depot_id': 'no-overlapping-depot'},
            {'depot_id': 'different-timezones-depot'},
            {
                'depot_id': 'timezones-overlapping-depot',
                'issues': ['same_timezones_overlapping'],
            },
        ],
    }

    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_result, ['depots'])
