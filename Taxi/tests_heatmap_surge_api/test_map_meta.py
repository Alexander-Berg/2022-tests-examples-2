def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


async def test_map_meta(taxi_heatmap_surge_api):
    response = await taxi_heatmap_surge_api.get('map_meta?hash=s0mehash')
    assert response.status_code == 200
    assert response.json() == {
        'category': '__default__',
        'distribution_id': '148',
        'grid_id': '148',
        'legend': '1.1 - 1.7',
        'legend_measurement_units': 'RUR',
        'legend_max': 1.7,
        'legend_min': 1.1,
        'updated_epoch': 1580724683,
        'updated_str': '2020-02-03T10:11:23+0000',
    }
    assert response.headers['Access-Control-Allow-Origin'] == '*'
    check_polling_header(response.headers['X-Polling-Power-Policy'])


async def test_map_meta_204(taxi_heatmap_surge_api, mockserver):
    @mockserver.handler('/heatmap-renderer/v2/meta')
    def _meta_handler(request):
        return mockserver.make_response(
            status=204, headers={'Access-Control-Allow-Origin': '*'},
        )

    response = await taxi_heatmap_surge_api.get('map_meta?hash=s0mehash')
    assert response.status_code == 204


async def test_map_meta_400(taxi_heatmap_surge_api):
    response = await taxi_heatmap_surge_api.get('map_meta')
    assert response.status_code == 400
