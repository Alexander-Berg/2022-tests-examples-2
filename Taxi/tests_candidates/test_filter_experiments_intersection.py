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
@pytest.mark.parametrize('required_experiments', [None, [], ['experiment']])
@pytest.mark.parametrize(
    'metadata',
    [
        _get_metadata(None),
        _get_metadata([]),
        _get_metadata([('experiment', 1)]),
        _get_metadata([('experiment', 2)]),
        _get_metadata([('experiment1', 1)]),
        _get_metadata([('experiment1', 1), ('experiment', 1)]),
    ],
)
async def test_experiments_intersection(
        taxi_candidates, driver_positions, metadata, required_experiments,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['efficiency/experiments_intersection'],
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    if metadata is not None:
        request_body['metadata'] = metadata
    if required_experiments is not None:
        request_body['required_experiments'] = required_experiments
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    intersection = set()
    if metadata:
        metadata_experiments = {
            item['name'] for item in metadata['experiments']
        }
        if required_experiments is not None:
            intersection = metadata_experiments & set(required_experiments)

    experiment = None
    if metadata and 'experiments' in metadata:
        for item in metadata['experiments']:
            if item['name'] == 'experiment':
                experiment = item
                break

    if required_experiments is None or not intersection:
        assert len(drivers) == 3
    elif experiment and experiment['value']['value'] == 2:
        assert len(drivers) == 1
        assert drivers[0]['uuid'] == 'uuid0'
    else:
        assert len(drivers) == 2
        for driver in drivers:
            assert driver['uuid'] != 'uuid0'
