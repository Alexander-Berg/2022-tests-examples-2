import pytest


@pytest.mark.servicetest
async def test_reachable_points(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'reachable-points',
        {
            'position': {'lat': 55.73506420531938, 'lon': 37.5783920288086},
            'radius': 1000,
            'mode': 'distance',
            'concaveness': 5.0,
            'length_threshold': 1e-9,
        },
    )
    assert response.status_code == 200

    data = response.json()
    # This test is succeptable to changes in order of edges that NearestEdges
    # return. If this assertion fails, check that NearestEdges() returns
    # array in the same order. If not - if the order is different now and
    # search starts from different edge - then check that handle still works
    # good and change the assertion to new points count.
    assert len(data['points']) == 16

    response = await taxi_yaga_adjust.post(
        'reachable-points',
        {
            'position': {'lat': 55.73506420531938, 'lon': 37.5783920288086},
            'radius': 1000,
            'mode': 'distance',
            'concaveness': 2.0,
            'length_threshold': 1e-9,
        },
    )
    assert response.status_code == 200

    data = response.json()
    # See comment above
    assert len(data['points']) == 25


@pytest.mark.servicetest
async def test_bad_input(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'reachable-points',
        {
            'position': {'lat': 93, 'lon': 25},
            'radius': -100,
            'mode': 'distance',
        },
    )
    assert response.status_code == 400


@pytest.mark.servicetest
async def test_in_the_atlantic_ocean(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'reachable-points',
        {
            'position': {'lat': 47.838349, 'lon': -12.698312},
            'radius': 100,
            'mode': 'time_without_jams',
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert not data['points']
