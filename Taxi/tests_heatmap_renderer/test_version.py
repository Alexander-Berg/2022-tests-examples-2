import pytest


CONTENT_KEY = 'some_content'


@pytest.mark.config(HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY])
async def test_version(taxi_heatmap_renderer, heatmap_storage):
    heatmap_storage.add_map(
        CONTENT_KEY,
        2,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'hex_grid',
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    version_response = await taxi_heatmap_renderer.get(
        '/v2/version?content={}'.format(CONTENT_KEY),
    )

    assert version_response.status_code == 200
    assert version_response.json() == {'version_id': '2'}
    assert version_response.headers['Access-Control-Allow-Origin'] == '*'


async def test_version_404(taxi_heatmap_renderer):
    version_response = await taxi_heatmap_renderer.get(
        '/v2/version?content=wrong_key',
    )
    assert version_response.status_code == 404
    assert version_response.headers['Access-Control-Allow-Origin'] == '*'
