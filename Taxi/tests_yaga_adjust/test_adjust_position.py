async def test_adjust_position(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'adjust/position',
        {
            'latitude': 55.73506420531938,
            'longitude': 37.5783920288086,
            'max_distance': 100,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data['adjusted']) == 1

    adjusted = data['adjusted'][0]
    assert abs(adjusted['latitude'] - 55.735056) < 0.0001
    assert abs(adjusted['longitude'] - 37.578403) < 0.001
    assert int(adjusted['geo_distance']) == 1


async def test_adjust_position_hard_nopoint(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'adjust/position',
        {'latitude': 55.630785, 'longitude': 37.563727, 'max_distance': 100},
    )
    assert response.status_code == 200

    data = response.json()
    assert not data['adjusted']


async def test_adjust_position_hard(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'adjust/position',
        {'latitude': 55.630785, 'longitude': 37.563727, 'max_distance': 2000},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data['adjusted']) == 1

    adjusted = data['adjusted'][0]
    assert abs(adjusted['latitude'] - 55.634770) < 0.0001
    assert abs(adjusted['longitude'] - 37.543107) < 0.001
    assert int(adjusted['geo_distance']) == 1368


async def test_adjust_position_bad_input(taxi_yaga_adjust):
    response = await taxi_yaga_adjust.post(
        'adjust/position',
        {'latitude': 55.630785, 'longitude': 37.563727, 'max_distance': -1},
    )
    assert response.status_code == 400


async def test_adjust_no_bridge(taxi_yaga_adjust):
    """Target is on the bridge, but bridges are disabled. Thus it will
       be adjusted to some road at a distance
    """
    response = await taxi_yaga_adjust.post(
        'adjust/position',
        # point is right on the Krymskiy Most bridge
        {
            'latitude': 55.734058,
            'longitude': 37.598951,
            'max_distance': 200,
            'roads_struct_filter': {
                'roads': True,
                'tunnels': True,
                'bridges': False,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['adjusted']) == 1
    adjusted = data['adjusted'][0]
    # we can't query edge struct type, but we know that the closed road
    # is approx 50-70m away from the point
    assert abs(adjusted['latitude'] - 55.734058) > 0.0001
    assert abs(adjusted['longitude'] - 37.598951) > 0.001
    assert int(adjusted['geo_distance']) > 50
