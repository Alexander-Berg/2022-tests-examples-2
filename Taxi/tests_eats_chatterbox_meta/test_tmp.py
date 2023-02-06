async def test_tmp_get(taxi_eats_chatterbox_meta):
    response = await taxi_eats_chatterbox_meta.get('tmp?operation=privet')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.json()['message'] == 'Приветик-пакетик!'


async def test_tmp_get_failed(taxi_eats_chatterbox_meta):
    response = await taxi_eats_chatterbox_meta.get('tmp?operation=unknown')
    assert response.status_code == 400
