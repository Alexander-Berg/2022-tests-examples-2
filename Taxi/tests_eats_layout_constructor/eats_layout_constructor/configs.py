import typing

import pytest


def layout_experiment_name(
        name: str = 'eats_layout_template',
        filters=None,
        collection=None,
        map_name=None,
        recommendations: str = 'eats_layout_constructor_recommendations',
):
    return pytest.mark.config(
        EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
            'check_experiment': True,
            'refresh_period_ms': 1000,
            'experiment_name': name,
            'recommendations_experiment_name': recommendations,
            'collections_experiment_name': collection,
            'filters_experiment_name': filters,
            'map_experiment_name': map_name,
        },
    )


def fallback_layout(slug: str, collection_slug=None):
    return pytest.mark.config(
        EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
            'fallback_enabled': True,
            'layout_slug': slug,
            'collection_layout_slug': collection_slug,
        },
    )


def keep_empty_layout(layout_slug: typing.Optional[str] = None):
    if layout_slug is None:
        return pytest.mark.config(
            EATS_LAYOUT_CONSTRUCTOR_SETTINGS={
                'layout': {'__default__': {'display_without_places': True}},
            },
        )

    return pytest.mark.config(
        EATS_LAYOUT_CONSTRUCTOR_SETTINGS={
            'layout': {layout_slug: {'display_without_places': True}},
        },
    )


def ultima_places(places: dict):
    return pytest.mark.config(
        ULTIMA_PLACES={
            'colors': {
                'title': {'dark': '#TTITLE', 'light': '#TTITLE'},
                'ads': {
                    'text': {'dark': '#ADTEXT', 'light': '#ADTEXT'},
                    'background': {'dark': '#ADBACK', 'light': '#ADBACK'},
                },
                'delivery': {
                    'text': {'dark': '#DETEXT', 'light': '#DETEXT'},
                    'background': {'dark': '#DEBACK', 'light': '#DEBACK'},
                },
                'info': {
                    'title': {'dark': '#ITITLE', 'light': '#ITITLE'},
                    'description': {'dark': '#IDESCR', 'light': '#IDESCR'},
                },
                'review': {
                    'text': {'dark': '#RETEXT', 'light': '#RETEXT'},
                    'subtext': {'dark': '#RSUBTE', 'light': '#RSUBTE'},
                },
            },
            'header': {
                'image': {
                    'light': 'http://header/light',
                    'dark': 'http://header/dark',
                },
                'button': {
                    'deeplink': {
                        'app': 'eda.yandex://carousel/link',
                        'web': 'http://carousel/link',
                    },
                    'icon_image': {
                        'light': 'http://eda.yandex.ru/light',
                        'dark': 'http://eda.yandex.ru/dark',
                    },
                    'background_color': {
                        'dark': '#RETEXT',
                        'light': '#RETEXT',
                    },
                },
            },
            'places': places,
        },
    )


BrandId = str
Tag = str
Url = str


def brands_photo(photos: typing.Dict[BrandId, typing.Dict[Tag, Url]]):
    return pytest.mark.config(EATS_LAYOUT_CONSTRUCTOR_BRAND_HERO_PHOTO=photos)
