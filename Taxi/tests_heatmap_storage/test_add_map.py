import datetime
import struct

import pytest


def execute_query(query, pgsql):
    pg_cursor = pgsql['heatmap-storage'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


@pytest.mark.parametrize('save_compressed', (True, False))
async def test_add_map(
        taxi_config, taxi_heatmap_storage, pgsql, load_binary, save_compressed,
):
    taxi_config.set(HEATMAP_STORAGE_SAVE_COMPRESSED_MAPS=save_compressed)
    await taxi_heatmap_storage.invalidate_caches()

    data = load_binary('map_content.bin')
    response = await taxi_heatmap_storage.put(
        'v1/insert_map',
        params={'content_key': 'some_content', 'heatmap_type': 'some_type'},
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=data,
    )

    assert response.status_code == 200

    content = execute_query('SELECT * FROM maps.maps', pgsql)

    assert content[0][1] == 'some_content'
    assert content[0][2] == 'some_type'

    if save_compressed:
        size_header = bytes(content[0][3])[:4]
        assert struct.unpack('<I', size_header)[0] == len(data)
        assert content[0][5] == 'lz4'
    else:
        assert bytes(content[0][3]) == data
        assert content[0][5] == 'none'

    # we can't mock time in postgres, so
    # check that it is bigger than test creation time
    assert content[0][4] > datetime.datetime(2019, 10, 9, 0, 0, 0)


@pytest.mark.config(HEATMAP_STORAGE_SAVE_COMPRESSED_MAPS=True)
async def test_add_map_lz4(taxi_heatmap_storage, pgsql, load_binary):
    raw_data = load_binary('map_content.bin')
    data = struct.pack('<I', len(raw_data))
    data += raw_data

    response = await taxi_heatmap_storage.put(
        'v1/insert_map',
        params={
            'content_key': 'some_content',
            'heatmap_type': 'some_type',
            'compression': 'lz4',
        },
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=data,
    )

    assert response.status_code == 200

    content = execute_query('SELECT * FROM maps.maps', pgsql)

    assert content[0][1] == 'some_content'
    assert content[0][2] == 'some_type'
    assert bytes(content[0][3]) == data

    # we can't mock time in postgres, so
    # check that it is bigger than test creation time
    assert content[0][4] > datetime.datetime(2019, 10, 9, 0, 0, 0)
    assert content[0][5] == 'lz4'
