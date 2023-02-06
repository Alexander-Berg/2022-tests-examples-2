import copy

import pytest

from promotions.logic import const


PUBLISHED_PROMOTION_ID = 'id1'
UNPUBLISHED_PROMOTION_ID = 'id4'
UNPUBLISHED_STORY_ID = 'story_id1'
UNPUBLISHED_EDA_BANNER_ID = 'eda_unpublished'
DEFAULT_JSON = {
    'name': 'new name 4',
    'promotion_type': 'card',
    'screens': ['title'],
    'priority': 10,
    'zones': ['spb'],
    'pages': [{'widgets': {'action_buttons': []}}],
}


@pytest.mark.parametrize(
    'promotion_id', [UNPUBLISHED_PROMOTION_ID, UNPUBLISHED_EDA_BANNER_ID],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_edit_ok(web_app_client, promotion_id):
    response = await web_app_client.put(
        f'admin/promotions/{promotion_id}/', json=DEFAULT_JSON,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={promotion_id}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['name'] == DEFAULT_JSON['name']
    assert promotion['promotion_type'] == DEFAULT_JSON['promotion_type']
    assert promotion['screens'] == DEFAULT_JSON['screens']
    assert promotion['priority'] == DEFAULT_JSON['priority']
    assert promotion['zones'] == DEFAULT_JSON['zones']
    assert promotion['pages'] == DEFAULT_JSON['pages']


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_compat.sql'])
async def test_compatibility_ok(web_app_client, load_json):
    promotion_id = 'e7deaabe0e0b4c9f8a86e19a6da4db59'
    payload = load_json('compat_request.json')

    response = await web_app_client.put(
        f'admin/promotions/{promotion_id}/', json=payload,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={promotion_id}',
    )
    promotion = await response.json()
    assert response.status == 200
    promotion.pop('updated_at')
    assert promotion == load_json('compat_response.json')


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_name_already_exists(web_app_client):
    data = copy.deepcopy(DEFAULT_JSON)
    data['name'] = 'banner 1'
    response = await web_app_client.put(
        f'admin/promotions/{UNPUBLISHED_PROMOTION_ID}/', json=data,
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'already_exists',
        'message': 'Коммуникация с таким названием уже существует',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_promotion_not_found(web_app_client):
    response = await web_app_client.put(
        f'admin/promotions/not_exists/', json=DEFAULT_JSON,
    )
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Коммуникация не найдена',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_promotion_already_published(web_app_client):
    response = await web_app_client.put(
        f'admin/promotions/{PUBLISHED_PROMOTION_ID}/', json=DEFAULT_JSON,
    )
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'edit_error',
        'message': 'Нельзя редактировать опубликованные коммуникации',
    }


@pytest.mark.parametrize(
    'expected_code, add_close_widget', [(200, True), (400, False)],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_edit_stories(web_app_client, expected_code, add_close_widget):
    payload = copy.deepcopy(DEFAULT_JSON)
    payload['promotion_type'] = 'story'
    payload['consumers'] = ['consumer1', 'consumer2']
    payload['meta_tags'] = ['tag1', 'tag2', 'tag3']
    payload['extra_fields'] = {'overlays': [{'text': 'new_overlay_value'}]}
    payload['pages'][0].update({'layout': {'id': 'new_layout_id'}})
    if add_close_widget:
        payload['pages'][0]['widgets'].update(
            {'close_button': {'color': 'fefefe'}},
        )
    response = await web_app_client.put(
        f'admin/promotions/{UNPUBLISHED_STORY_ID}/', json=payload,
    )
    resp_data = await response.json()
    assert response.status == expected_code
    if expected_code == 400:
        assert resp_data['code'] == 'no_close_button'
        return

    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={UNPUBLISHED_STORY_ID}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['name'] == payload['name']
    assert promotion['promotion_type'] == payload['promotion_type']
    assert promotion['screens'] == payload['screens']
    assert promotion['priority'] == payload['priority']
    assert promotion['zones'] == payload['zones']
    assert promotion['consumers'] == payload['consumers']
    assert promotion['meta_tags'] == payload['meta_tags']
    assert promotion['extra_fields'] == payload['extra_fields']
    assert promotion['pages'] == payload['pages']


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_edit_invalid_url(web_app_client):
    payload = copy.deepcopy(DEFAULT_JSON)
    payload['pages'] = [
        {
            'title': {
                'content': '<a href=\\"http://a.ru\\">',
                'color': 'fefefe',
            },
        },
    ]

    response = await web_app_client.put(
        f'admin/promotions/{UNPUBLISHED_PROMOTION_ID}/', json=payload,
    )
    data = await response.json()
    assert response.status == 400
    assert data['code'] == 'invalid_url'
    assert (
        data['message'] == 'Некорректный url <a href=\\"http://a.ru\\">: '
        'http-ссылка в контенте коммуникации'
    )


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_edit_make_old_story_ok(web_app_client):
    payload = DEFAULT_JSON.copy()
    payload['promotion_type'] = 'story'
    payload['extra_fields'] = {'meta_type': const.OLD_STORY_META_TYPE_TOTW}
    payload['pages'][0]['widgets'].update(
        {'close_button': {'color': 'fefefe'}},
    )
    response = await web_app_client.put(
        f'admin/promotions/{UNPUBLISHED_PROMOTION_ID}/', json=payload,
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={UNPUBLISHED_PROMOTION_ID}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['name'] == payload['name']
    assert promotion['promotion_type'] == payload['promotion_type']
    assert promotion['screens'] == [const.SCREENS_NO_SCREEN]
    meta_type, story_context = const.OLD_STORY_META_TYPE_TOTW.split('/')
    assert promotion['extra_fields']['meta_type'] == meta_type
    assert promotion['extra_fields']['story_context'] == story_context


async def test_edit_totw_banner(web_app_client, load_json):
    def check_totw_banner(request, view_response_json):
        assert view_response_json['status'] == 'created'
        assert not view_response_json['has_yql_data']

        view_response_json = copy.deepcopy(view_response_json)

        for prop in [
                'id',
                'created_at',
                'updated_at',
                'has_yql_data',
                'consumers',
                'meta_tags',
                'status',
        ]:
            del view_response_json[prop]

        assert view_response_json == request

    create_request = load_json('totw_banner_internal.json')

    create_response = await web_app_client.post(
        '/admin/promotions/create/', json=create_request,
    )
    assert create_response.status == 201
    create_response_json = await create_response.json()
    promotion_id = create_response_json['id']

    view_response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert view_response.status == 200
    view_response_json = await view_response.json()

    check_totw_banner(create_request, view_response_json)

    edit_request = load_json('totw_banner_internal_edit.json')

    edit_response = await web_app_client.put(
        f'admin/promotions/{promotion_id}/', json=edit_request,
    )
    edit_response_json = await edit_response.json()
    assert edit_response.status == 200
    assert edit_response_json == {}

    view_response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert view_response.status == 200
    view_response_json = await view_response.json()

    check_totw_banner(edit_request, view_response_json)


async def test_edit_object_over_map(web_app_client, load_json):
    def check_object_over_map(request, view_response_json):
        request = copy.deepcopy(request)
        view_response_json = copy.deepcopy(view_response_json)

        assert view_response_json['status'] == 'created'

        for prop in [
                'id',
                'created_at',
                'updated_at',
                'consumers',
                'meta_tags',
                'status',
                'has_yql_data',
        ]:
            del view_response_json[prop]

        del request['pages']

        assert view_response_json == request

    create_request = load_json('object_over_map_internal.json')

    create_response = await web_app_client.post(
        '/admin/promotions/create/', json=create_request,
    )
    assert create_response.status == 201
    create_response_json = await create_response.json()
    promotion_id = create_response_json['id']

    view_response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert view_response.status == 200
    view_response_json = await view_response.json()

    check_object_over_map(create_request, view_response_json)

    edit_request = load_json('object_over_map_internal_edit.json')

    edit_response = await web_app_client.put(
        f'admin/promotions/{promotion_id}/', json=edit_request,
    )
    edit_response_json = await edit_response.json()
    assert edit_response.status == 200
    assert edit_response_json == {}

    view_response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert view_response.status == 200
    view_response_json = await view_response.json()

    check_object_over_map(edit_request, view_response_json)
