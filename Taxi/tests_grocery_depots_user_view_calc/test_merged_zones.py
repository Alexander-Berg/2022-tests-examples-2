import pytest

from tests_grocery_depots_user_view_calc import helpers


@pytest.mark.config(GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_ENABLED=True)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_merged_zones(
        taxi_grocery_depots_user_view_calc, grocery_depots,
):
    helpers.prepare_depots(grocery_depots)

    await taxi_grocery_depots_user_view_calc.invalidate_caches()
    await taxi_grocery_depots_user_view_calc.run_periodic_task(
        'zone-merge-periodic-periodic',
    )

    response = await taxi_grocery_depots_user_view_calc.post(
        '/internal/v1/depots/v1/merged-zones', json={'region_id': 213},
    )

    merged_zones = response.json()['merged_zones']
    active_zones = merged_zones['active_zones']
    soon_zones = merged_zones['soon_zones']

    assert len(active_zones) == 1
    assert len(active_zones[0]['extern_contour']['coords']) == 8
    assert len(active_zones[0]['inners']) == 1
    assert len(active_zones[0]['inners'][0]['coords']) == 3

    assert len(soon_zones) == 1
    assert len(soon_zones[0]['extern_contour']['coords']) == 8
    assert len(soon_zones[0]['inners']) == 1
    assert len(soon_zones[0]['inners'][0]['coords']) == 3


@pytest.mark.config(GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_ENABLED=True)
@pytest.mark.now('2020-01-01T12:00:00+0000')
async def test_merged_zones_list(
        taxi_grocery_depots_user_view_calc, grocery_depots,
):
    helpers.prepare_depots(grocery_depots)

    await taxi_grocery_depots_user_view_calc.invalidate_caches()
    await taxi_grocery_depots_user_view_calc.run_periodic_task(
        'zone-merge-periodic-periodic',
    )

    response = await taxi_grocery_depots_user_view_calc.post(
        '/internal/v1/depots/v1/merged-zones/list', json={},
    )
    zone_info = response.json()['zone_info'][0]

    assert zone_info['region_id'] == 213
    assert len(zone_info['merged_zones']['active_zones']) == 1
    assert len(zone_info['merged_zones']['soon_zones']) == 1
