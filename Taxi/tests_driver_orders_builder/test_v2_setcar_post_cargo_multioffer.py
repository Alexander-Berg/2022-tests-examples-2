import pytest


@pytest.mark.parametrize('is_enabled_multioffer_by_exp', [True, False])
@pytest.mark.parametrize(
    'is_default_layout_for_chain_order_by_exp', [True, False],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cargo_multipoints': True},
)
@pytest.mark.parametrize(
    'mock_claim_ids',
    [
        ['claim_id_1', 'claim_id_2'],
        ['claim_id_1', 'claim_id_2', 'claim_id_3', 'claim_id_4', 'claim_id_5'],
    ],
)
async def test_cargo_multioffer(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        stq,
        experiments3,
        is_enabled_multioffer_by_exp,
        is_default_layout_for_chain_order_by_exp,
        mock_cargo_setcar_data,
        mock_claim_ids,
        setcar_create_params,
        order_proc,
):
    exp_default_value = {
        'header': {
            'show_type': 'tanker_string',
            'subtitle_show_type': 'tanker_string',
            'tanker_key': 'eats_courier_order_title',
            'subtitle_tanker_key': 'eats_courier_order_subtitle',
            'time_interval_type': 'b_a',
        },
        'acceptance_button': {'use_default': True},
    }
    clauses = []
    if is_enabled_multioffer_by_exp:
        exp_clause_value = exp_default_value.copy()
        exp_clause_value['rear_card_layout'] = (
            'default' if is_default_layout_for_chain_order_by_exp else 'custom'
        )
        clauses = [
            {
                'title': 'for_multioffer',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {'arg_name': 'is_multioffer'},
                                'type': 'bool',
                            },
                            # {
                            #     'init': {
                            #         'value': 'eda',
                            #         'arg_name': 'orders_providers',
                            #         'arg_type': 'string',
                            #     },
                            #     'type': 'contains',
                            # },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': exp_clause_value,
            },
        ]
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_courier_screen_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=clauses,
        default_value=exp_default_value,
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, 'order_core_response_courier.json')

    mock_cargo_setcar_data(claim_ids=mock_claim_ids, is_picker_order=True)

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    response_json = response.json()

    assert response.status_code == 200

    if not is_enabled_multioffer_by_exp:
        assert 'rear_card_title' not in response_json['setcar']['ui']
        return

    if is_default_layout_for_chain_order_by_exp:
        assert 'rear_card' not in response_json['setcar']['ui']
    else:
        assert 'rear_card' in response_json['setcar']['ui']

    if len(mock_claim_ids) == 2:
        assert (
            response_json['setcar']['ui']['rear_card_title']
            == 'Мультизаказ - 2 заказа'
        )
    else:
        assert (
            response_json['setcar']['ui']['rear_card_title']
            == 'Мультизаказ - 5 заказов'
        )
