DEFAULT_TOTW_PROMOTIONS_EXP_NAME = 'totw_promotions_exp'

DEFAULT_BUTTON_TITLE_KEY = 'promo_story.button_title'
DEFAULT_TOTW_BANNER_TITLE_KEY = 'totw_banner.title'
DEFAULT_TOTW_PROMOBLOCK_TITLE_KEY = 'totw_family_share_promoblock.title'
DEFAULT_TOTW_PROMOBLOCK_TEXT_KEY = 'totw_family_share_promoblock.text'
DEFAULT_TOTW_PROMOBLOCK_ALT_WAITING_TEXT_KEY = (
    'totw_promoblock_alt_waiting.text'
)
DEFAULT_TOTW_PROMOBLOCK_ALT_WAITING_TITLE_KEY = (
    'totw_promoblock_alt_waiting.title'
)

DEFAULT_CLIENT_MESSAGES = {
    DEFAULT_BUTTON_TITLE_KEY: {'ru': 'Узнать больше', 'en': 'Find out more'},
}
DEFAULT_BACKEND_PROMOTIONS = {
    DEFAULT_TOTW_BANNER_TITLE_KEY: {
        'ru': 'Заголовок баннера',
        'en': 'Banner title',
    },
    DEFAULT_TOTW_PROMOBLOCK_TITLE_KEY: {
        'ru': 'Заголовок промоблока',
        'en': 'Promoblock title',
    },
    DEFAULT_TOTW_PROMOBLOCK_TEXT_KEY: {
        'ru': 'Текст промоблока',
        'en': 'Promoblock text',
    },
    DEFAULT_TOTW_PROMOBLOCK_ALT_WAITING_TEXT_KEY: {
        'ru': 'Вы экономите %(cost)s',
        'en': 'Thanks! You saved %(cost)s',
    },
    DEFAULT_TOTW_PROMOBLOCK_ALT_WAITING_TITLE_KEY: {
        'ru': 'Спасибо вам за ожидание',
        'en': 'Thanks for waitingg',
    },
}

BASE_MEDIA_URL = 'https://promo-stories.s3.yandex.net/prod/middle_point/ru'

DEFAULT_PROMOBLOCK_TEXT_ITEMS = [
    {
        'color': '#000000',
        'font_size': 10,
        'text': 'totw_family_share_promoblock.text',
        'type': 'text',
        'is_tanker_key': True,
    },
    {
        'color': '#000000',
        'font_size': 10,
        'text': 'просто текст',
        'type': 'text',
        'is_tanker_key': False,
    },
]

DEFAULT_PROMOBLOCK_TITLE_ITEMS = [
    {
        'color': '#000000',
        'font_size': 10,
        'text': 'totw_family_share_promoblock.title',
        'type': 'text',
        'is_tanker_key': True,
    },
    {
        'color': '#000000',
        'font_size': 10,
        'text': 'просто текст',
        'type': 'text',
        'is_tanker_key': False,
    },
]


def localize(key, locale, default_locale, keyset):
    if key in keyset:
        mapping = keyset[key]

        if locale in mapping:
            return mapping[locale]
        if default_locale in mapping:
            return mapping[default_locale]

    return None


def create_promotions_story(
        story_id,
        name='middle_point',
        active=False,
        story_context=None,
        zones=None,
        with_mediatags=False,
):
    result = {
        'active': active,
        'id': story_id,
        'name': name,
        'options': {
            'activate_condition': {},
            'communication_type': 'story',
            'end_date': '2022-09-01T00:00:00.000000Z',
            'meta_type': 'old_story',
            'priority': 1,
            'start_date': '2020-09-01T00:00:00.000000Z',
            'zones': zones or [],
        },
        'payload': {
            'pages': [
                {
                    'backgrounds': [
                        create_background(
                            'video',
                            f'{BASE_MEDIA_URL}/point-01.mp4',
                            is_mediatag=with_mediatags,
                        ),
                    ],
                },
                {
                    'backgrounds': [
                        create_background(
                            'video',
                            f'{BASE_MEDIA_URL}/point-02.mp4',
                            is_mediatag=with_mediatags,
                        ),
                    ],
                    'widgets': {
                        'action_buttons': [
                            {
                                'color': 'FFFFFF',
                                'is_tanker_key': True,
                                'text': DEFAULT_BUTTON_TITLE_KEY,
                                'text_color': '000000',
                                'action': {
                                    'type': 'web_view',
                                    'payload': {
                                        'content': 'https://yandex.com/',
                                    },
                                },
                            },
                        ],
                    },
                },
            ],
            'preview': {
                'backgrounds': [
                    create_background(
                        'image',
                        f'{BASE_MEDIA_URL}/teaser_image.jpg',
                        is_mediatag=with_mediatags,
                    ),
                ],
            },
        },
        'type': 'story',
    }
    if story_context:
        result['story_context'] = story_context
    return result


def create_background(media_type, content, is_mediatag=False):
    if is_mediatag:
        return create_mediatag(media_type, content)

    return {'content': content, 'type': media_type}


def create_mediatag(media_type, content):
    return {
        'id': 'mediatag_id',
        'type': media_type,
        'resize_mode': 'original_only',
        'sizes': [
            {
                'field': 'original',
                'value': 0.0,
                'mds_id': 'mds_id.jpg',
                'url': content,
            },
        ],
    }


def create_old_story(
        story_id,
        locale,
        default_locale='ru',
        active=False,
        name='middle_point',
):
    return {
        'active': active,
        'button_link': 'https://yandex.com/',
        'button_title': localize(
            DEFAULT_BUTTON_TITLE_KEY,
            locale,
            default_locale,
            keyset=DEFAULT_CLIENT_MESSAGES,
        ),
        'id': story_id,
        'media': [
            {
                'content': f'{BASE_MEDIA_URL}/point-01.mp4',
                'show_button': False,
                'type': 'video',
            },
            {
                'content': f'{BASE_MEDIA_URL}/point-02.mp4',
                'show_button': True,
                'type': 'video',
            },
        ],
        'name': name,
        'teaser_image': f'{BASE_MEDIA_URL}/teaser_image.jpg',
    }


def create_promotions_response(
        stories=None, promos_on_summary=None, totw_banners=None,
):
    return {
        'stories': stories or [],
        'fullscreens': [],
        'cards': [],
        'notifications': [],
        'deeplink_shortcuts': [],
        'eda_banners': [],
        'promos_on_map': [],
        'promos_on_summary': promos_on_summary or [],
        'showcases': [],
        'totw_banners': totw_banners or [],
    }


def create_stories_response(stories):
    return {'stories': stories}


def create_eq_predicate(arg_name, value, arg_type='string'):
    return {
        'init': {'arg_name': arg_name, 'arg_type': arg_type, 'value': value},
        'type': 'eq',
    }


def create_experiment(name, consumers, predicates, value):
    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'name': name,
        'consumers': consumers,
        'clauses': [
            {
                'predicate': {
                    'init': {'predicates': predicates},
                    'type': 'all_of',
                },
                'value': value,
            },
        ],
    }


# pylint: disable=dangerous-default-value
def create_promotions_promoblock(
        promoblock_id,
        experiment=DEFAULT_TOTW_PROMOTIONS_EXP_NAME,
        text_items=DEFAULT_PROMOBLOCK_TEXT_ITEMS,
        title_items=DEFAULT_PROMOBLOCK_TITLE_ITEMS,
        priority=1,
        widgets=None,
):
    result = {
        'id': promoblock_id,
        'meta_type': 'family_promo_block',
        'supported_classes': ['econom', 'comfort', 'comfortplus'],
        'options': {
            'experiment': experiment,
            'priority': priority,
            'has_yql_data': False,
        },
        'title': {'items': title_items},
        'text': {'items': text_items},
        'widgets': {},
        'show_policy': {'max_show_count': 3, 'max_widget_usage_count': 1},
        'configuration': {'type': 'list'},
    }

    if not widgets:
        widgets = []
    if 'toggle' in widgets:
        result['widgets'].update(
            {
                'toggle': {
                    'is_selected': False,
                    'option_on': {
                        'text': {
                            'items': [
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': (
                                        'totw_family_share_promoblock.text'
                                    ),
                                    'type': 'text',
                                    'is_tanker_key': True,
                                },
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': 'просто текст',
                                    'type': 'text',
                                    'is_tanker_key': False,
                                },
                            ],
                        },
                        'title': {
                            'items': [
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': (
                                        'totw_family_share_promoblock.title'
                                    ),
                                    'type': 'text',
                                    'is_tanker_key': True,
                                },
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': 'просто текст',
                                    'type': 'text',
                                    'is_tanker_key': False,
                                },
                            ],
                        },
                        'actions': [],
                    },
                    'option_off': {
                        'text': {
                            'items': [
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': (
                                        'totw_family_share_promoblock.text'
                                    ),
                                    'type': 'text',
                                    'is_tanker_key': True,
                                },
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': 'просто текст',
                                    'type': 'text',
                                    'is_tanker_key': False,
                                },
                            ],
                        },
                        'title': {
                            'items': [
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': (
                                        'totw_family_share_promoblock.title'
                                    ),
                                    'type': 'text',
                                    'is_tanker_key': True,
                                },
                                {
                                    'color': '#000000',
                                    'font_size': 10,
                                    'text': 'просто текст',
                                    'type': 'text',
                                    'is_tanker_key': False,
                                },
                            ],
                        },
                        'actions': [],
                    },
                },
            },
        )
    if 'attributed_text' in widgets:
        result['widgets'].update({'attributed_text': {'items': []}})

    return result


def create_promotions_totw_banner(
        banner_id, experiment=DEFAULT_TOTW_PROMOTIONS_EXP_NAME, priority=1,
):
    return {
        'id': banner_id,
        'title': {
            'content': DEFAULT_TOTW_BANNER_TITLE_KEY,
            'color': 'FFFFFF',
            'type': 'large',
            'is_tanker_key': True,
        },
        'text': {'content': 'text'},
        'icon': {
            'image_tag': 'my_image_tag',
            'image_url': 'http://here.is.url/with/path?and=query',
        },
        'backgrounds': [
            {
                'content': (
                    'https://promo-stories-testing.s3.mds.yandex.net'
                    '/5_stars_movies_2/ru'
                    '/bddc645586f92b2fef9fd8b9ad6f617efc37be80.png'
                ),
                'type': 'image',
            },
            {'content': 'FFFFFF', 'type': 'color'},
        ],
        'action': {'deeplink': 'yandextaxi://depplink'},
        'show_policy': {
            'id': 'show_policy_id',
            'max_show_count': 3,
            'max_widget_usage_count': 1,
        },
        'options': {
            'experiment': experiment,
            'priority': priority,
            'start_date': '2020-04-15T14:40:00.000000Z',
            'end_date': '2029-04-15T14:40:00.000000Z',
            'has_yql_data': False,
        },
    }


def create_inapp_totw_banner(banner_id, priority=1, locale='ru'):
    return {
        'id': banner_id,
        'title': {
            'items': [
                {
                    'text': localize(
                        DEFAULT_TOTW_BANNER_TITLE_KEY,
                        locale,
                        'ru',
                        keyset=DEFAULT_BACKEND_PROMOTIONS,
                    ),
                    'type': 'text',
                },
            ],
        },
        'text': {'items': [{'text': 'text', 'type': 'text'}]},
        'icon': {
            'image_tag': 'my_image_tag',
            'image_url': 'http://here.is.url/with/path?and=query',
        },
        'backgrounds': [
            {
                'content': (
                    'https://promo-stories-testing.s3.mds.yandex.net'
                    '/5_stars_movies_2/ru'
                    '/bddc645586f92b2fef9fd8b9ad6f617efc37be80.png'
                ),
                'type': 'image',
            },
            {'content': 'FFFFFF', 'type': 'color'},
        ],
        'action': {'deeplink': 'yandextaxi://depplink'},
        'show_policy': {
            'id': 'show_policy_id',
            'max_show_count': 3,
            'max_widget_usage_count': 1,
        },
        'priority': priority,
    }
