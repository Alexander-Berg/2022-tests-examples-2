async def test_zones(taxi_heatmap_surge_api, load_binary):
    response = await taxi_heatmap_surge_api.get('zones?hash=s0mehash')
    assert response.status_code == 200
    assert response.content == load_binary('zones.bin')
    assert response.headers['Access-Control-Allow-Origin'] == '*'


async def test_empty_zones(taxi_heatmap_surge_api, mockserver):
    @mockserver.handler('/heatmap-renderer/v2/meta')
    def _meta_handler(request):
        return mockserver.make_response(
            status=204, headers={'Access-Control-Allow-Origin': '*'},
        )

    response = await taxi_heatmap_surge_api.get('zones?hash=s0mehash')
    assert response.status_code == 404


async def test_region_id(taxi_heatmap_surge_api, load_binary):
    response = await taxi_heatmap_surge_api.get('region_id?hash=s0mehash')
    assert response.status_code == 200
    assert response.text == '148'
    assert response.headers['Access-Control-Allow-Origin'] == '*'
