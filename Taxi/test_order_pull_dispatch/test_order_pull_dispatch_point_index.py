import pytest


@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_dropoff(
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        experiments3,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled
    waybill_info_pull_dispatch['execution']['segments'][0][
        'status'
    ] = 'delivery_arrived'

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['cargo-orders/build-actions'],
        name='cargo_orders_localize_actions',
        clauses=[
            {
                'alias': 'lavka1',
                'enabled': True,
                'extension_method': 'replace',
                'is_paired_signal': False,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'arg_name': 'point_index_in_segment',
                        'arg_type': 'int',
                        'value': 1,
                    },
                    'type': 'eq',
                },
                'title': 'Лавка 1',
                'value': {
                    'pickup_action_tanker_key': 'pickup_action.sms.title',
                    'dropoff_action_tanker_key': (
                        'dropoff_action.pull_dispatch'
                    ),
                },
            },
        ],
        default_value={},
    )

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200
    assert (
        list(
            filter(
                lambda a: a['type'] == 'dropoff',
                response.json()['current_point']['actions'],
            ),
        )[0]['title']
        == 'Вернулся на склад'
    )
