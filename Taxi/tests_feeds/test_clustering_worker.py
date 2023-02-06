import pytest

ZOOM_LEVEL = 1


@pytest.mark.pgsql('feeds-pg', files=['insert_geo_markers.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.config(
    FEEDS_GEO_CLUSTERING={
        'neighbors_number': 100,
        'zoom_levels': [
            {
                'zoom_level': ZOOM_LEVEL,
                'distance_threshold_meters': 10,
                'choosing_bounds': {'lower': 0, 'upper': 1e18},
            },
        ],
    },
    FEEDS_CLUSTERING_WORKER={
        'enable': True,
        'work_interval_minutes': 3,
        'limit': 1000,
    },
)
async def test_clustering_start(taxi_feeds, pgsql):
    await taxi_feeds.run_task('distlock/clustering-worker')
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        f"""SELECT CL.cluster_id,
                   GM.lon,
                   GM.lat
            FROM geo_clusters CL
            INNER JOIN geo_markers GM ON ARRAY[CL.cluster_id] <@ GM.cluster_ids
            WHERE zoom_level = {ZOOM_LEVEL};""",
    )
    geo_markers = list(cursor)

    cursor.execute(f'SELECT marker_id from geo_markers;')
    assert len(geo_markers) == len(list(cursor))
