import copy

import pytest


PUBLISHED_ID = 'published_promo_on_map_id'
PROMO_ON_MAP_ID = 'stopped_promo_on_map_id'
DEFAULT_JSON = {'promotion_id': PROMO_ON_MAP_ID}


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_archive_ok(web_app_client):
    response = await web_app_client.post(
        'admin/promo_on_map/archive/', json=DEFAULT_JSON,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id={PROMO_ON_MAP_ID}',
    )
    promo_on_map = await response.json()
    assert response.status == 200
    assert promo_on_map['status'] == 'archived'


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_promo_on_map_not_found(web_app_client):
    response = await web_app_client.post(
        'admin/promo_on_map/archive/', json={'promotion_id': 'not_exists'},
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Промо-объект не найден',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_promo_on_map_already_published(web_app_client):
    data = copy.deepcopy(DEFAULT_JSON)
    data['promotion_id'] = PUBLISHED_ID
    response = await web_app_client.post(
        'admin/promo_on_map/archive/', json=data,
    )
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'already_published',
        'message': 'Невозможно архивировать опубликованный промо-объект',
    }
