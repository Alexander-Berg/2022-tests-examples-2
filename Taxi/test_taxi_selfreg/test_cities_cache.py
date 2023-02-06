async def test_cities_cache(web_app, web_app_client):
    ctx = web_app['context']
    cities_storage = ctx.cities_cache.data
    assert cities_storage.cities
    assert len(cities_storage.cities) == len(cities_storage.by_name)
    # some cities have same region_id
    assert len(cities_storage.cities) > len(cities_storage.by_region_id)

    msk = ctx.cities_cache.get_city('Москва')
    assert msk.name == 'Москва'
    assert msk.geoarea == 'moscow'
    assert msk.region_id == '213'

    msk_oblast = ctx.cities_cache.get_city('Московская область')
    assert msk_oblast.name == 'Московская область'
    assert msk_oblast.geoarea == 'moscow'
    assert msk_oblast.region_id == '213'
