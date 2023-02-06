import json

import pytest


@pytest.mark.parametrize(
    'test_params',
    [
        {'radius': '3000.0'},
        {'radius': '3000.0', 'concaveness': '1.0', 'length_threshold': '0.01'},
        {'radius': '3000.0', 'concaveness': '0.1', 'length_threshold': '0.01'},
    ],
    ids=[
        'only radius',
        'concaveness and length_threshold provided',
        'concaveness and length_threshold are very low',
    ],
)
async def test_calculate_polygons(taxi_pin_storage, test_params, load_json):
    points = load_json('points.json')

    response = await taxi_pin_storage.post(
        '/v1/calculate-polygons',
        headers={'Content-Type': 'application/json'},
        params=test_params,
        data=json.dumps({'points': points}),
    )

    assert response.status_code == 200
    data = response.json()

    assert 'polygons' in data
    polygons = data['polygons']
    assert len(polygons) > 0

    for polygon in polygons:
        assert 'fixed_point' in polygon
        assert 'vertices' in polygon
        assert 'position' in polygon['fixed_point']
        assert 'position_id' in polygon['fixed_point']


@pytest.mark.parametrize(
    'test_params',
    [{'radius': '1000.0'}, {'radius': '3000.0'}, {'radius': '6000.0'}],
)
async def test_gather_nearest_edges(taxi_pin_storage, test_params, load_json):
    points = load_json('points.json')

    response = await taxi_pin_storage.post(
        '/v1/nearest-edges',
        headers={'Content-Type': 'application/json'},
        params=test_params,
        data=json.dumps({'fixed_points': points}),
    )

    assert response.status_code == 200
    data = response.json()

    assert 'edges' in data
    edges = data['edges']
    assert len(edges) > 0

    for edge in edges:
        assert 'start' in edge
        assert 'end' in edge
        assert 'road_class' in edge
        assert 'nearest_fixed_points' in edge

        points = edge['nearest_fixed_points']
        assert len(points) == 1
        point = points[0]

        assert 'distance' in point
        assert 'position_id' in point
