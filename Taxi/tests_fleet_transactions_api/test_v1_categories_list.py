ENDPOINT_URL = '/v1/categories/list'


async def test_ok(taxi_fleet_transactions_api, load_json):
    response = await taxi_fleet_transactions_api.post(ENDPOINT_URL, json={})
    categories = load_json('categories.json')

    assert response.status_code == 200, response.text
    assert response.json() == {'categories': categories}


async def test_categories(taxi_fleet_transactions_api, load_json):
    category_ids = ['manual', 'internal']
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json={'category_ids': category_ids},
    )
    categories = load_json('categories.json')

    assert response.status_code == 200, response.text
    assert response.json() == {
        'categories': [
            x for x in categories if x['category_id'] in category_ids
        ],
    }


async def test_groups(taxi_fleet_transactions_api, load_json):
    group_ids = ['platform_other']
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json={'group_ids': group_ids},
    )
    categories = load_json('categories.json')

    assert response.status_code == 200, response.text
    assert response.json() == {
        'categories': [x for x in categories if x['group_id'] in group_ids],
    }


async def test_affecting_driver_balance(
        taxi_fleet_transactions_api, load_json,
):
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json={'is_affecting_driver_balance': True},
    )
    categories = load_json('categories.json')

    assert response.status_code == 200, response.text
    assert response.json() == {
        'categories': [
            x for x in categories if x['is_affecting_driver_balance']
        ],
    }
