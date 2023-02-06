from copy import deepcopy
import json

from bson import ObjectId
import pytest

LESSON_ID = '5bca0c9e7bcecff318fef2aa'

OK_REQUEST = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'lesson5_title',
    'icon': 'text',
    'preview_image_url': 'lesson1_img_url_pre',
    'category': 'category',
    'content': [{'type': 'html', 'payload': 'text'}],
    'allowed_territories': {},
    'reactions_enabled': True,
}

OK_DB_ENTRY = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'lesson5_title',
    'icon': 'text',
    'preview_image_url': 'lesson1_img_url_pre',
    'category': 'category',
    'type': 'default_lesson',
    'close_available': True,
    'is_continuous': False,
    'content': [
        {
            'id': 'e72a55f9a177435cf50a5b8996e3b565',
            'type': 'html',
            'payload': 'text',
        },
    ],
    'allowed_territories': {},
    'reactions_enabled': True,
}

OK_STORIES_REQUEST_FILLED_PREVIEW = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'some_story',
    'type': 'stories',
    'icon': 'text',
    'preview_image_url': 'lesson2_img_url_pre',
    'category': 'category',
    'is_continuous': True,
    'content': [
        {
            'type': 'stories',
            'stories_type': 'image_top',
            'timer': 3,
            'block_name': 'name',
            'text': {'title': 'something amazing', 'color': '#FFFFFF'},
            'progress_bar': {
                'filled_color': '#FFFFFF',
                'unfilled_color': '#FFFFFF',
            },
        },
    ],
    'allowed_territories': {},
    'preview': {
        'title': {'text': 'tanker_key', 'color': 'some_hex_color'},
        'background': {'type': 'video', 'value': 'link_or_hex'},
    },
}

OK_STORIES_DB_ENTRY_FILLED_PREVIEW = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'some_story',
    'icon': 'text',
    'preview_image_url': 'lesson2_img_url_pre',
    'category': 'category',
    'type': 'stories',
    'close_available': True,
    'is_continuous': True,
    'content': [
        {
            'id': '6ac61e91d10eb9bf238f7a2e85d735cb',
            'type': 'stories',
            'stories_type': 'image_top',
            'timer': 3,
            'block_name': 'name',
            'text': {'title': 'something amazing', 'color': '#FFFFFF'},
            'progress_bar': {
                'filled_color': '#FFFFFF',
                'unfilled_color': '#FFFFFF',
            },
        },
    ],
    'allowed_territories': {},
    'preview': {
        'title': {'text': 'tanker_key', 'color': 'some_hex_color'},
        'background': {'type': 'video', 'value': 'link_or_hex'},
    },
    'reactions_enabled': None,
}

OK_STORIES_REQUEST_UNFILLED_PREVIEW = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'some_story',
    'type': 'stories',
    'icon': 'text',
    'preview_image_url': 'lesson5_img_url_pre',
    'category': 'category',
    'content': [
        {
            'type': 'stories',
            'stories_type': 'image_top',
            'timer': 3,
            'block_name': 'name',
            'text': {'title': 'something amazing', 'color': '#FFFFFF'},
            'progress_bar': {
                'filled_color': '#FFFFFF',
                'unfilled_color': '#FFFFFF',
            },
        },
    ],
    'allowed_territories': {},
}

OK_STORIES_DB_ENTRY_UNFILLED_PREVIEW = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'some_story',
    'icon': 'text',
    'preview_image_url': 'lesson5_img_url_pre',
    'category': 'category',
    'type': 'stories',
    'close_available': True,
    'is_continuous': False,
    'content': [
        {
            'id': '6ac61e91d10eb9bf238f7a2e85d735cb',
            'type': 'stories',
            'stories_type': 'image_top',
            'timer': 3,
            'block_name': 'name',
            'text': {'title': 'something amazing', 'color': '#FFFFFF'},
            'progress_bar': {
                'filled_color': '#FFFFFF',
                'unfilled_color': '#FFFFFF',
            },
        },
    ],
    'allowed_territories': {},
    'preview': {
        'title': {'text': '', 'color': ''},
        'background': {'value': ''},
    },
    'reactions_enabled': None,
}


async def test_edit_nonexistent_lesson(web_app_client):
    response = await web_app_client.post(
        '/admin/driver-lessons/5bc000999bcecffffff222aa',
        data=json.dumps(OK_REQUEST),
    )
    assert response.status == 404


def _remove_field_and_pack(field_name):
    data = deepcopy(OK_REQUEST)
    data.pop(field_name)
    return json.dumps(data)


def _change_field_type_and_pack(field_name):
    data = deepcopy(OK_REQUEST)
    if isinstance(data[field_name], int):
        data[field_name] = 'now it is string'
    else:
        data[field_name] = 42
    return json.dumps(data)


@pytest.mark.parametrize(
    'missing_field',
    [
        'priority',
        'is_hidden',
        'title',
        'icon',
        'category',
        'content',
        'allowed_territories',
    ],
)
async def test_missing_value(web_app_client, missing_field):
    response = await web_app_client.post(
        '/admin/driver-lessons/' + LESSON_ID,
        data=_remove_field_and_pack(missing_field),
    )
    assert response.status == 400

    response = await web_app_client.post(
        '/admin/driver-lessons/' + LESSON_ID,
        data=_change_field_type_and_pack(missing_field),
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'lesson_request,db_entry',
    [
        (OK_REQUEST, OK_DB_ENTRY),
        (
            OK_STORIES_REQUEST_FILLED_PREVIEW,
            OK_STORIES_DB_ENTRY_FILLED_PREVIEW,
        ),
        (
            OK_STORIES_REQUEST_UNFILLED_PREVIEW,
            OK_STORIES_DB_ENTRY_UNFILLED_PREVIEW,
        ),
    ],
)
async def test_ok_request(web_app_client, mongo, lesson_request, db_entry):
    response = await web_app_client.post(
        '/admin/driver-lessons/' + LESSON_ID, data=json.dumps(lesson_request),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}

    lesson = await mongo.driver_lessons.find_one({'_id': ObjectId(LESSON_ID)})
    assert lesson is not None

    lesson.pop('_id')
    lesson.pop('modified_date')
    lesson.pop('updated_ts')

    assert lesson == db_entry


@pytest.mark.parametrize(
    'content,code',
    [
        ([{'type': 'web_url', 'payload': 't'}], 200),
        (
            [
                {'type': 'text', 'payload': 't'},
                {'type': 'web_url', 'payload': 't'},
            ],
            400,
        ),
    ],
)
async def test_weburl(web_app_client, content, code):
    data = deepcopy(OK_REQUEST)
    data['content'] = content
    response = await web_app_client.post(
        '/admin/driver-lessons', data=json.dumps(data),
    )
    assert response.status == code


@pytest.mark.parametrize(
    'allowed_territories,code',
    [
        ({}, 200),
        ({'rus': {}}, 200),
        (
            {
                'rus': {
                    'mode': 'include',
                    'cities': ['Москва', 'Санкт-Петербург'],
                },
                'blr': {'mode': 'exclude', 'cities': ['Минск', 'Гомель']},
                'fin': {},
            },
            200,
        ),
        ({'rus': {'mode': 'exclude', 'cities': ['Минск', 'Москва']}}, 400),
        ({'rus': {'mode': 'exclude', 'cities': ['Минск', 'Москва']}}, 400),
        ({'x': {}}, 400),
        ({'x': {'mode': 'wrong'}}, 400),
        ({'x': {'mode': 'include'}}, 400),
    ],
)
async def test_allowed_territories(
        web_app_client, mongo, allowed_territories, code,
):
    data = deepcopy(OK_REQUEST)
    data['allowed_territories'] = allowed_territories
    response = await web_app_client.post(
        '/admin/driver-lessons/' + LESSON_ID, data=json.dumps(data),
    )
    assert response.status == code

    if code == 200:
        lesson = await mongo.driver_lessons.find_one(
            {'_id': ObjectId(LESSON_ID)},
        )
        assert lesson['allowed_territories'] == allowed_territories
