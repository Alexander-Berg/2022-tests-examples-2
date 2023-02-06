import pytest


@pytest.mark.pgsql('heatmap-storage', files=['maps.sql'])
async def test_basic(taxi_heatmap_storage, pgsql, load_binary):

    response = await taxi_heatmap_storage.get('v1/get_map', params={'id': 1})

    assert response.status_code == 200
    assert response.headers['X-YaTaxi-Heatmap-Type'] == 'some_type'
    assert response.headers['X-YaTaxi-Heatmap-Compression'] == 'none'
    assert response.content == b'some_binary_\x00_data'
    assert response.headers['Created'] == '2019-01-02T00:00:00+0000'
    assert response.headers['Expires'] == '2019-01-02T04:00:00+0000'


@pytest.mark.pgsql('heatmap-storage', files=['maps.sql'])
async def test_lz4(taxi_heatmap_storage, pgsql, load_binary):

    response = await taxi_heatmap_storage.get(
        'v1/get_map', params={'id': 1, 'compression': 'lz4'},
    )

    assert response.status_code == 200
    assert response.content[:4] == b'\x12\x00\x00\x00'
    assert response.headers['X-YaTaxi-Heatmap-Type'] == 'some_type'
    assert response.headers['X-YaTaxi-Heatmap-Compression'] == 'lz4'
    assert response.headers['Created'] == '2019-01-02T00:00:00+0000'
    assert response.headers['Expires'] == '2019-01-02T04:00:00+0000'
