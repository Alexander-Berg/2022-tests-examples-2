import pytest

CONFIG_VALUE = '1.11'

EXPECTED_RESPONSE = {
    'id': '5bca0c9e7bcecff318fef3cc',
    'type': 'stories',
    'title': 'button_or_not_button',
    'icon': 'text',
    'category': 'category',
    'is_new': False,
    'is_completed': False,
    'close_available': True,
    'is_continuous': False,
    'progress': 80,
    'content': [
        {
            'id': '98b24196d27ab22471207e7ea71478fb',
            'type': 'stories',
            'stories_type': 'image_top',
            'timer': 3,
            'progress': 50,
            'text': {'title': 'check_button', 'color': '#FFFFFF'},
            'progress_bar': {
                'filled_color': '#FFFFFF',
                'unfilled_color': '#FFFFFF',
            },
            'buttons': [
                {
                    'title': 'title1',
                    'title_color': '#FFFFFF',
                    'background_color': '#000000',
                    'stroke_color': '#808080',
                    'action': {'url_open_type': 'webview', 'link': 'link1'},
                },
                {
                    'title': 'title2',
                    'title_color': '#FFFFFF',
                    'background_color': '#000000',
                    'stroke_color': '#808080',
                    'action': {
                        'url_open_type': 'screenshare',
                        'link': 'link2',
                    },
                },
            ],
        },
    ],
}


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {},
        'taximeter-ios': {
            'disabled': [],
            'feature_support': {'screenshare_button_in_stories': CONFIG_VALUE},
        },
    },
)
@pytest.mark.parametrize(
    'ios_version',
    [
        pytest.param('1.12', id='greater'),
        pytest.param('1.11', id='equal'),
        pytest.param('0.99', id='less'),
    ],
)
async def test_ios_story_button(web_app_client, ios_version):
    response = await web_app_client.get(
        '/driver/v1/driver-lessons/v1/lessons/5bca0c9e7bcecff318fef3cc',
        headers={
            'X-Request-Application-Version': ios_version,
            'X-Request-Platform': 'ios',
            'Accept-Language': 'ru',
            'X-YaTaxi-Park-Id': 'park',
            'X-YaTaxi-Driver-Profile-Id': 'driver4',
        },
    )
    assert response.status == 200
    content = await response.json()
    if ios_version < CONFIG_VALUE:
        EXPECTED_RESPONSE['content'][0]['buttons'].pop(1)
    assert content == EXPECTED_RESPONSE
