import pytest


UNPUBLISH_URL = 'admin/promo_on_map/unpublish/'


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_unpublish_ok(web_app_client):
    req_data = {'promotion_id': 'published_promo_on_map_id'}
    response = await web_app_client.post(UNPUBLISH_URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id=' f'{req_data.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'stopped'


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_unpublish_not_found(web_app_client):
    req_data = {'promotion_id': 'not_exists'}
    response = await web_app_client.post(UNPUBLISH_URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Промо-объект не найден',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_unpublish_not_published(web_app_client):
    req_data = {'promotion_id': 'promo_on_map_id'}
    response = await web_app_client.post(UNPUBLISH_URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'not_published',
        'message': 'Промо-объект еще не опубликован',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_unpublish_by_campaign_ok(web_app_client):
    campaign_label = 'test_campaign_1'
    req_data = {
        'promotion_id': 'published_by_campaign_promo_on_map_id',
        'campaign_label': campaign_label,
    }
    response = await web_app_client.post(UNPUBLISH_URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id=' f'{req_data.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'stopped'
    assert campaign_label not in promotion['campaign_labels']


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_unpublish_partially_by_campaign_ok(web_app_client):
    campaign_label = 'test_campaign_1'
    req_data = {
        'promotion_id': 'published_by_two_campaigns_promo_on_map_id',
        'campaign_label': campaign_label,
    }
    response = await web_app_client.post(UNPUBLISH_URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id=' f'{req_data.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'published'
    assert campaign_label not in promotion['campaign_labels']
