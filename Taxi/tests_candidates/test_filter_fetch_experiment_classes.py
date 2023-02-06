import typing

import pytest


def _get_metadata(
        experiments: typing.Optional[typing.List[typing.Tuple[str, int]]],
) -> typing.Optional[dict]:
    if experiments is None:
        return None
    if not experiments:
        return {}
    metadata: dict = {'experiments': []}
    metadata_experiments = metadata.setdefault('experiments', [])
    for name, value in experiments:
        metadata_experiments.append(
            {
                'name': name,
                'value': {'value': value},
                'position': 0,
                'version': 0,
                'is_signal': False,
            },
        )
    return metadata


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'tariff_zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='experiment',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': 'experiment_1',
            'value': {'value': 2},
            'predicate': {
                'init': {
                    'set': ['56f968f07c0aa65c44998e4b'],
                    'arg_name': 'unique_driver_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'not_experiment_1',
            'value': {'value': 1},
            'predicate': {'type': 'true'},
        },
    ],
    default_value=True,
)
@pytest.mark.parametrize(
    'affected_classes', [set(), {'econom'}, {'econom', 'minivan'}],
)
@pytest.mark.parametrize('required_experiments', [None, [], ['experiment']])
@pytest.mark.parametrize(
    'enabled,metadata,filter_experiments',
    [
        (False, _get_metadata(None), []),
        (True, _get_metadata(None), []),
        (True, _get_metadata([]), []),
        (True, _get_metadata([('experiment', 1)]), []),
        (True, _get_metadata([('experiment', 1)]), ['experiment']),
        (True, _get_metadata([('experiment', 2)]), ['experiment']),
        (True, _get_metadata([('experiment1', 1)]), ['experiment']),
        (
            True,
            _get_metadata([('experiment1', 1), ('experiment', 1)]),
            ['experiment'],
        ),
    ],
)
async def test_fetch_experiment_classes(
        taxi_candidates,
        driver_positions,
        taxi_config,
        enabled,
        metadata,
        filter_experiments,
        required_experiments,
        affected_classes,
):
    taxi_config.set_values(
        dict(
            CANDIDATES_FILTER_FETCH_EXPERIMENT_CLASSES={
                '__default__': {},
                'moscow': {
                    'affect': enabled,
                    'classes': list(affected_classes),
                    'experiments': filter_experiments,
                },
                'spb': {
                    'affect': enabled,
                    'classes': ['business'],
                    'experiments': filter_experiments,
                },
            },
        ),
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'allowed_classes': ['econom', 'vip', 'comfort', 'minivan'],
        'geoindex': 'kdtree',
        'limit': 10,
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    if metadata is not None:
        request_body['metadata'] = metadata
    if required_experiments is not None:
        request_body['required_experiments'] = required_experiments
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']

    intersection = set()
    experiments_match = False
    driver_0_classes = {'econom', 'minivan'}
    emptify_classes = affected_classes == driver_0_classes
    if metadata:
        metadata_experiments = {
            item['name'] for item in metadata['experiments']
        }
        intersection = metadata_experiments & set(filter_experiments)

        affecting_experiment = [
            item
            for item in metadata['experiments']
            if item['name'] == 'experiment'
        ]
        if affecting_experiment:
            experiments_match = affecting_experiment[0]['value']['value'] == 2
    filter_disabled = not enabled or required_experiments is not None
    if (
            filter_disabled
            or not intersection
            or not emptify_classes
            or experiments_match
    ):
        assert len(drivers) == 2
        expected_classes = set(driver_0_classes)
        if (
                affected_classes
                and not filter_disabled
                and intersection
                and not emptify_classes
                and not experiments_match
        ):
            expected_classes -= affected_classes
        for driver in drivers:
            assert driver['uuid'] in {'uuid0', 'uuid1'}
            if driver['uuid'] == 'uuid0':
                assert set(driver['classes']) == expected_classes
    else:
        assert len(drivers) == 1
        assert drivers[0]['uuid'] == 'uuid1'
