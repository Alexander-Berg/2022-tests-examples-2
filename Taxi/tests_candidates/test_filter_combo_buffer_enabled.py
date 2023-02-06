import pytest


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
@pytest.mark.parametrize(
    'clause_enabled,is_buffer_combo,expected_drivers',
    [
        (False, True, ['dbid0_uuid0', 'dbid0_uuid1']),
        (True, False, ['dbid0_uuid0', 'dbid0_uuid1']),
        (True, True, ['dbid0_uuid0']),
    ],
)
async def test_filter_combo_buffer_enabled(
        taxi_candidates,
        driver_positions,
        combo_contractors,
        experiments3,
        clause_enabled,
        is_buffer_combo,
        expected_drivers,
):
    disable_combo_taximeter_version_filters(experiments3)
    configure_combo_buffer_filter(experiments3, clause_enabled, ['uuid0'])

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
        ],
    )

    combo_contractors(
        [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
    )

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
        'order': {'calc': {'alternative_type': 'combo_outer'}},
    }
    if is_buffer_combo:
        request_body['order']['buffer_combo'] = {'enabled': True}

    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]

    assert sorted(candidates) == expected_drivers


def disable_combo_taximeter_version_filters(experiments3):
    for exp_name in [
            'combo_outer_taximeter_version',
            'combo_taximeter_version',
    ]:
        experiments3.add_config(
            name=exp_name,
            consumers=['candidates/filters'],
            default_value={'enabled': True},
        )


def configure_combo_buffer_filter(experiments3, enabled, test_drivers):
    experiments3.add_config(
        name='combo_buffer_contractors',
        consumers=['candidates/filters'],
        clauses=[
            {
                'value': {'enabled': False},
                'predicate': {
                    'type': 'not',
                    'init': {
                        'predicate': {
                            'type': 'in_set',
                            'init': {
                                'set': test_drivers,
                                'arg_name': 'driver_uuid',
                                'set_elem_type': 'string',
                            },
                        },
                    },
                },
                'enabled': enabled,
            },
        ],
        default_value={'enabled': True},
    )
