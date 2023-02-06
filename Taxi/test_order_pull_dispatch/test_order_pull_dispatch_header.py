# pylint: disable=C0302,C0103
import pytest

pull_dispatch_filters = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {
            '__default__': False,
            'claim_route_points': True,
            'set_title_header': True,
        },
    },
)

# middle point not contain header_title in any case
@pull_dispatch_filters
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_set_headers_middle_point(
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    response = await get_driver_cargo_state(default_order_id)

    current_point = response.json()['current_point']
    # middle point not contain header_title
    assert 'header_title' not in current_point


@pull_dispatch_filters
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_set_headers_last_point(
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][1]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][2]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][3]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][4]['is_resolved'] = True

    response = await get_driver_cargo_state(default_order_id)

    current_point = response.json()['current_point']

    # last point contains header_title if pull_dispatch_enabled
    if not pull_dispatch_enabled:
        assert 'header_title' not in current_point
    else:
        assert (
            current_point['header_title']
            == 'point_label.header_title.pull_dispatch_return'
        )


@pull_dispatch_filters
async def test_pull_dispatch_set_headers_last_point_nobatch(
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch_nobatch,
        mock_driver_tags_v1_match_profile,
):
    waybill_info = waybill_info_pull_dispatch_nobatch
    waybill_info['dispatch']['is_pull_dispatch'] = True
    waybill_info['execution']['points'][0]['is_resolved'] = True
    waybill_info['execution']['points'][1]['is_resolved'] = True

    response = await get_driver_cargo_state(default_order_id)

    current_point = response.json()['current_point']
    assert (
        current_point['header_title']
        == 'point_label.header_title.pull_dispatch_return'
    )
