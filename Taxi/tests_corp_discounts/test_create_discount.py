async def test_create_discount(taxi_corp_discounts, load_json):
    body = load_json('create_discount.json')
    response = await taxi_corp_discounts.post(
        '/v1/admin/discounts/create', json=body,
    )
    assert response.status == 200
    assert response.json().get('id') == 1


async def test_create_duplicate(taxi_corp_discounts, load_json):
    body = load_json('create_discount.json')
    response = await taxi_corp_discounts.post(
        '/v1/admin/discounts/create', json=body,
    )
    assert response.json().get('id') == 1
    assert response.status == 200
    response = await taxi_corp_discounts.post(
        '/v1/admin/discounts/create', json=body,
    )
    assert response.status == 409


async def test_incorrect_rule_class(taxi_corp_discounts, load_json):
    body = load_json('create_discount.json')
    body['rule']['rule_class'] = 'invalid'
    response = await taxi_corp_discounts.post(
        '/v1/admin/discounts/create', json=body,
    )
    assert response.status == 400
