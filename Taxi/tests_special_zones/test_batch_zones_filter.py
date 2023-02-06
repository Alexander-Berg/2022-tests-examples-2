import pytest


@pytest.mark.config(
    MODES=[
        {
            'experiment': 'enable_helicopter',
            'mode': 'helicopter',
            'zone_activation': {
                'point_image_tag': 'custom_pp_icons_helicopter',
                'point_title': 'helicopter.pickuppoint_name',
                'zone_type': 'helicopter',
            },
        },
    ],
)
@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'points, results',
    [
        ([], []),
        ([[37.553950, 55.715731]], [{'in_zone': False}]),
        ([[37.547476, 55.726553]], [{'in_zone': True}]),
        ([[37.55295219027704, 55.715765499105544]], [{'in_zone': False}]),
        (
            [[37.553950, 55.715731], [37.552632, 55.719157]],
            [{'in_zone': False}, {'in_zone': True}],
        ),
        (
            [
                [37.577744, 55.715488],
                [37.553950, 55.715731],
                [37.552632, 55.719157],
                [37.564444, 55.722536],
            ],
            [
                {'in_zone': False},
                {'in_zone': False},
                {'in_zone': True},
                {'in_zone': False},
            ],
        ),
        ([[37.47796533823657, 55.86741593065496]], [{'in_zone': False}]),
    ],
)
async def test_filter(points, results, taxi_special_zones):
    response = await taxi_special_zones.post(
        'special-zones/v1/filter', json={'points': points},
    )

    assert response.status_code == 200
    assert results == response.json()['results']


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'points, zone_types, filter_type, results',
    [
        (
            [[37.553950, 55.715731]],
            ['fan_zone'],
            'allowed_zone_types',
            [{'in_zone': False}],
        ),
        (
            [[37.553950, 55.715731]],
            ['bad_zone'],
            'allowed_zone_types',
            [{'in_zone': False}],
        ),
        (
            [[37.547476, 55.726553]],
            ['fan_zone'],
            'allowed_zone_types',
            [{'in_zone': True}],
        ),
        (
            [[37.547476, 55.726553]],
            ['bad_zone'],
            'allowed_zone_types',
            [{'in_zone': False}],
        ),
        (
            [[37.553950, 55.715731]],
            ['fan_zone'],
            'excluded_zone_types',
            [{'in_zone': False}],
        ),
        (
            [[37.553950, 55.715731]],
            ['bad_zone'],
            'excluded_zone_types',
            [{'in_zone': False}],
        ),
        (
            [[37.547476, 55.726553]],
            ['fan_zone'],
            'excluded_zone_types',
            [{'in_zone': False}],
        ),
        (
            [[37.547476, 55.726553]],
            ['bad_zone'],
            'excluded_zone_types',
            [{'in_zone': True}],
        ),
    ],
)
async def test_filter_zone_types(
        points, zone_types, filter_type, results, taxi_special_zones,
):
    response = await taxi_special_zones.post(
        'special-zones/v1/filter',
        json={'points': points, filter_type: zone_types},
    )

    assert response.status_code == 200
    assert results == response.json()['results']


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.parametrize(
    'allowed_ids,in_zone', [([], True), (['unreal_id'], False)],
)
async def test_filter_with_allowed_ids(
        taxi_special_zones, allowed_ids, in_zone,
):
    response = await taxi_special_zones.post(
        'special-zones/v1/filter',
        json={
            'points': [[37.476603, 55.867612], [37.547476, 55.726553]],
            'allowed_ids': allowed_ids,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'results': [{'in_zone': in_zone}, {'in_zone': in_zone}],
    }


@pytest.mark.config(PPAAS_MAX_BATCH_FILTER_POINTS_COUNT=3)
async def test_filter_bad_request(taxi_special_zones):
    response = await taxi_special_zones.post(
        'special-zones/v1/filter', json={},
    )
    assert response.status_code == 400

    response = await taxi_special_zones.post(
        'special-zones/v1/filter',
        json={'points': [[1.0, 2.0]], 'allowed_zone_types': []},
    )
    assert response.status_code == 400

    response = await taxi_special_zones.post(
        'special-zones/v1/filter', json={'points': {}},
    )
    assert response.status_code == 400

    response = await taxi_special_zones.post(
        'special-zones/v1/filter',
        json={'points': [[1.0, 2.0], [1.0, 2.0], [1.0, 2.0]]},
    )
    assert response.status_code == 200

    response = await taxi_special_zones.post(
        'special-zones/v1/filter',
        json={'points': [[1.0, 2.0], [1.0, 2.0], [1.0, 2.0], [1.0, 2.0]]},
    )
    assert response.status_code == 400
