async def test_version(taxi_heatmap_surge_api, load_binary):
    response = await taxi_heatmap_surge_api.get('version_mapkit')
    assert response.status_code == 200
    assert response.text == '148'
    assert response.headers['Access-Control-Allow-Origin'] == '*'


async def test_version_bad(taxi_heatmap_surge_api, mockserver, load_binary):
    @mockserver.json_handler('/heatmap-renderer/v2/version')
    def _meta_handler(request):
        return mockserver.make_response('', status=404)

    response = await taxi_heatmap_surge_api.get('version_mapkit')
    assert response.status_code == 500
