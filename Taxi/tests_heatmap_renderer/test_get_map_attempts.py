import pytest


CONTENT_KEY = 'some_content'


@pytest.mark.parametrize('storage_status_code', [500])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(
    HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY],
    HEATMAP_STORAGE_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
)
async def test_update_on_demand(
        taxi_heatmap_renderer, mockserver, storage_status_code,
):
    @mockserver.handler('/heatmap-storage/v1/get_map')
    def mock_get_map(request):
        return mockserver.make_response(
            response='NOT_FOUND', status=storage_status_code,
        )

    for _ in range(10):
        tile_response = await taxi_heatmap_renderer.get(
            'tile?v=12&x=2476&y=1284&z=12',
        )
        assert tile_response.status_code == storage_status_code

    assert mock_get_map.times_called == 2
