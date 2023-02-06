import pytest


@pytest.mark.pgsql('corp_discounts', files=['insert_discounts.sql'])
async def test_create_link(taxi_corp_discounts, load_json):
    body = load_json('create_links.json')
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 200


@pytest.mark.pgsql('corp_discounts', files=['insert_discounts.sql'])
async def test_link_to_frozen_discount(taxi_corp_discounts, load_json):
    body = load_json('create_links.json')
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 200
    body['client_ids'] = ['client_id_4']
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 403


@pytest.mark.pgsql('corp_discounts', files=['insert_discounts.sql'])
async def test_discount_does_not_exist(taxi_corp_discounts, load_json):
    body = load_json('create_links.json')
    body['discount_id'] = 42
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 404


@pytest.mark.pgsql('corp_discounts', files=['insert_discounts.sql'])
async def test_create_conflicting_links(taxi_corp_discounts, load_json):
    body = load_json('create_links.json')
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 200
    body['discount_id'] = 2
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 409
    expected = load_json('conflicts_response.json')
    assert response.json() == expected


@pytest.mark.pgsql('corp_discounts', files=['insert_discounts.sql'])
async def test_concurrent_non_conflicting(taxi_corp_discounts, load_json):
    body = load_json('create_links.json')
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 200
    body['discount_id'] = 3
    response = await taxi_corp_discounts.post(
        '/v1/admin/links/create', json=body,
    )
    assert response.status == 200
