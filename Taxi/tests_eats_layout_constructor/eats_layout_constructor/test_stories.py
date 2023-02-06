import pytest

from . import configs
from . import experiments
from . import utils

LAYOUT_RESPONSE = {
    'data': {
        'stories': [
            {
                'id': '1_stories',
                'template_name': 'any_two_stories_template',
                'payload': {
                    'stories': [
                        {
                            'offer': {
                                'shortcut_id': '',
                                'title': {
                                    'content': 'Story from group a, b, c',
                                    'color': 'bada55',
                                },
                                'backgrounds': [
                                    {
                                        'type': 'image',
                                        'content': 'http://preview_image.png',
                                    },
                                    {'type': 'color', 'content': 'ffffff'},
                                ],
                            },
                            'pages': [
                                {
                                    'duration': 1,
                                    'autonext': False,
                                    'title': {
                                        'content': 'Story 1 Page 1',
                                        'color': '000000',
                                    },
                                    'backgrounds': [
                                        {
                                            'type': 'image',
                                            'content': (
                                                'http://page_1_background.png'
                                            ),
                                        },
                                        {'type': 'color', 'content': 'ffffff'},
                                    ],
                                    'widgets': {
                                        'close_button': {},
                                        'pager': {
                                            'color_on': 'ededed',
                                            'color_off': 'fafafa',
                                        },
                                        'actions_buttons': [
                                            {
                                                'color': 'dbdbdb',
                                                'text': (
                                                    'action button'
                                                    ' web_veiw text'
                                                ),
                                                'text_color': 'dadada',
                                            },
                                            {
                                                'color': 'dbdbdb',
                                                'text': (
                                                    'action button move text'
                                                ),
                                                'text_color': 'dadada',
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                        {
                            'offer': {
                                'shortcut_id': '',
                                'title': {
                                    'content': 'Story from group b, c',
                                    'color': 'bada55',
                                },
                                'backgrounds': [],
                            },
                            'pages': [],
                        },
                    ],
                },
            },
            {
                'id': '2_stories',
                'template_name': 'stories_of_group_a_and_c_template',
                'payload': {
                    'stories': [
                        {
                            'offer': {
                                'shortcut_id': '',
                                'title': {
                                    'content': 'Story from group a, b, c',
                                    'color': 'bada55',
                                },
                                'backgrounds': [
                                    {
                                        'type': 'image',
                                        'content': 'http://preview_image.png',
                                    },
                                    {'type': 'color', 'content': 'ffffff'},
                                ],
                            },
                            'pages': [
                                {
                                    'duration': 1,
                                    'autonext': False,
                                    'title': {
                                        'content': 'Story 1 Page 1',
                                        'color': '000000',
                                    },
                                    'backgrounds': [
                                        {
                                            'type': 'image',
                                            'content': (
                                                'http://page_1_background.png'
                                            ),
                                        },
                                        {'type': 'color', 'content': 'ffffff'},
                                    ],
                                    'widgets': {
                                        'close_button': {},
                                        'pager': {
                                            'color_on': 'ededed',
                                            'color_off': 'fafafa',
                                        },
                                        'actions_buttons': [
                                            {
                                                'color': 'dbdbdb',
                                                'text': (
                                                    'action button'
                                                    ' web_veiw text'
                                                ),
                                                'text_color': 'dadada',
                                            },
                                            {
                                                'color': 'dbdbdb',
                                                'text': (
                                                    'action button move text'
                                                ),
                                                'text_color': 'dadada',
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                        {
                            'offer': {
                                'shortcut_id': '',
                                'title': {
                                    'content': 'Story from group b, c',
                                    'color': 'bada55',
                                },
                                'backgrounds': [],
                            },
                            'pages': [],
                        },
                        {
                            'offer': {
                                'shortcut_id': '',
                                'title': {
                                    'content': 'Story from group a, c',
                                    'color': 'bada55',
                                },
                                'backgrounds': [],
                            },
                            'pages': [],
                        },
                    ],
                },
            },
        ],
    },
    'layout': [
        {
            'id': '1_stories',
            'payload': {'title': 'Any two stories'},
            'type': 'stories',
        },
        {
            'id': '2_stories',
            'payload': {'title': 'Stories of group "a" and "c"'},
            'type': 'stories',
        },
    ],
}


@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('test_place_layout')
@pytest.mark.layout(
    slug='test_place_layout',
    widgets=[
        utils.Widget(
            name='any_two_stories',
            type='stories',
            meta={'limit': 2},
            payload={'title': 'Any two stories'},
            payload_schema={},
        ),
        utils.Widget(
            name='stories_of_group_a_and_c',
            type='stories',
            meta={'groups': ['a', 'c']},
            payload={'title': 'Stories of group "a" and "c"'},
            payload_schema={},
        ),
        utils.Widget(
            name='at_least_two_of_group_b',
            type='stories',
            meta={'groups': ['b'], 'min_count': 2},
            payload={'title': 'At least two stires of group "b"'},
            payload_schema={},
        ),
    ],
)
async def test_layout_stories(
        taxi_eats_layout_constructor, mockserver, load_json,
):
    """Теструет виджет сторизов
    """

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/communications',
    )
    def _communications(request):
        assert request.json == {
            'location': {'latitude': 1.0, 'longitude': 2.0},
            'application': {
                'device_id': 'dev_id',
                'platform': 'android_app',
                'version': '12.11.12',
                'user_id': '12345',
                'screen_resolution': {},
            },
        }
        return load_json('eats_communications_layout_stories_response.json')

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'content-type': 'application/json',
        },
        #  params={},
        json={'location': {'latitude': 1.0, 'longitude': 2.0}},
    )

    assert response.status_code == 200
    assert response.json() == LAYOUT_RESPONSE
