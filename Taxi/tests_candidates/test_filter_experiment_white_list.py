import typing

import pytest


def _get_metadata(
        experiments: typing.Optional[
            typing.List[typing.Tuple[str, typing.List[str]]]
        ],
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
                'value': {'drivers': value},
                'position': 0,
                'version': 0,
                'is_signal': False,
            },
        )
    return metadata


@pytest.mark.parametrize(
    'metadata, count',
    [
        (_get_metadata(None), 1),
        (_get_metadata([]), 1),
        (_get_metadata([('random_experiment', ['dbid1_uuid1'])]), 1),
        (_get_metadata([('testers_white_list', ['dbid1_uuid1'])]), 0),
        (_get_metadata([('testers_white_list', ['dbid0_uuid0'])]), 1),
        (
            _get_metadata(
                [('testers_white_list', ['dbid0_uuid0', 'dbid1_uuid1'])],
            ),
            1,
        ),
    ],
)
async def test_filter_experiment_white_list(
        taxi_candidates, driver_positions, metadata, count,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 1,
        'filters': ['partners/experiment_white_list'],
        'zone_id': 'moscow',
        'point': [55, 35],
    }
    if metadata is not None:
        request_body['metadata'] = metadata

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json_resp = response.json()

    assert 'drivers' in json_resp
    assert len(json_resp['drivers']) == count
