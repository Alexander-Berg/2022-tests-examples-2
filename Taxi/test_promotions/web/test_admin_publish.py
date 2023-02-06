import copy

import pytest

from promotions.logic import const
import promotions.logic.utils as utils


DEFAULT_JSON = {
    'promotion_id': 'id4',
    'start_date': '2019-07-22T16:51:09.000042Z',
    'end_date': '2019-07-22T16:51:09.000042Z',
    'experiment': 'pub_exp',
    'ticket': '123',
}


@pytest.mark.parametrize('promotion_id', ['id4', 'eda_unpublished'])
@pytest.mark.now('2020-03-17T09:29:04.667466Z')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_ok(web_app_client, promotion_id):
    request = copy.deepcopy(DEFAULT_JSON)
    request.update({'promotion_id': promotion_id})
    response = await web_app_client.post(
        'admin/promotions/publish/', json=request,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={request["promotion_id"]}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'published'
    assert 'published_at' in promotion
    assert promotion['experiment'] == request['experiment']
    assert promotion['start_date'] == request['start_date']
    assert promotion['end_date'] == request['end_date']
    assert promotion['revision_history'] == [
        {
            'revision': 'some_revision2',
            'created_at': '2019-07-22T16:51:10.000000Z',
        },
        {
            'revision': 'some_revision3',
            'created_at': '2019-07-22T16:51:11.000000Z',
        },
        {
            'revision': 'some_revision4',
            'created_at': '2019-07-22T16:51:12.000000Z',
        },
        {
            'revision': 'some_revision5',
            'created_at': '2019-07-22T16:51:13.000000Z',
        },
        {
            'revision': promotion['revision'],
            'created_at': '2020-03-17T09:29:04.667466Z',
        },
    ]


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_yql_ok(web_app_client):
    yql_link = 'https://localhost/Operations/yql_operation_id'
    json_data = copy.deepcopy(DEFAULT_JSON)
    json_data.pop('experiment')
    json_data['yql_link'] = yql_link

    response = await web_app_client.post(
        'admin/promotions/publish/', json=json_data,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={DEFAULT_JSON.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'publishing'
    assert 'published_at' not in promotion
    assert promotion['start_date'] == DEFAULT_JSON['start_date']
    assert promotion['end_date'] == DEFAULT_JSON['end_date']
    assert promotion['yql_data'] == {'link': yql_link, 'retries': 0}


@pytest.mark.parametrize(
    'promotion_id, result_campaigns',
    [
        pytest.param('id4', ['campaign_12345'], id='publish_new_fullscreen'),
        pytest.param(
            'id1',
            ['campaign_12345'],
            id='add_campaign_to_fs_published_by_experiment',
        ),
        pytest.param(
            'id5',
            ['campaign1', 'campaign_12345'],
            id='add_campaign_to_fs_published_by_campaign_label',
        ),
        pytest.param(
            'id3',
            ['campaign_12345'],
            id='add_campaign_to_card_published_by_experiment',
        ),
        pytest.param(
            'card_2',
            ['campaign1', 'campaign_12345'],
            id='add_campaign_to_card_published_by_campaign_label',
        ),
        pytest.param(
            '6b2ee5529f5b4ffc8fea7008e6913ca6',
            ['campaign_12345'],
            id='publish_notification_by_campaign',
        ),
        pytest.param(
            'notification_3',
            ['campaign1', 'campaign_12345'],
            id='add_campaign_to_notification_published_by_campaign_label',
        ),
        pytest.param(
            'grocery_published',
            ['abc', 'def', 'campaign_12345'],
            id='add_campaign_to_grocery_informer_published_by_campaign_label',
        ),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_crm_publish_by_campaign_label(
        web_app_client, promotion_id, result_campaigns, pgsql,
):
    campaign_label = 'campaign_12345'

    json_data = copy.deepcopy(DEFAULT_JSON)
    json_data.pop('experiment')
    json_data.update({'promotion_id': promotion_id})
    json_data['campaign_label'] = campaign_label

    response = await web_app_client.post(
        'admin/promotions/publish/', json=json_data,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={promotion_id}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'published'

    assert 'extra_fields' in promotion
    assert promotion['extra_fields']['campaign_labels'] == result_campaigns

    # we are not returning campaigns in /admin/promotions/ response now,
    # so we check data directly in db
    cursor = pgsql['promotions'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM promotions.campaigns '
            f'WHERE campaign_label = \'{campaign_label}\''
        ),
    )

    columns = [it.name for it in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor]

    assert rows
    campaign = rows[0]
    assert (
        utils.formatted_datetime(campaign['starts_at'])
        == DEFAULT_JSON['start_date']
    )
    assert (
        utils.formatted_datetime(campaign['ends_at'])
        == DEFAULT_JSON['end_date']
    )

    # publish again and check campaigns are not duplicated
    response = await web_app_client.post(
        'admin/promotions/publish/', json=json_data,
    )
    resp_data = await response.json()
    assert response.status == 200

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={promotion_id}',
    )
    promotion = await response.json()
    assert response.status == 200

    assert 'extra_fields' in promotion
    assert promotion['extra_fields']['campaign_labels'] == result_campaigns


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_exp_and_yql_ok(web_app_client):
    yql_link = 'https://localhost/Operations/yql_operation_id'
    json_data = copy.deepcopy(DEFAULT_JSON)
    json_data['yql_link'] = yql_link

    response = await web_app_client.post(
        'admin/promotions/publish/', json=json_data,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={DEFAULT_JSON.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'publishing'
    assert 'published_at' not in promotion
    assert promotion['start_date'] == DEFAULT_JSON['start_date']
    assert promotion['end_date'] == DEFAULT_JSON['end_date']
    assert promotion['experiment'] == 'pub_exp'
    assert promotion['yql_data'] == {'link': yql_link, 'retries': 0}


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_not_found(web_app_client):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'not_exists'
    response = await web_app_client.post(
        'admin/promotions/publish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Коммуникация не найдена',
    }


@pytest.mark.parametrize('promotion_id', ['id1', 'eda_published'])
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_already_published(web_app_client, promotion_id):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = promotion_id
    response = await web_app_client.post(
        'admin/promotions/publish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'already_published',
        'message': 'Коммуникация уже опубликована',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_old_story_ok(web_app_client):
    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'story_id2'
    req_data['experiment'] = const.OLD_STORY_FAKE_EXP_NAME
    response = await web_app_client.post(
        'admin/promotions/publish/', json=req_data,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={req_data.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['experiment'] == const.OLD_STORY_FAKE_EXP_NAME
    meta_type, story_context = const.OLD_STORY_META_TYPE_TOTW.split('/')
    assert promotion['extra_fields']['meta_type'] == meta_type
    assert promotion['extra_fields']['story_context'] == story_context
    assert promotion['extra_fields']['active'] is True


OLD_STORY_REQUEST_DATA_EXP = copy.deepcopy(DEFAULT_JSON)
OLD_STORY_REQUEST_DATA_EXP['promotion_id'] = 'story_id2'
OLD_STORY_EXP_EXPECTED = {
    'code': 'old_story_wrong_exp',
    'message': 'Для данного типа историй указан неправильный эксперимент',
}

OLD_STORY_REQUEST_DATA_YQL = copy.deepcopy(DEFAULT_JSON)
OLD_STORY_REQUEST_DATA_YQL['promotion_id'] = 'story_id2'
OLD_STORY_REQUEST_DATA_YQL['experiment'] = const.OLD_STORY_FAKE_EXP_NAME
OLD_STORY_REQUEST_DATA_YQL['yql_link'] = 'some_link'
OLD_STORY_YQL_EXPECTED = {
    'code': 'old_story_has_yql_link',
    'message': 'Данный тип историй не может быть опубликован через YQL-ссылку',
}


@pytest.mark.parametrize(
    ['request_data', 'expected_resp'],
    [
        (OLD_STORY_REQUEST_DATA_EXP, OLD_STORY_EXP_EXPECTED),
        (OLD_STORY_REQUEST_DATA_YQL, OLD_STORY_YQL_EXPECTED),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_old_story_err(
        web_app_client, request_data, expected_resp,
):
    response = await web_app_client.post(
        'admin/promotions/publish/', json=request_data,
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == expected_resp


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_test_publication(web_app_client, pgsql):
    request_data = copy.deepcopy(DEFAULT_JSON)
    campaign_label = 'campaign_12345'
    request_data['campaign_label'] = campaign_label
    request_data['is_test_publication'] = True
    response = await web_app_client.post(
        'admin/promotions/publish/', json=request_data,
    )
    assert response.status == 200

    cursor = pgsql['promotions'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM promotions.campaigns '
            f'WHERE campaign_label = \'{campaign_label}\''
        ),
    )

    columns = [it.name for it in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor]

    assert rows
    campaign = rows[0]
    assert campaign['is_test_publication']
