import typing

import pytest

ALWAYS = {'predicate': {'type': 'true'}, 'enabled': True}


def always_match(
        name: str, consumer: str, value: dict, is_config: bool = False,
):
    return pytest.mark.experiments3(
        is_config=is_config,
        match=ALWAYS,
        name=name,
        consumers=[consumer],
        clauses=[
            {
                'title': 'Always match',
                'value': value,
                'predicate': {'type': 'true'},
            },
        ],
    )


ENABLE_AUTOSCALING = always_match(
    is_config=True,
    name='eats_communications_banners_source',
    consumer='eats-communications/layout-banners',
    value={
        'enable_inapp': True,
        'enable_feeds': True,
        'enable_autoscaling': True,
    },
)

ADVERTS_OFF = always_match(
    name='eats_switching_off_advertising',
    consumer='eats-communications/layout-banners',
    value={'enabled': True},
    is_config=True,
)

ENABLE_LINKS_OVERRIDE = always_match(
    is_config=True,
    name='eats_communications_url_from_feeds',
    consumer='eats-communications/layout-banners',
    value={'enabled': True},
)


def has_ya_plus(name: str, consumers: typing.List[str]):
    return pytest.mark.experiments3(
        match=ALWAYS,
        name=name,
        consumers=consumers,
        clauses=[
            {
                'title': 'Match plus',
                'predicate': {
                    'init': {
                        'arg_name': 'has_ya_plus',
                        'arg_type': 'bool',
                        'value': True,
                    },
                    'type': 'eq',
                },
                'enabled': True,
                'value': {'enabled': True},
            },
        ],
    )


def feed(name: str):
    return always_match(
        name, 'eats-communications/eats-promotions-banner', {'enabled': True},
    )


def feeds(names: typing.List[str]):
    return pytest.mark.bulk_experiments(
        consumer='eats-communications/eats-promotions-banner',
        names=names,
        value={'enabled': True},
    )


def channel(name: str):
    return always_match(
        name=name,
        consumer='eats-communications/communications',
        value={'enabled': True},
    )


def brand_link(links: typing.List):
    return always_match(
        'eats_catalog_place_link',
        'eats-communications/layout-banners',
        {'brand_link': links},
        is_config=True,
    )


def filter_banners(banner_ids: typing.List[int]):
    return always_match(
        name='eats_communications_filter_banners',
        consumer='eats-communications/layout-banners',
        value={'exclude_banner_id': banner_ids},
    )


def feed_validation(remove_invalid: bool = True):
    return always_match(
        name='eats_communications_feeds_validation',
        consumer='eats-communications/feeds_validation',
        value={
            'invalid_feeds_log_level': 'error',
            'remove_invalid_feeds': remove_invalid,
        },
        is_config=True,
    )


def use_eats_catalog():
    return always_match(
        name='eats_communications_use_eats_catalog_places',
        consumer='eats-communications/layout-banners',
        value={'enabled': True},
        is_config=True,
    )


def yabs_parameters(
        enabled: bool = True,
        page_id: int = 1,
        imp_id: int = 1,
        target_ref: str = 'testsuite',
):
    return always_match(
        name='eats_communications_yabs_parameters',
        consumer='eats-communications/layout-banners',
        value={
            'enabled': enabled,
            'page_id': page_id,
            'imp_id': imp_id,
            'target_ref': target_ref,
        },
        is_config=True,
    )


def stories_limit_settings(
        max_screen_stories: int = 1, max_categories_stories: int = 1,
):
    return always_match(
        is_config=True,
        name='eats_communications_communications_settings',
        consumer='eats-communications/screen-stories',
        value={
            'max_stories_screen_communications': max_screen_stories,
            'max_stories_categories_communications': max_categories_stories,
        },
    )


def informers_limit_settings(
        max_screen_informers: int = 1, max_categories_informers: int = 1,
):
    return always_match(
        is_config=True,
        name='eats_communications_communications_settings',
        consumer='eats-communications/informers',
        value={
            'max_informers_screen_communications': max_screen_informers,
            'max_informers_categories_communications': (
                max_categories_informers
            ),
        },
    )


def screen_stories(name):
    return always_match(
        is_config=False,
        name=name,
        consumer='eats-communications/screen-stories',
        value={'enabled': True},
    )


def informers(name):
    return always_match(
        is_config=False,
        name=name,
        consumer='eats-communications/informers',
        value={'enabled': True},
    )
