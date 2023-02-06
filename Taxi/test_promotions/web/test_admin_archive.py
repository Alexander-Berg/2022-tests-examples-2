import copy

import pytest


PUBLISHED_ID = 'id1'
PROMOTION_ID = '6b2ee5529f5b4ffc8fea7008e6913ca6'
DEFAULT_JSON = {'promotion_id': PROMOTION_ID}


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_archive_ok(web_app_client):
    response = await web_app_client.post(
        'admin/promotions/archive/', json=DEFAULT_JSON,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={PROMOTION_ID}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'archived'


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_promotion_not_found(web_app_client):
    response = await web_app_client.post(
        'admin/promotions/archive/', json={'promotion_id': 'not_exists'},
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Коммуникация не найдена',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_promotion_already_published(web_app_client):
    data = copy.deepcopy(DEFAULT_JSON)
    data['promotion_id'] = PUBLISHED_ID
    response = await web_app_client.post(
        'admin/promotions/archive/', json=data,
    )
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'already_published',
        'message': ('Невозможно архивировать опубликованную ' 'коммуникацию'),
    }
