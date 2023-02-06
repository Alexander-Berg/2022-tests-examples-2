import datetime

import pytest

from tests_grocery_depots_user_view_calc import helpers


@pytest.mark.config(
    GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_STQ_RESCHEDULE_ENABLED=True,
    GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_STQ_RESCHEDULE_AFTER_MINUTES=60,
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_merged_zones_stq(
        taxi_grocery_depots_user_view_calc, grocery_depots, stq, stq_runner,
):
    helpers.prepare_depots(grocery_depots)

    response = await taxi_grocery_depots_user_view_calc.post(
        '/internal/v1/depots/v1/merged-zones', json={'region_id': 213},
    )

    assert response.status_code == 404

    await stq_runner.grocery_depots_view_calc_zone_merge_execute.call(
        task_id='any_task_id',
    )

    assert stq.grocery_depots_view_calc_zone_merge_execute.times_called == 1

    next_stq_call = stq.grocery_depots_view_calc_zone_merge_execute.next_call()
    del next_stq_call['kwargs']['log_extra']
    assert next_stq_call == {
        'queue': 'grocery_depots_view_calc_zone_merge_execute',
        'id': 'grocery-depots-view-calc-zones-merge-reschedule',
        'eta': datetime.datetime(2019, 1, 1, 13, 0),
        'args': [],
        'kwargs': {},
    }

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


@pytest.mark.config(
    GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_STQ_RESCHEDULE_ENABLED=False,
    GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_STQ_RESCHEDULE_AFTER_MINUTES=60,
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_merged_zones_stq_no_reschedule(
        taxi_grocery_depots_user_view_calc, grocery_depots, stq, stq_runner,
):
    helpers.prepare_depots(grocery_depots)

    await stq_runner.grocery_depots_view_calc_zone_merge_execute.call(
        task_id='any_task_id',
    )

    assert stq.grocery_depots_view_calc_zone_merge_execute.times_called == 0

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


@pytest.mark.config(
    GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_STQ_RESCHEDULE_ENABLED=False,
    GROCERY_DEPOTS_USER_VIEW_CALC_ZONES_MERGE_STQ_RESCHEDULE_AFTER_MINUTES=60,
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_merged_zones_list_stq(
        taxi_grocery_depots_user_view_calc, grocery_depots, stq, stq_runner,
):
    helpers.prepare_depots(grocery_depots)

    await stq_runner.grocery_depots_view_calc_zone_merge_execute.call(
        task_id='any_task_id',
    )

    response = await taxi_grocery_depots_user_view_calc.post(
        '/internal/v1/depots/v1/merged-zones/list', json={},
    )

    zone_info = response.json()['zone_info'][0]
    active_zones = zone_info['merged_zones']['active_zones']
    soon_zones = zone_info['merged_zones']['soon_zones']

    assert len(active_zones) == 1
    assert len(active_zones[0]['extern_contour']['coords']) == 8
    assert len(active_zones[0]['inners']) == 1
    assert len(active_zones[0]['inners'][0]['coords']) == 3

    assert len(soon_zones) == 1
    assert len(soon_zones[0]['extern_contour']['coords']) == 8
    assert len(soon_zones[0]['inners']) == 1
    assert len(soon_zones[0]['inners'][0]['coords']) == 3

    assert zone_info['region_id'] == 213
    assert 'updated_at' in zone_info
