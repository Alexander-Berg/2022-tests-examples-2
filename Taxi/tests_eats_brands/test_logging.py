MERGED_BRAND = 2


async def test_brands_merging_logging(taxi_eats_brands, testpoint):
    @testpoint('yt-logger-brands-merging')
    def commit(data):
        del data['timestamp']
        assert data == {'actual_id': 1, 'merged_brand': commit.merged_brand}
        commit.merged_brand += 1

    commit.merged_brand = 2

    response = await taxi_eats_brands.post(
        '/brands/v1/create', json={'name': 'kitty-kat'},
    )
    assert response.status_code == 200

    response = await taxi_eats_brands.post(
        '/brands/v1/create', json={'name': 'kitty-dog'},
    )
    assert response.status_code == 200

    response = await taxi_eats_brands.post(
        '/brands/v1/create', json={'name': 'kitty-abracadabra'},
    )
    assert response.status_code == 200

    response = await taxi_eats_brands.post(
        '/brands/v1/merge-brands',
        json={'actual_id': 1, 'ids_to_merge': [2, 3]},
    )
    assert response.status_code == 200

    await commit.wait_call()
