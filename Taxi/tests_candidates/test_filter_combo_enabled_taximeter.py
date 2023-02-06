import pytest

# @pytest.mark.experiments3(filename='combo_taximeter_version.json')
@pytest.mark.parametrize(
    'version,application,expected_candidates',
    [
        ('8.0.0', 'taximeter', ['dbid0_uuid0']),
        ('9.0.0', 'taximeter', []),
        ('8.0.0', 'taximeter-ios', []),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
async def test_filter_combo_enabled_taximeter(
        taxi_candidates,
        driver_positions,
        combo_contractors,
        experiments3,
        version,
        application,
        expected_candidates,
):
    experiments3.add_config(
        match={
            'predicate': {'type': 'true'},
            'enabled': True,
            'applications': [
                {'name': application, 'version_range': {'from': version}},
            ],
        },
        name='combo_taximeter_version',
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

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]}],
    )

    combo_contractors([{'dbid_uuid': 'dbid0_uuid0'}])

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
    }
    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]

    assert candidates == expected_candidates


@pytest.mark.parametrize(
    'version,application,alternative_type,expected_candidates',
    [
        ('8.0.0', 'taximeter-ios', 'combo_outer', ['dbid0_uuid1']),
        ('9.0.0', 'taximeter-ios', 'combo_outer', []),
        ('8.0.0', 'taximeter', 'combo_outer', []),
        ('8.0.0', 'taximeter', '', ['dbid0_uuid1']),
    ],
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
async def test_filter_combo_outer_enabled_taximeter(
        taxi_candidates,
        driver_positions,
        experiments3,
        version,
        application,
        alternative_type,
        expected_candidates,
):
    experiments3.add_config(
        match={
            'predicate': {'type': 'true'},
            'enabled': True,
            'applications': [
                {'name': application, 'version_range': {'from': version}},
            ],
        },
        name='combo_outer_taximeter_version',
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
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]}],
    )

    request_body = {
        'limit': 10,
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
        'point': [37.63, 55.74],
        'destination': [37.64, 55.73],
        'order': {'calc': {'alternative_type': alternative_type}},
    }
    response = await taxi_candidates.post('order-search', json=request_body)

    assert response.status_code == 200

    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]

    assert candidates == expected_candidates
