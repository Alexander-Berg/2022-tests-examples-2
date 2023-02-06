NEW_SHORTLINK_JSON = {
    'filter': {
        'city': ['Абакан', 'Абдулино', 'Абинск'],
        'car_class': 'any',
        'daterange_type': 'custom',
        'daterange_start': 1605788912,
        'daterange_end': 1606223865,
        'granularity': '5',
        'wow': '1',
        'metric': ['requests_volume_test_amazanov'],
        'selectedTiles': [],
        'offset_time': False,
        'additional_metrics': {},
        'charts': {
            'requests_volume_test_amazanov': {
                'chartType': 'line',
                'isKalmanFilterApplied': False,
                'Rmult': 0.00005,
                'Q': 1,
                'chartSize': 'S',
                'heatmapTotalCount': 0,
                'heatmapCurrentPage': 0,
                'heatmapShowType': 'current',
                'scatterShowType': ['current'],
                'colorizeScatterType': None,
                'isMapPlaybackControlsShown': False,
                'isFilterPercentile': False,
                'playbackSettings': {
                    'playbackSpeed': 1,
                    'isPlaying': False,
                    'currentFrame': None,
                    'isRecording': False,
                },
                'heatmapSettings': {
                    'min': {'value': 0.05, 'color': '#00ff00'},
                    'middle': {'value': 0.5, 'color': '#ffff00'},
                    'max': {'value': 0.95, 'color': '#ff0000'},
                    'common': {'opacity': 0.5, 'type': 'percentile'},
                },
            },
        },
    },
    'heatmapFilters': {
        'heatmapPrimaryFilterSettings': {'min': None, 'max': None},
        'heatmapSecondaryFilterSettings': {'min': None, 'max': None},
    },
    'heatmapParams': {
        'metrics': ['requests_volume_test_amazanov'],
        'date_from': 1606165200,
    },
    'commonSettings': {
        'chartSize': 'S',
        'isShowMap': True,
        'isRoundedToHours': False,
        'minutesStashStart': None,
        'minutesStashEnd': None,
        'isRoundedToDays': False,
        'hoursStashStart': None,
        'hoursStashEnd': None,
    },
    'user': 'shedx',
    'name': 'test_link_name',
    'db': 'pixel',
}


async def test_create_preset(web_app_client, db):
    response = await web_app_client.post(
        '/api/short/test_link_name/', json=NEW_SHORTLINK_JSON,
    )
    assert response.status == 200

    preset = await db.atlas_links.find_one(
        {'link_name': 'test_link_name'}, ['_id'],
    )
    data = await response.json()
    assert str(preset['_id']) == data['_id']


async def test_update_preset(web_app_client, db):
    response = await web_app_client.post(
        '/api/short/test_link_name/', json=NEW_SHORTLINK_JSON,
    )
    assert response.status == 200
    response = await web_app_client.post(
        '/api/short/test_link_name/update',
        json={'filter': {'new_filters': []}},
    )
    assert response.status == 200

    preset = await db.atlas_links.find_one({'link_name': 'test_link_name'})
    data = await response.json()
    assert str(preset['_id']) == data['_id']
    assert preset['filter'] == {'new_filters': []}


async def test_get_shortlink(web_app_client):
    response = await web_app_client.post(
        '/api/short/test_link_name/', json=NEW_SHORTLINK_JSON,
    )
    assert response.status == 200

    response = await web_app_client.get('/api/short/test_link_name/')
    assert response.status == 200

    data = await response.json()
    data.pop('link_name')
    assert data == NEW_SHORTLINK_JSON
