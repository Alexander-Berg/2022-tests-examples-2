# flake8: noqa
# pylint: disable=import-error,wildcard-import


async def test_shop_list_def(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop/list', {'filter': {}},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['name'] == 'Одинокий FBY 5'
    assert response.json()['shops'][4]['name'] == 'Магнит'
    assert response.json()['shops'][9]['name'] == 'КуулКлевер'
    assert len(response.json()['shops']) == 10


async def test_shop_list_page_size(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop/list', {'filter': {}, 'page_size': 5},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['name'] == 'Одинокий FBY 5'
    assert response.json()['shops'][4]['name'] == 'Магнит'
    assert len(response.json()['shops']) == 5


async def test_shop_list_cursor(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop/list', {'filter': {}, 'page_size': 5},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['name'] == 'Одинокий FBY 5'
    assert response.json()['shops'][4]['name'] == 'Магнит'

    response = await taxi_market_shops.post(
        'market-shops/v1/shop/list',
        {'filter': {}, 'cursor': response.json()['cursor'], 'page_size': 5},
    )
    assert response.status_code == 200
    assert (
        response.json()['shops'][0]['name']
        == 'Autotest marketmbi-1316 15.02.2022 13-58-45'
    )
    assert response.json()['shops'][4]['name'] == 'КуулКлевер'

    response = await taxi_market_shops.post(
        'market-shops/v1/shop/list',
        {'filter': {}, 'cursor': response.json()['cursor'], 'page_size': 5},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['name'] == 'Мясницкий ряд'
    assert len(response.json()['shops']) == 1
