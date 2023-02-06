import pytest


@pytest.mark.experiments3(filename='exp3_deduce_by_category.json')
async def test_map_meta_deduce_content_key_by_category(
        taxi_heatmap_surge_api, driver_authorizer, mockserver,
):
    # Moscow
    position = [37.727063, 55.716563]
    geohash = 'ucfuf'

    park_id = 'park1d'
    session = 'sess10n'
    driver_id = 'dr1ver1d'

    driver_authorizer.set_session(park_id, session, driver_id)

    @mockserver.json_handler('/candidates/profiles')
    def profiles(request):
        return {
            'drivers': [
                {
                    'uuid': driver_id,
                    'dbid': park_id,
                    'position': position,
                    'classes': ['econom', 'business', 'comfortplus'],
                },
            ],
        }

    @mockserver.json_handler('/heatmap-storage/v1/enumerate_keys')
    def _mock_enumerate_keys(request):
        content_type = request.query['content_type']
        if content_type == 'taxi_surge':
            return mockserver.make_response(
                json={
                    'content_keys': [
                        'taxi_surge/__default__/default',
                        'taxi_surge/business/default',
                    ],
                },
            )
        return mockserver.make_response(json={'content_keys': []})

    response = await taxi_heatmap_surge_api.get(
        f'map_meta?hash={geohash}&park_id={park_id}',
        headers={'X-Driver-Session': session},
    )

    assert response.status_code == 200
    assert response.json() == {
        'category': 'business',
        'distribution_id': '148',
        'grid_id': '148',
        'legend': '1.1 - 1.7',
        'legend_measurement_units': 'RUR',
        'legend_max': 1.7,
        'legend_min': 1.1,
        'updated_epoch': 1580724683,
        'updated_str': '2020-02-03T10:11:23+0000',
    }

    assert (await profiles.wait_call())['request'].json == {
        'data_keys': ['classes'],
        'driver_ids': [{'dbid': 'park1d', 'uuid': 'dr1ver1d'}],
        'zone_id': 'moscow',
    }


@pytest.mark.experiments3(filename='exp3_deduce_by_tags.json')
async def test_deduce_content_key_by_tags(
        taxi_heatmap_surge_api, driver_authorizer, mockserver,
):
    geohash = 'ucgtj'

    park_id = 'dbid1'
    session = 'sess10n'
    driver_id = 'uuid1'

    driver_authorizer.set_session(park_id, session, driver_id)

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {
            'dbid': 'dbid1',
            'uuid': 'uuid1',
            'topics': ['surge_heatmap'],
        }
        return {'tags': ['eats_courier']}

    @mockserver.json_handler('/heatmap-storage/v1/enumerate_keys')
    def _mock_enumerate_keys(request):
        content_type = request.query['content_type']
        if content_type == 'taxi_surge':
            return mockserver.make_response(
                json={'content_keys': ['taxi_surge/__default__/default']},
            )
        if content_type == 'eda_surge':
            return mockserver.make_response(
                json={'content_keys': ['eda_surge/default/default']},
            )
        return mockserver.make_response(json={'content_keys': []})

    meta_queries_contents = []

    @mockserver.json_handler('/heatmap-renderer/v2/meta')
    def _meta_handler(request):
        meta_queries_contents.append(request.query['content'])
        return mockserver.make_response(
            json={
                'version_id': '149',
                'legend_min': 1.1,
                'legend_max': 1.2,
                'legend': '1.1 - 1.2',
                'updated_epoch': 1580724683,
            },
            headers={'Access-Control-Allow-Origin': '*'},
        )

    await taxi_heatmap_surge_api.invalidate_caches()
    response = await taxi_heatmap_surge_api.get(
        f'map_meta?hash={geohash}&park_id={park_id}',
        headers={'X-Driver-Session': session},
    )

    assert response.status_code == 200
    assert response.json() == {
        'category': 'default',
        'distribution_id': '149',
        'grid_id': '149',
        'legend': '1.1 - 1.2',
        'legend_max': 1.2,
        'legend_min': 1.1,
        'updated_epoch': 1580724683,
        'updated_str': '2020-02-03T10:11:23+0000',
    }
    assert meta_queries_contents == ['eda_surge/default/default']
