import copy

import pytest


DEFAULT_JSON = {'promotion_id': 'id3'}
DEFAULT_EXPERIMENT = {
    'name': 'promotions_test_publish',
    'last_modified_at': 123,
    'clauses': [],
}


@pytest.mark.parametrize(
    'promotion_id', ['id3', 'eda_published', 'grocery_published'],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_unpublish_ok(web_app_client, mockserver, promotion_id):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        if request.method == 'PUT':
            assert request.json == {
                'name': 'promotions_test_publish',
                'last_modified_at': 123,
                'clauses': [
                    {
                        'title': 'default_clause',
                        'value': {'enabled': False},
                        'is_signal': False,
                        'predicate': {'init': {}, 'type': 'true'},
                        'is_paired_signal': False,
                    },
                ],
            }

        resp = copy.deepcopy(DEFAULT_EXPERIMENT)
        resp['clauses'].extend(
            [
                {
                    'title': '+79999999999',
                    'value': {'enabled': True, 'promotions': ['id3']},
                    'predicate': {
                        'type': 'in_set',
                        'init': {
                            'set': ['+79999999999'],
                            'arg_name': 'phone_id',
                            'transform': 'replace_phone_to_phone_id',
                            'phone_type': 'yandex',
                            'set_elem_type': 'string',
                        },
                    },
                },
            ],
        )
        return resp

    request = copy.deepcopy(DEFAULT_JSON)
    request.update({'promotion_id': promotion_id})
    response = await web_app_client.post(
        'admin/promotions/unpublish/', json=request,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={request.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'stopped'


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_unpublish_not_found(web_app_client):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'not_exists'
    response = await web_app_client.post(
        'admin/promotions/unpublish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Коммуникация не найдена',
    }


@pytest.mark.parametrize(
    'promotion_id', ['id4', 'eda_unpublished', 'grocery_unpublished'],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_unpublish_not_published(web_app_client, promotion_id):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = promotion_id
    response = await web_app_client.post(
        'admin/promotions/unpublish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'not_published',
        'message': 'Коммуникация еще не опубликована',
    }


@pytest.mark.parametrize(
    'campaign_label,expected_status,expected_result,promotion_id',
    [
        pytest.param(
            'test_campaign_label_1',
            'published',
            ['test_campaign_label_2'],
            'totw_banner_1',
            id='not_only_campaign',
        ),
        pytest.param(
            'test_campaign_label_3',
            'published',
            [],
            'totw_banner_2',
            id='published_by_experiment_or_yql_link',
        ),
        pytest.param(
            'test_campaign_label_4',
            'stopped',
            [],
            'totw_banner_3',
            id='only_campaign',
        ),
        pytest.param(
            'test_campaign_label_1',
            'stopped',
            [],
            'card_2',
            id='card_by_campaign',
        ),
        pytest.param(
            'test_campaign_label_1',
            'stopped',
            [],
            'notification_3',
            id='notification_by_campaign',
        ),
        pytest.param(
            'test_campaign_label_1',
            'stopped',
            [],
            'grocery_published',
            id='grocery_informer_by_campaign',
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_campaigns.sql'])
async def test_admin_unpublish_by_campaign_label(
        web_app_client,
        campaign_label,
        expected_status,
        expected_result,
        promotion_id,
):
    req_data = {'promotion_id': promotion_id, 'campaign_label': campaign_label}
    response = await web_app_client.post(
        'admin/promotions/unpublish/', json=req_data,
    )
    assert response.status == 200

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={promotion_id}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == expected_status
    assert promotion['extra_fields'] == {'campaign_labels': expected_result}
