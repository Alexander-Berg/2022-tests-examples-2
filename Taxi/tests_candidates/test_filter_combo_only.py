import pytest


def enable_version_experiment(experiments3):
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


@pytest.mark.parametrize(
    'zone_id, allowed_classes, combo_only_data, expected_candidates',
    [
        (
            'moscow',
            ['econom'],
            {'order': {'calc': {'alternative_type': 'combo_inner'}}},
            [{'dbid_uuid': 'dbid0_uuid2'}],
        ),
        (
            'moscow',
            ['econom'],
            {
                'order': {'calc': {'alternative_type': 'combo_inner'}},
                'combo': {'need_free': True},
            },
            [
                {'dbid_uuid': 'dbid0_uuid0'},
                {'dbid_uuid': 'dbid0_uuid1'},
                {'dbid_uuid': 'dbid0_uuid2'},
            ],
        ),
        (
            'moscow',
            ['econom'],
            {'order': {'calc': {'alternative_type': 'combo_outer'}}},
            [
                {'dbid_uuid': 'dbid0_uuid0'},
                {'dbid_uuid': 'dbid0_uuid1'},
                {'dbid_uuid': 'dbid0_uuid2'},
            ],
        ),
        (
            'moscow',
            ['econom'],
            {},
            [
                {'dbid_uuid': 'dbid0_uuid0'},
                {'dbid_uuid': 'dbid0_uuid1'},
                {'dbid_uuid': 'dbid0_uuid2'},
            ],
        ),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
async def test_combo_only(
        taxi_candidates,
        driver_positions,
        combo_contractors,
        zone_id,
        allowed_classes,
        combo_only_data,
        expected_candidates,
        experiments3,
):
    enable_version_experiment(experiments3)

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.63, 55.74]},
        ],
    )

    combo_contractors([{'dbid_uuid': 'dbid0_uuid2'}])

    request_body = {
        'limit': 10,
        'zone_id': zone_id,
        'allowed_classes': allowed_classes,
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
    }

    request_body.update(combo_only_data)

    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200

    candidates = [
        {'dbid_uuid': candidate['id']}
        for candidate in response.json()['candidates']
    ]

    assert (
        sorted(candidates, key=lambda x: x['dbid_uuid']) == expected_candidates
    )
