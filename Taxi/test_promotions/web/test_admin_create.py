import copy

import pytest

from promotions.generated.service.swagger import requests
from promotions.generated.service.swagger.models import api as api_module
from promotions.logic import const
from promotions.logic.admin import validation
from promotions.repositories import exceptions


URI = '/admin/promotions/create/'
DEFAULT_DATA = {
    'name': 'test',
    'promotion_type': 'fullscreen',
    'priority': 1,
    'zones': ['moscow', 'abakan'],
    'pages': [],
    'screens': ['main'],
}


async def test_create_already_exists(web_app_client):
    response = await web_app_client.post(URI, json=DEFAULT_DATA)
    data1 = await response.json()
    assert response.status == 201
    assert 'id' in data1

    response = await web_app_client.post(URI, json=DEFAULT_DATA)
    data2 = await response.json()
    assert response.status == 400
    assert data2['code'] == 'already_exists'
    assert data2['message'] == 'Коммуникация с таким названием уже существует'


@pytest.mark.parametrize(
    ['request_response_id'], [('story',), ('deeplink_shortcut',)],
)
async def test_create_storylike_ok(
        web_app_client, request_response_id, load_json,
):
    request_response = load_json('storylike_create_ok.json')
    request_body = request_response[request_response_id]['request']
    expected_response = request_response[request_response_id]['response']

    response = await web_app_client.post(URI, json=request_body)
    response_json = await response.json()
    assert response.status == 201
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    response_json.pop('id')
    response_json.pop('created_at')
    response_json.pop('updated_at')
    assert response_json == expected_response


def _check_validation_failure(data):
    request = requests.AdminCreate(
        {}, None, None, api_module.AdminCreateRequest.deserialize(data),
    )
    try:
        validation.validate_request(request)
    except exceptions.InvalidUrl:
        return True
    return False


def _set_nested_content(data_copy, keys):
    for key in keys[:-1]:
        data_copy = data_copy[key]
    data_copy[keys[-1]] = 'http://'


async def test_content_validation(web_app_client, load_json):
    # We don't want to do a lot of simple and monotonous tests
    field_paths_parametrization = [
        (
            'filled_story_with_invalid_urls.json',
            ['extra_fields', 'preview', 'title', 'content'],
        ),
        (
            'filled_story_with_invalid_urls.json',
            [
                'pages',
                0,
                'widgets',
                'action_buttons',
                0,
                'action',
                'payload',
                'content',
            ],
        ),
        (
            'filled_story_with_invalid_urls.json',
            ['pages', 0, 'widgets', 'link', 'action', 'payload', 'content'],
        ),
        (
            'filled_story_with_invalid_urls.json',
            ['pages', 0, 'widgets', 'switch_button', 'deeplink'],
        ),
        (
            'filled_story_with_invalid_urls.json',
            ['pages', 0, 'widgets', 'arrow_button', 'deeplink'],
        ),
        ('filled_eda_banner_with_invalid_urls.json', ['extra_fields', 'url']),
        (
            'filled_eda_banner_with_invalid_urls.json',
            ['extra_fields', 'app_url'],
        ),
        (
            'filled_eda_banner_with_invalid_urls.json',
            ['pages', 0, 'images', 0, 'url'],
        ),
        (
            'filled_eda_banner_with_invalid_urls.json',
            ['pages', 0, 'shortcuts', 0, 'url'],
        ),
        (
            'filled_eda_banner_with_invalid_urls.json',
            ['pages', 0, 'wide', 0, 'url'],
        ),
    ]
    for (request_template, field_path) in field_paths_parametrization:
        data_copy = load_json(request_template)
        _set_nested_content(data_copy, field_path)
        assert _check_validation_failure(data_copy)


@pytest.mark.parametrize(
    ['pages_data_file', 'error_code', 'error_message'],
    [
        pytest.param(
            'pages_without_close_buttons.json',
            'no_close_button',
            'Виджет close_button обязателен (отсутствует на страницах 1, 3)',
            id='Expect close button in widgets',
        ),
        pytest.param(
            'pages_with_required_fields.json',
            'invalid_page',
            'Ошибка построения страницы: '
            'page фуллскрина не должен иметь поле required',
            id='Unexpect required in FS pages',
        ),
    ],
)
async def test_create_fullscreen_with_invalid_pages(
        web_app_client, load_json, pages_data_file, error_code, error_message,
):
    request = {**DEFAULT_DATA, **load_json(pages_data_file)}

    response = await web_app_client.post(URI, json=request)
    assert response.status == 400
    assert await response.json() == {
        'code': error_code,
        'message': error_message,
    }


async def test_create_story_pages_inconsistency(web_app_client):
    request = {
        **DEFAULT_DATA,
        'pages': [
            {
                'widgets': {
                    'action_buttons': [],
                    'close_button': {'color': 'fefefe'},
                },
            },
            {
                'required': True,
                'widgets': {
                    'action_buttons': [],
                    'close_button': {'color': 'fefefe'},
                },
            },
            {
                'required': True,
                'widgets': {
                    'action_buttons': [],
                    'close_button': {'color': 'fefefe'},
                },
            },
            {
                'required': False,
                'widgets': {
                    'action_buttons': [],
                    'close_button': {'color': 'fefefe'},
                },
            },
        ],
        'extra_fields': {'min_pages_amount': 2},
    }

    response = await web_app_client.post(URI, json=request)
    assert response.status == 400
    assert await response.json() == {
        'code': 'pages_amount_inconsistency',
        'message': (
            'min_pages_amount должен быть не меньше '
            'числа обязательных страниц'
        ),
    }


async def test_create_fullscreen_backward_compatibility(
        web_app_client, load_json,
):
    request = {
        **DEFAULT_DATA,
        'pages': [
            {
                'widgets': {
                    'action_buttons': [
                        {
                            'color': 'fafafa',
                            'text': 'text',
                            'text_color': 'fafafa',
                            'deeplink': 'deeplink',
                        },
                        {
                            'color': 'fafafa',
                            'text': 'text',
                            'text_color': 'fafafa',
                            'action': {
                                'type': 'web_view',
                                'payload': {'content': 'deeplink'},
                            },
                        },
                    ],
                    'close_button': {'color': 'fefefe'},
                },
            },
        ],
    }

    response = await web_app_client.post(URI, json=request)
    assert response.status == 201
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    response_json = await response.json()
    response_json.pop('id')
    response_json.pop('created_at')
    response_json.pop('updated_at')
    assert response_json == load_json('fullscreen_old_deeplink_create_ok.json')


async def test_create_fullscreen_invalid_page(web_app_client):
    request = {
        **DEFAULT_DATA,
        'pages': [
            {
                'widgets': {
                    'action_buttons': [
                        {
                            'color': 'fafafa',
                            'text': 'text',
                            'text_color': 'fafafa',
                            'action': {
                                'type': 'deeplink',
                                'payload': {'page': 8},
                            },
                        },
                    ],
                    'close_button': {'color': 'fefefe'},
                },
            },
        ],
    }

    response = await web_app_client.post(URI, json=request)
    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid_page',
        'message': (
            'Ошибка построения страницы: '
            'payload фуллскрина должен иметь тип ActionPayload'
        ),
    }


async def test_create_empty_screens(web_app_client):
    request = copy.deepcopy(DEFAULT_DATA)
    request['screens'] = []

    response = await web_app_client.post(URI, json=request)
    data = await response.json()
    assert response.status == 400
    assert data['code'] == 'empty_screens'
    assert (
        data['message'] == 'Массив screens для данного типа коммуникаций '
        'должен иметь размер не менее 1'
    )


async def test_create_invalid_url(web_app_client):
    request = copy.deepcopy(DEFAULT_DATA)
    request['promotion_type'] = 'card'
    request['pages'] = [
        {
            'title': {
                'content': '<a href=\\"http://a.ru\\">',
                'color': 'fefefe',
            },
        },
    ]

    response = await web_app_client.post(URI, json=request)
    data = await response.json()
    assert response.status == 400
    assert data['code'] == 'invalid_url'
    assert (
        data['message'] == 'Некорректный url <a href=\\"http://a.ru\\">: '
        'http-ссылка в контенте коммуникации'
    )


async def test_create_deeplink_shortcut_with_overlay(web_app_client):
    payload = {
        **copy.deepcopy(DEFAULT_DATA),
        'extra_fields': {
            'meta_type': 'test_meta_type',
            'overlays': [{'text': 'overlay_value'}],
        },
    }

    response = await web_app_client.post(URI, json=payload)
    assert response.status == 201
    promotion_id = (await response.json())['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['extra_fields'] == payload['extra_fields']


async def test_create_no_meta_type(web_app_client, load_json):
    request = copy.deepcopy(DEFAULT_DATA)
    request['promotion_type'] = 'deeplink_shortcut'
    request['extra_fields'] = {}

    response = await web_app_client.post(URI, json=request)
    data = await response.json()
    assert response.status == 400
    assert data['code'] == 'empty_meta_type'
    assert data['message'] == 'Диплинк-шорткат обязан иметь meta_type'


async def test_create_eda_banner(web_app_client, load_json):
    request_response = load_json('eda_banner_create_ok.json')
    request = request_response['request']
    expected_response = request_response['response']

    response = await web_app_client.post(URI, json=request)
    response_json = await response.json()
    assert response.status == 201
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    response_json.pop('id')
    response_json.pop('created_at')
    response_json.pop('updated_at')
    assert response_json == expected_response


async def test_create_consumers(web_app_client):
    request = copy.deepcopy(DEFAULT_DATA)
    request['consumers'] = ['consumer1', 'consumer2']

    response = await web_app_client.post(URI, json=request)
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['consumers'] == request['consumers']


async def test_create_promo_on_summary(web_app_client, load_json):
    request = {
        'name': 'promo on summary',
        'pages': [
            {
                'icon': {'image_tag': 'achievements_car'},
                'widgets': {
                    'actions_arrow_button': {
                        'color': 'afafaf',
                        'actions': [
                            {
                                'alt_offer': {
                                    'types': ['combo_inner', 'combo_outer'],
                                },
                                'type': 'select_alt_offer',
                            },
                        ],
                        'items': [{'text': 'af', 'type': 'text'}],
                    },
                },
            },
        ],
        'priority': 1,
        'promotion_type': 'promo_on_summary',
        'zones': [],
        'extra_fields': {
            'meta_type': 'promoblock',
            'supported_classes': ['comfort'],
            'show_policy': {
                'max_show_count': 10,
                'max_widget_usage_count': 15,
            },
            'display_on': ['summary', 'totw', 'alt_offer'],
            'configuration': {'type': 'list'},
        },
    }

    response = await web_app_client.post(URI, json=request)
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    response_json.pop('id')
    response_json.pop('created_at')
    response_json.pop('updated_at')
    assert response_json == load_json('promo_on_summary_create_ok.json')


async def test_create_old_stories(web_app_client):
    request = copy.deepcopy(DEFAULT_DATA)
    request['promotion_type'] = 'story'
    request['extra_fields'] = {'meta_type': const.OLD_STORY_META_TYPE_TOTW}

    response = await web_app_client.post(URI, json=request)
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()
    meta_type, story_context = const.OLD_STORY_META_TYPE_TOTW.split('/')
    assert response_json['extra_fields']['meta_type'] == meta_type
    assert response_json['extra_fields']['story_context'] == story_context
    assert response_json['screens'] == [const.SCREENS_NO_SCREEN]
    assert (
        response_json['extra_fields']['preview']['title']['content']
        == const.PREVIEW_DEFAULT_TITLE_CONTENT
    )
    assert (
        response_json['extra_fields']['preview']['title']['color']
        == const.PREVIEW_DEFAULT_TITLE_COLOR
    )


async def test_create_totw_banner(web_app_client, load_json):
    request = load_json('totw_banner_internal.json')

    response = await web_app_client.post(URI, json=request)
    assert response.status == 201
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['status'] == 'created'
    assert not response_json['has_yql_data']

    for prop in [
            'id',
            'created_at',
            'updated_at',
            'has_yql_data',
            'consumers',
            'meta_tags',
            'status',
    ]:
        del response_json[prop]

    assert response_json == request


async def test_totw_banner_pages_validation(web_app_client, load_json):
    request = load_json('totw_banner_internal.json')

    request['pages'] = []

    response = await web_app_client.post(URI, json=request)
    assert response.status == 400
    response_json = await response.json()

    assert response_json == {
        'code': 'pages_amount_inconsistency',
        'message': 'промо-объект должен иметь ровно одну страницу',
    }


async def test_totw_banner_backgrounds_validation(web_app_client, load_json):
    request = load_json('totw_banner_internal.json')

    request['pages'][0]['backgrounds'] = []

    response = await web_app_client.post(URI, json=request)
    assert response.status == 400
    response_json = await response.json()

    assert response_json == {
        'code': 'invalid_page',
        'message': (
            'Ошибка построения страницы: должен быть задан минимум 1 бэкграунд'
        ),
    }


async def test_create_object_over_map(web_app_client, load_json):
    request = load_json('object_over_map_internal.json')

    response = await web_app_client.post(URI, json=request)
    assert response.status == 201
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['status'] == 'created'

    for prop in [
            'id',
            'created_at',
            'updated_at',
            'consumers',
            'meta_tags',
            'status',
            'has_yql_data',
    ]:
        del response_json[prop]

    del request['pages']

    assert response_json == request


async def test_create_grocery_informer(web_app_client, load_json):
    request = load_json('grocery_informer_create_request.json')
    response = await web_app_client.post(URI, json=request)

    assert response.status == 201
    response_json = await response.json()
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['status'] == 'created'

    for prop in [
            'id',
            'created_at',
            'updated_at',
            'consumers',
            'meta_tags',
            'status',
            'has_yql_data',
    ]:
        del response_json[prop]

    assert response_json == request
