import copy

import pytest


DEFAULT_JSON = {
    'promotion_id': 'promo_on_map_id',
    'start_date': '2019-07-22T19:51:09.000042+03:00',
    'end_date': '2019-07-22T19:51:09.000042+03:00',
    'experiment': 'pub_exp',
}


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_publish_ok(web_app_client):
    response = await web_app_client.post(
        'admin/promo_on_map/publish/', json=DEFAULT_JSON,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id='
        f'{DEFAULT_JSON.get("promotion_id")}',
    )
    promo_on_map = await response.json()
    assert response.status == 200
    assert promo_on_map['status'] == 'published'
    assert 'published_at' in promo_on_map
    assert promo_on_map['start_date'] == DEFAULT_JSON['start_date']
    assert promo_on_map['end_date'] == DEFAULT_JSON['end_date']
    assert promo_on_map['experiment'] == DEFAULT_JSON['experiment']


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_publish_not_found(web_app_client):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'not_exists'
    response = await web_app_client.post(
        'admin/promo_on_map/publish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Промо-объект не найден',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_publish_already_published(web_app_client):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'published_promo_on_map_id'
    response = await web_app_client.post(
        'admin/promo_on_map/publish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'already_published',
        'message': 'Промо-объект уже опубликован',
    }


@pytest.mark.parametrize(
    'promotion_id, campaign_label, result_campaigns, experiment_name',
    [
        pytest.param(
            'promo_on_map_id',
            'test_campaign',
            ['test_campaign'],
            None,
            id='not published',
        ),
        pytest.param(
            'published_promo_on_map_id',
            'test_campaign',
            ['test_campaign'],
            'experiment_name',
            id='published by experiment',
        ),
        pytest.param(
            'published_by_campaign_promo_on_map_id',
            'test_campaign',
            ['test_campaign, test_campaign_1'],
            None,
            id='published by campaign',
        ),
        pytest.param(
            'published_by_campaign_promo_on_map_id',
            'test_campaign_1',
            ['test_campaign_1'],
            None,
            id='publish twice',
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_admin_publish_by_campaign_ok(
        web_app_client,
        promotion_id,
        campaign_label,
        result_campaigns,
        experiment_name,
):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data.pop('experiment')
    campaign_label = 'test_campaign'
    req_data['campaign_label'] = campaign_label
    req_data['promotion_id'] = promotion_id
    response = await web_app_client.post(
        'admin/promo_on_map/publish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id=' f'{req_data.get("promotion_id")}',
    )
    promo_on_map = await response.json()
    assert response.status == 200
    assert promo_on_map['status'] == 'published'
    assert 'published_at' in promo_on_map
    assert promo_on_map['start_date'] == DEFAULT_JSON['start_date']
    assert promo_on_map['end_date'] == DEFAULT_JSON['end_date']
    if experiment_name is None:
        assert 'experiment' not in promo_on_map
    else:
        assert promo_on_map['experiment'] == experiment_name
    assert promo_on_map['campaign_labels'].sort() == result_campaigns.sort()
