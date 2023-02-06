import copy

import pytest

import tests_superapp_misc.exp3_helpers as exp3

URL = '/4.0/communications/push/settings'

PUSH_SETTINGS_TEMPLATE_EXP = 'push_settings_template'
PUSH_DEFAULT_TAGS_EXP = 'push_default_tags'
CONSUMER = 'communications/push/settings'

DEFAULT_POSITION = [37.5, 55.5]
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_ID = 'user_id_1'
DEFAULT_PHONE_ID = 'phone_id_1'

DEFAULT_TAGS = ['default_tag_1', 'default_tag_2']


def _build_headers(lang):
    return {
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-YaTaxi-UserId': DEFAULT_USER_ID,
        'X-YaTaxi-PhoneId': DEFAULT_PHONE_ID,
        'X-Request-Application': (
            'app_brand=yataxi,app_build=release,app_name=android,'
            'platform_ver1=10,app_ver1=3,app_ver2=161,app_ver3=0'
        ),
        'X-Request-Language': lang,
    }


SECTION_TITLE_KEY = 'section_title_key'
LEAD_TITLE_TEXT_KEY = 'lead_title_text_key'
TRAIL_SUBTITLE_ATTRIBUTED_TEXT_KEY = 'trail_subtitle_attributed_text_key'

CLIENT_MESSAGES = {
    LEAD_TITLE_TEXT_KEY: {
        'ru': 'О новых функциях',
        'en': 'About new functions',
    },
    TRAIL_SUBTITLE_ATTRIBUTED_TEXT_KEY: {'ru': 'ру', 'en': 'en'},
    SECTION_TITLE_KEY: {'ru': 'Секция', 'en': 'Section'},
}


def _create_menu_item(tag):
    return {
        'lead': {'type': 'default', 'title': {'text': LEAD_TITLE_TEXT_KEY}},
        'trail': {
            'type': 'switch',
            'subtitle': {
                'attributed_text': {
                    'items': [
                        {
                            'type': 'text',
                            'text': TRAIL_SUBTITLE_ATTRIBUTED_TEXT_KEY,
                        },
                    ],
                },
            },
        },
        'action': {
            'type': 'setting',
            'content': {'id': tag, 'type': 'push_settings'},
        },
    }


def _create_section(items):
    return {'style': 'default', 'title': SECTION_TITLE_KEY, 'items': items}


def _create_response(sections):
    return {'menu': {'sections': sections}}


def _create_allowed_tags(push_settings, last_received_tags):
    allowed_tags = set(DEFAULT_TAGS)

    if push_settings is not None:
        allowed_tags.update(tag for tag in push_settings['excluded_tags'])
        allowed_tags.update(tag for tag in push_settings['included_tags'])
    if last_received_tags is not None:
        allowed_tags.update(last_received_tags)

    return allowed_tags


def _template_to_response(template, allowed_tags, lang):
    result = copy.deepcopy(template)

    def _filter(response):
        sections = response['menu']['sections']

        for section in sections:
            section['items'] = [
                item
                for item in section['items']
                if item['action']['content']['id'] in allowed_tags
            ]

        response['menu']['sections'] = [
            section for section in sections if section['items']
        ]

    _filter(result)

    def _localize(response):
        def _localize_key(key):
            return CLIENT_MESSAGES[key][lang]

        def _localize_text_template(text_template):
            if 'text' in text_template:
                text_template['text'] = _localize_key(text_template['text'])
            if 'attributed_text' in text_template:
                for item in text_template['attributed_text']['items']:
                    if item['type'] == 'text':
                        item['text'] = _localize_key(item['text'])

        def _localize_menu_item_element(menu_item_element):
            if 'title' in menu_item_element:
                _localize_text_template(menu_item_element['title'])
            if 'subtitle' in menu_item_element:
                _localize_text_template(menu_item_element['subtitle'])

        sections = response['menu']['sections']

        for section in sections:
            if 'title' in section:
                section['title'] = _localize_key(section['title'])
            for menu_item in section['items']:
                _localize_menu_item_element(menu_item['lead'])
                if 'trail' in menu_item:
                    _localize_menu_item_element(menu_item['trail'])

    _localize(result)

    return result


DEFAULT_PUSH_SETTINGS_TEMPLATE = _create_response(
    [
        _create_section(
            [
                _create_menu_item('default_tag_1'),
                _create_menu_item('tag_1'),
                _create_menu_item('unknown_tag_1'),
                _create_menu_item('received_tag_2'),
            ],
        ),
        _create_section(
            [
                _create_menu_item('received_tag_1'),
                _create_menu_item('unknown_tag_2'),
            ],
        ),
        _create_section([_create_menu_item('unknonw_tag_3')]),
    ],
)


def _create_push_settings_template_exp():
    return exp3.create_experiment(
        name=PUSH_SETTINGS_TEMPLATE_EXP,
        consumers=[CONSUMER],
        predicates=[
            exp3.create_eq_predicate('yandex_uid', DEFAULT_YANDEX_UID),
            exp3.create_eq_predicate('user_id', DEFAULT_USER_ID),
            exp3.create_eq_predicate('phone_id', DEFAULT_PHONE_ID),
            exp3.create_eq_predicate('application.brand', 'yataxi'),
            exp3.create_eq_predicate('country', 'RU'),
        ],
        value=DEFAULT_PUSH_SETTINGS_TEMPLATE,
    )


def _create_push_default_tags_exp():
    return exp3.create_experiment(
        name=PUSH_DEFAULT_TAGS_EXP,
        consumers=[CONSUMER],
        predicates=[
            exp3.create_eq_predicate('yandex_uid', DEFAULT_YANDEX_UID),
            exp3.create_eq_predicate('user_id', DEFAULT_USER_ID),
            exp3.create_eq_predicate('zone', 'moscow'),
            exp3.create_eq_predicate('country', 'RU'),
        ],
        value=DEFAULT_TAGS,
    )


def _create_request_json(
        position, push_settings=None, last_received_tags=None,
):
    json = {'position': position}

    if push_settings is not None:
        json['push_settings'] = push_settings
    if last_received_tags is not None:
        json['last_received_tags'] = last_received_tags

    return json


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'push_settings',
    [
        None,
        {
            'enabled_by_system': False,
            'excluded_tags': ['tag1'],
            'included_tags': ['tag2'],
        },
    ],
)
@pytest.mark.parametrize(
    'last_received_tags', [None, ['received_tag_1', 'received_tag_2']],
)
@pytest.mark.parametrize('lang', ['ru', 'en'])
async def test_push_settings(
        taxi_superapp_misc,
        experiments3,
        push_settings,
        last_received_tags,
        lang,
):
    experiments3.add_experiment(**_create_push_settings_template_exp())
    experiments3.add_experiment(**_create_push_default_tags_exp())

    await taxi_superapp_misc.invalidate_caches()

    allowed_tags = _create_allowed_tags(push_settings, last_received_tags)

    response = await taxi_superapp_misc.post(
        URL,
        headers=_build_headers(lang),
        json=_create_request_json(
            DEFAULT_POSITION, push_settings, last_received_tags,
        ),
    )

    assert response.status_code == 200
    assert response.json() == _template_to_response(
        DEFAULT_PUSH_SETTINGS_TEMPLATE, allowed_tags, lang,
    )
