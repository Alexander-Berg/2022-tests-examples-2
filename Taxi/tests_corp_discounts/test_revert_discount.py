import pytest


@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_create_link(taxi_corp_discounts, load_json):
    body = load_json('order_1.json')

    # create discount
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    assert response.json()['status'] == 'created'

    # make sure we can't use this discount again
    body = load_json('order_2.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    assert response.json()['status'] == 'rejected'

    # revert order_1
    body = load_json('revert_order_1.json')
    response = await taxi_corp_discounts.post(
        '/v1/discounts/revert', json=body,
    )
    assert response.status == 200

    # make sure we now can use this discount again
    body = load_json('order_2.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    assert response.json()['status'] == 'created'
