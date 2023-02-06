from aiohttp import ClientResponse
import pytest


async def test_lessons_updates__no_params(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons/updates', json={},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'priority': 1,
                'is_hidden': False,
                'title': 'lesson1_title',
                'icon': 'text',
                'tags': ['newbie', 'newbie2'],
                'category': 'lesson1_category',
                'content': [
                    {
                        'type': 'html',
                        'payload': 'lesson1_text1',
                        'id': '1bc8930f92ccd39525390d7be11eefe4',
                    },
                    {
                        'type': 'image',
                        'payload': 'lesson1_img_url1',
                        'id': 'b3cba4b41f5acec18073b1bb856c3934',
                    },
                    {
                        'type': 'video',
                        'payload': 'lesson1_youtube_url1',
                        'id': '580c4dee3a23c9397f13ceaca5fe3beb',
                    },
                    {
                        'type': 'markdown',
                        'payload': 'lesson1_text2',
                        'id': '1ef7c0a082457f4b9af16bbd184ac516',
                    },
                ],
                'modified_date': '2017-06-29T13:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2bb',
                'priority': 2,
                'is_hidden': False,
                'title': 'lesson2_title',
                'icon': 'text',
                'tags': [],
                'preview_image_url': 'lesson2_img_url_pre',
                'category': 'lesson2_category',
                'content': [
                    {'type': 'html', 'payload': 'lesson2_text1', 'id': '1'},
                    {
                        'type': 'image',
                        'payload': 'lesson2_img_url1',
                        'id': '2',
                    },
                    {
                        'type': 'video',
                        'payload': 'lesson2_youtube_url1',
                        'id': '3',
                    },
                    {
                        'type': 'markdown',
                        'payload': 'lesson2_text2',
                        'id': '4',
                    },
                ],
                'modified_date': '2017-06-29T14:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2cc',
                'priority': 3,
                'is_hidden': True,
                'title': 'lesson3_title',
                'icon': 'false',
                'tags': [],
                'preview_image_url': 'lesson3_img_url_pre',
                'category': 'lesson3_category',
                'content': [
                    {'type': 'html', 'payload': 'lesson3_text1', 'id': '5'},
                    {
                        'type': 'image',
                        'payload': 'lesson3_img_url1',
                        'id': '6',
                    },
                    {
                        'type': 'video',
                        'payload': 'lesson3_youtube_url1',
                        'id': '7',
                    },
                    {
                        'type': 'markdown',
                        'payload': 'lesson3_text2',
                        'id': '8',
                    },
                ],
                'modified_date': '2017-06-29T15:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef3cc',
                'priority': 3,
                'is_hidden': True,
                'title': 'lesson3_title',
                'icon': 'false',
                'tags': [],
                'preview_image_url': 'lesson3_img_url_pre',
                'category': 'lesson3_category',
                'content': [
                    {'type': 'html', 'payload': 'lesson3_text1', 'id': '5'},
                    {
                        'type': 'image',
                        'payload': 'lesson3_img_url1',
                        'id': '6',
                    },
                    {
                        'type': 'video',
                        'payload': 'lesson3_youtube_url1',
                        'id': '7',
                    },
                    {
                        'type': 'markdown',
                        'payload': 'lesson3_text2',
                        'id': '8',
                    },
                    {
                        'type': 'stories',
                        'stories_type': 'image_top',
                        'timer': 3,
                        'id': '99e400302c0a0fe401b22ff152dc8fc2',
                        'text': {
                            'title': 'something amazing',
                            'color': '#FFFFFF',
                        },
                        'block_name': 'name',
                    },
                ],
                'modified_date': '2017-06-29T16:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
                'type': 'stories',
                'close_available': False,
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef3cf',
                'priority': 3,
                'is_hidden': True,
                'title': 'lesson3_title',
                'icon': 'false',
                'tags': [],
                'preview_image_url': 'lesson3_img_url_pre',
                'category': 'lesson3_category',
                'content': [],
                'modified_date': '2017-06-29T17:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
                'type': 'stories',
                'close_available': False,
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2dd',
                'priority': 1,
                'is_hidden': False,
                'title': 'lesson1_title',
                'icon': 'text',
                'tags': [],
                'category': 'lesson1_category',
                'content': [
                    {
                        'type': 'stories',
                        'stories_type': 'image_top',
                        'timer': 3,
                        'id': '99e400302c0a0fe401b22ff152dc8fc2',
                        'text': {
                            'title': 'something amazing',
                            'color': '#FFFFFF',
                        },
                        'block_name': 'name',
                    },
                ],
                'modified_date': '2017-06-29T18:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
                'type': 'stories',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2ee',
                'priority': 1,
                'is_hidden': False,
                'title': 'lesson1_title',
                'icon': 'text',
                'tags': [],
                'category': 'lesson1_category',
                'content': [
                    {
                        'type': 'stories',
                        'stories_type': 'image_bottom',
                        'timer': 3,
                        'id': '99e400302c0a0fe401b22ff152dc8fc2',
                        'text': {
                            'title': 'something amazing',
                            'color': '#000000',
                        },
                    },
                ],
                'modified_date': '2017-06-29T19:39:27.367000+03:00',
                'allowed_territories': {
                    'rus': {'cities': ['Москва'], 'mode': 'include'},
                },
                'type': 'stories',
            },
        ],
        'revision': '1498754367_367',
    }


async def test_lessons_updates__with_limit_and_projection(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons/updates',
        json={
            'limit': 1,
            'projection': [
                'is_hidden',
                'title',
                'icon',
                'tags',
                'modified_date',
            ],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'is_hidden': False,
                'title': 'lesson1_title',
                'icon': 'text',
                'tags': ['newbie', 'newbie2'],
                'modified_date': '2017-06-29T13:39:27.367000+03:00',
            },
        ],
        'revision': '1498732767_367',
    }


async def test_lessons_updates__with_revision_and_projection(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons/updates',
        json={
            'last_known_revision': '1498747100_0',
            'projection': ['title', 'modified_date', 'content'],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef3cf',
                'title': 'lesson3_title',
                'content': [],
                'modified_date': '2017-06-29T17:39:27.367000+03:00',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2dd',
                'title': 'lesson1_title',
                'content': [
                    {
                        'type': 'stories',
                        'stories_type': 'image_top',
                        'timer': 3,
                        'id': '99e400302c0a0fe401b22ff152dc8fc2',
                        'text': {
                            'title': 'something amazing',
                            'color': '#FFFFFF',
                        },
                        'block_name': 'name',
                    },
                ],
                'modified_date': '2017-06-29T18:39:27.367000+03:00',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2ee',
                'title': 'lesson1_title',
                'content': [
                    {
                        'type': 'stories',
                        'stories_type': 'image_bottom',
                        'timer': 3,
                        'id': '99e400302c0a0fe401b22ff152dc8fc2',
                        'text': {
                            'title': 'something amazing',
                            'color': '#000000',
                        },
                    },
                ],
                'modified_date': '2017-06-29T19:39:27.367000+03:00',
            },
        ],
        'revision': '1498754367_367',
    }


async def test_lessons_updates__with_revision__nothing_found(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons/updates',
        json={'last_known_revision': '1498754400_000'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'lessons': [], 'revision': '1498754400_000'}


@pytest.mark.config(LESSONS_LIMIT_FOR_UPDATES_INTERNAL_API=2)
async def test_lessons_updates__limit_exceed_allowed__restrict(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons/updates',
        json={'limit': 5, 'projection': ['title']},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'title': 'lesson1_title',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2bb',
                'title': 'lesson2_title',
            },
        ],
        'revision': '1498736367_367',
    }


@pytest.mark.filldb(driver_lessons='empty')
async def test_lessons_updates__no_revision__nothing_found(
        mongodb, web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons/updates', json={},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'lessons': []}
