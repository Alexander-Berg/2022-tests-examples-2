import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_skip_source_points_action_settings',
    consumers=['cargo-claims/driver'],
    clauses=[],
    default_value={
        'is_enabled': True,
        'min_waiting_time_seconds': 20,
        'use_free_waiting_time_rules': False,
    },
)
async def test_multi_skip_source_point(
        taxi_cargo_orders,
        mock_waybill_info,
        mock_driver_tags_v1_match_profile,
        my_batch_waybill_info,
        get_driver_cargo_state,
        set_segment_status,
        set_current_point,
        default_order_id,
        find_action,
):
    set_current_point(my_batch_waybill_info, 0)
    set_segment_status(my_batch_waybill_info, 0, 'performer_found')

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    assert find_action(response.json(), 'multi_skip_source_point') == {
        'type': 'multi_skip_source_point',
        'free_conditions': [
            {'type': 'time_after', 'value': '2020-06-17T19:40:10.000000Z'},
        ],
        'force_allowed': False,
        'force_punishments': [],
    }
    assert find_action(response.json(), 'skip_source_point') is None


@pytest.mark.parametrize(
    [
        'waybill_tpl',
        'skipped_segments_list',
        'same_segments_ids_list',
        'has_action',
    ],
    [
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl.json',
            None,
            None,
            False,
            id='Not a batch',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_batch_tpl.json',
            None,
            None,
            True,
            id='A batch',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_batch_tpl.json',
            ['seg_2'],
            None,
            False,
            id='A batch with a skipped segment',
        ),
        # TODO: add a case with an already resolved segment
        pytest.param(
            'cargo-dispatch/v1_waybill_info_batch_tpl.json',
            None,
            [0, 1],
            False,
            id='A batch with a one unique source point',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_triple_batch_tpl.json',
            ['seg_2', 'seg_3'],
            [1, 2],
            False,
            id='A batch with a simple point and fully skipped unique point',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_triple_batch_tpl.json',
            ['seg_2'],
            [1, 2],
            True,
            id='A batch with a simple point and halfly skipped unique point',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_skip_source_points_action_settings',
    consumers=['cargo-claims/driver'],
    clauses=[],
    default_value={
        'is_enabled': True,
        'min_waiting_time_seconds': 20,
        'use_free_waiting_time_rules': False,
    },
)
async def test_multi_skip_source_point_conditions(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        get_driver_cargo_state,
        set_segments_points_skipped,
        set_segments_place_id,
        set_segment_status,
        set_current_point,
        default_order_id,
        waybill_state,
        find_action,
        waybill_tpl,
        skipped_segments_list,
        same_segments_ids_list,
        has_action,
):
    waybill_info = waybill_state.load_waybill(waybill_tpl)
    set_current_point(waybill_info, 0)
    set_segment_status(waybill_info, 0, 'performer_found')
    if skipped_segments_list is not None:
        set_segments_points_skipped(waybill_info, skipped_segments_list)
    if same_segments_ids_list is not None:
        set_segments_place_id(waybill_info, same_segments_ids_list, 123)

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200
    assert (
        find_action(response.json(), 'multi_skip_source_point') is not None
    ) == has_action
