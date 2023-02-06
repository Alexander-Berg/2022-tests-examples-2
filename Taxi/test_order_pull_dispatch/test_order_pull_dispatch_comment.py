# pylint: disable=C0302

import pytest


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_batch_screen_comments': '8.00'},
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_newflow_comments_settings',
    consumers=['cargo/newflow-comments-settings'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'clear_source_comment': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_comment_in_source_point(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][0]['is_resolved'] = False

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']

    if pull_dispatch_enabled:
        assert current_point['comment'] == ''
    else:
        assert (
            current_point['comment']
            == 'Код от подъезда/домофона: 123#.\nКомментарий: первая'
        )


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_batch_screen_comments': '8.00'},
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_newflow_comments_settings',
    consumers=['cargo/newflow-comments-settings'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'clear_source_comment': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_comment_in_middle_point(
        taxi_cargo_orders,
        mock_waybill_info,
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
    assert response.status_code == 200

    current_point = response.json()['current_point']

    assert current_point['comment'] == 'Комментарий: вторая точка коммент'


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_batch_screen_comments': '8.00'},
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_newflow_comments_settings',
    consumers=['cargo/newflow-comments-settings'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[
        {
            'title': 'enbled',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {'arg_name': 'point_need_confirmation'},
                            'type': 'bool',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enabled': True,
                'filters': {
                    '__default__': False,
                    'clear_source_comment': True,
                },
            },
        },
    ],
    default_value={'enabled': False, 'filters': {'__default__': False}},
)
@pytest.mark.parametrize('need_confirmation', [True, False])
async def test_pull_dispatch_comment_in_source_point_filter_enabled_disabled(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        need_confirmation,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch']['is_pull_dispatch'] = True

    waybill_info_pull_dispatch['execution']['points'][0]['is_resolved'] = False
    waybill_info_pull_dispatch['execution']['points'][0][
        'need_confirmation'
    ] = need_confirmation

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']

    if need_confirmation:
        assert current_point['comment'] == ''
    else:
        assert (
            current_point['comment']
            == 'Код от подъезда/домофона: 123#.\nКомментарий: первая'
        )
