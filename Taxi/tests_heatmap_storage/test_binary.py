async def test_add_and_get(taxi_heatmap_storage, load_binary):
    response = await taxi_heatmap_storage.put(
        'v1/insert_map?content_key=some_content&heatmap_type=some_type',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=load_binary('map_content.bin'),
    )

    assert response.status_code == 200
    map_id = response.json()['id']

    response = await taxi_heatmap_storage.get(
        'v1/get_map?id={}'.format(map_id),
    )
    assert response.status_code == 200

    assert response.content == load_binary('map_content.bin')
