from copy import deepcopy
import datetime
import json

import bson.timestamp
import pytest


OK_REQUEST = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'lesson5_title',
    'icon': 'text',
    'preview_image_url': 'lesson5_img_url_pre',
    'category': 'category',
    'content': [{'type': 'html', 'payload': 'text'}],
    'allowed_territories': {},
    'preview': {
        'title': {'text': 'preview_tanker_key', 'color': '#FFFFFF'},
        'background': {'type': 'image', 'value': 'https://image.ru'},
    },
    'reactions_enabled': True,
}

OK_ANSWER = {
    'priority': 1,
    'tags': ['newbie'],
    'is_hidden': False,
    'title': 'lesson5_title',
    'icon': 'text',
    'preview_image_url': 'lesson5_img_url_pre',
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
    'preview': {
        'title': {'text': 'preview_tanker_key', 'color': '#FFFFFF'},
        'background': {'type': 'image', 'value': 'https://image.ru'},
    },
    'reactions_enabled': True,
}


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
        '/admin/driver-lessons', data=_remove_field_and_pack(missing_field),
    )
    assert response.status == 400

    response = await web_app_client.post(
        '/admin/driver-lessons',
        data=_change_field_type_and_pack(missing_field),
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'lesson_overrides',
    [
        None,
        {'type': 'webview'},
        {'type': 'stories', 'close_available': False},
        {'type': 'stories', 'is_continuous': True},
        {
            'type': 'stories',
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
        },
    ],
)
async def test_ok_request(web_app_client, web_app, mongo, lesson_overrides):
    data = OK_REQUEST.copy()
    if lesson_overrides:
        data = {**data, **lesson_overrides}

    response = await web_app_client.post(
        '/admin/driver-lessons', data=json.dumps(data),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {}

    lesson = await mongo.driver_lessons.find_one(
        {'title': OK_REQUEST['title']},
    )
    assert lesson is not None
    lesson.pop('_id')
    resulted_timestamp = lesson.pop('updated_ts')
    assert resulted_timestamp is not None
    assert isinstance(resulted_timestamp, bson.timestamp.Timestamp)
    resulted_datetime = lesson.pop('modified_date')
    assert resulted_datetime is not None
    assert isinstance(resulted_datetime, datetime.datetime)

    expected = OK_ANSWER.copy()
    if lesson_overrides:
        expected = {**expected, **lesson_overrides}
    assert lesson == expected


async def test_not_ok_request(web_app_client):
    data = deepcopy(OK_REQUEST)
    data['_id'] = 'a1a1a1a1a1a1a1a1a1a1a1a1'
    response = await web_app_client.post(
        '/admin/driver-lessons', data=json.dumps(data),
    )
    assert response.status == 400


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
async def test_allowed_territories(web_app_client, allowed_territories, code):
    data = deepcopy(OK_REQUEST)
    data['allowed_territories'] = allowed_territories
    response = await web_app_client.post(
        '/admin/driver-lessons', data=json.dumps(data),
    )
    assert response.status == code
