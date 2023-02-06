import pytest


CLUSTERING_WORKER_CONFIG = {
    'enable': True,
    'work_interval_minutes': 3,
    'limit': 1000,
}


@pytest.mark.pgsql('feeds-pg', files=['feeds_geo.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.config(
    FEEDS_GEO_CLUSTERING={
        'neighbors_number': 100,
        'zoom_levels': [
            {
                'zoom_level': 1,
                'distance_threshold_meters': 0.1,
                'choosing_bounds': {'lower': 0, 'upper': 1e18},
            },
        ],
    },
    FEEDS_CLUSTERING_WORKER=CLUSTERING_WORKER_CONFIG,
)
async def test_one_point_in_box(taxi_feeds):
    await taxi_feeds.run_task('distlock/clustering-worker')
    response = await taxi_feeds.post(
        '/v1/fetch_by_geo',
        json={
            'service': 'service',
            'channels': ['user:1', 'user:2'],
            'geo': {
                'bottom_left': {
                    'latitude': 40.74848203263488,
                    'longitude': -111.98594155648394,
                },
                'top_right': {
                    'latitude': 40.776413955797054,
                    'longitude': -111.81228561064376,
                },
                'type': 'box',
            },
        },
    )

    assert response.status_code == 200
    [feed] = response.json()['feed']
    assert feed['location']['meta'] == 2


@pytest.mark.pgsql('feeds-pg', files=['feeds_geo.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.config(
    FEEDS_GEO_CLUSTERING={
        'neighbors_number': 100,
        'zoom_levels': [
            {
                'zoom_level': 1,
                'distance_threshold_meters': 10000,
                'choosing_bounds': {'lower': 0, 'upper': 1e25},
            },
        ],
    },
    FEEDS_CLUSTERING_WORKER=CLUSTERING_WORKER_CONFIG,
)
@pytest.mark.parametrize(
    'channels_with_expected', [(['user:1'], 2), (['user:2'], 1)],
)
async def test_all_points_in_box(taxi_feeds, channels_with_expected):
    await taxi_feeds.run_task('distlock/clustering-worker')
    (channels, expected) = channels_with_expected
    response = await taxi_feeds.post(
        '/v1/fetch_by_geo',
        json={
            'service': 'service',
            'channels': channels,
            'geo': {
                'bottom_left': {'latitude': 40, 'longitude': -112},
                'top_right': {'latitude': 41, 'longitude': -111},
                'type': 'box',
            },
        },
    )
    assert response.status_code == 200
    [feed] = response.json()['feed']
    assert feed['location']['meta'] == expected


@pytest.mark.pgsql('feeds-pg', files=['feeds_geo.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.config(
    FEEDS_GEO_CLUSTERING={
        'neighbors_number': 100,
        'zoom_levels': [
            {
                'zoom_level': 1,
                'distance_threshold_meters': 0,
                'choosing_bounds': {'lower': 30_000, 'upper': 1e18},
            },
            {
                'zoom_level': 2,
                'distance_threshold_meters': 3500,
                'choosing_bounds': {'lower': 10_000, 'upper': 30_000},
            },
            {
                'zoom_level': 3,
                'distance_threshold_meters': 0.1,
                'choosing_bounds': {'lower': 0, 'upper': 10_000},
            },
        ],
    },
    FEEDS_CLUSTERING_WORKER=CLUSTERING_WORKER_CONFIG,
)
@pytest.mark.parametrize(
    'top_right_param',
    [
        (
            {'latitude': 40.77993682071284, 'longitude': -111.8401084677947},
            {1, 2},
        ),
        (
            {'latitude': 40.71570197841644, 'longitude': -111.84859718800995},
            {1},
        ),
        (
            {'latitude': 40.909641597653696, 'longitude': -111.68397392751189},
            {1, 2, 3},
        ),
    ],
)
async def test_different_zoom_levels(taxi_feeds, top_right_param):
    await taxi_feeds.run_task('distlock/clustering-worker')
    top_right, expected_meta = top_right_param
    response = await taxi_feeds.post(
        '/v1/fetch_by_geo',
        json={
            'service': 'service',
            'channels': ['user:1', 'user:2'],
            'geo': {
                'bottom_left': {
                    'latitude': 40.698200479379764,
                    'longitude': -111.95271833107597,
                },
                'top_right': top_right,
                'type': 'box',
            },
        },
    )

    assert response.status_code == 200
    assert {
        i['location']['meta'] for i in response.json()['feed']
    } == expected_meta
