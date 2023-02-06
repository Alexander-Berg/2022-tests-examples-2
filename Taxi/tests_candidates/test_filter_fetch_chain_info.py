import pytest


def enable_version_experiment(experiments3, enable_chain_combo):
    for exp_name in [
            'combo_outer_taximeter_version',
            'combo_taximeter_version',
    ]:
        experiments3.add_config(
            match={
                'predicate': {'type': 'true'},
                'enabled': True,
                'applications': [
                    {'name': 'taximeter', 'version_range': {'from': '8.0.0'}},
                    {
                        'name': 'taximeter-ios',
                        'version_range': {'from': '1.0.0'},
                    },
                ],
            },
            name=exp_name,
            consumers=['candidates/filters'],
            clauses=[
                {
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                    'enabled': True,
                },
            ],
            default_value={'enabled': False},
        )

    experiments3.add_config(
        name='chain_contractors_for_combo',
        consumers=['candidates/user'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': enable_chain_combo},
    )


@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
@pytest.mark.parametrize('enable_chain_combo', [True, False])
async def test_chain_with_combo(
        taxi_candidates,
        taxi_config,
        driver_positions,
        combo_contractors,
        experiments3,
        chain_busy_drivers,
        enable_chain_combo,
):
    enable_version_experiment(experiments3, enable_chain_combo)

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid2', 'position': [37.63, 55.74]}],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 100,
                'left_distance': 100,
                'destination': [37.64, 55.73],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )

    combo_contractors([{'dbid_uuid': 'dbid0_uuid2'}])

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['uberblack'],
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
    }
    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200
    assert len(response.json()['candidates']) == enable_chain_combo
