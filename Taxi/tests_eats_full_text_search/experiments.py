import dataclasses
import typing

import pytest

from tests_eats_full_text_search import catalog
from tests_eats_full_text_search import colors


@dataclasses.dataclass
class ZeroSuggestBlockYabsParams:
    page_id: int = 1
    target_ref: str = 'testsuite'
    page_ref: str = 'testsuite'


@dataclasses.dataclass
class ZeroSuggestBlockAdvertSettings:
    limit: int = 1
    yabs_parameters: ZeroSuggestBlockYabsParams = ZeroSuggestBlockYabsParams()


@dataclasses.dataclass
class CatalogZeroSuggestBlock:
    title: str = 'testsuite'
    title_key: str = 'zero_suggest.recommends'
    low: int = 0
    min_count: int = 0
    limit: typing.Optional[int] = None
    compilation_type: typing.Optional[str] = None
    brand_ids: typing.Iterable[int] = ()
    advert_settings: typing.Optional[ZeroSuggestBlockAdvertSettings] = None


ADVERTS_OFF = pytest.mark.experiments3(
    name='eats_switching_off_advertising',
    consumers=[
        'eats-full-text-search/catalog-search',
        'eats-full-text-search/search',
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)


def catalog_zero_suggest(blocks: typing.List[CatalogZeroSuggestBlock]):
    exp_blocks = []
    for block in blocks:
        exp_blocks.append(dataclasses.asdict(block))

    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_fts_catalog_zero_suggest',
        consumers=['eats-full-text-search/catalog-search'],
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': {'blocks': exp_blocks},
            },
        ],
    )


def place_block_settings(
        place_items_limit: int,
        search_type: str,
        show_more: str,
        show_more_text: str,
):
    return pytest.mark.experiments3(
        name='eats_fts_place_block_settings',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'place_items_limit': place_items_limit,
                    'search_type': search_type,
                    'show_more': show_more,
                    'show_more_text': show_more_text,
                },
            },
        ],
    )


def set_sort_by_sku_experiment(experiments3, sort_by_sku: bool):
    experiments3.add_experiment(
        name='eats_fts_sort_by_sku',
        consumers=['eats_full_text_search/sort_by_sku'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Title',
                'predicate': {'type': 'true'},
                'value': {'sort_by_sku': sort_by_sku},
            },
        ],
    )


USE_ERMS_IN_CATALOG_SEARCH = pytest.mark.experiments3(
    name='eats_fts_use_erms_in_catalog_search',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)


USE_ERMS_IN_RESTAURANT_SEARCH = pytest.mark.experiments3(
    name='eats_fts_use_erms_in_restaurant_search',
    consumers=['eats-full-text-search/search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)

BANNER_MARKET = pytest.mark.experiments3(
    name='eats_fts_banner_market',
    consumers=['eats-full-text-search/search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {
                'banner': {
                    'id': 'market',
                    'url': 'some_banner_url',
                    'gallery': {
                        'dark': {'url': 'some_dark_url'},
                        'light': {'url': 'some_light_url'},
                    },
                },
            },
        },
    ],
    is_config=True,
)


@dataclasses.dataclass
class EatsFTSColors:
    adverts_label: typing.Optional[colors.ColoredText] = None

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


def eats_fts_colors(fts_colors: EatsFTSColors):
    return pytest.mark.experiments3(
        name='eats_fts_colors',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': fts_colors.asdict(),
            },
        ],
        is_config=True,
    )


def eats_fts_blocks_for_catalog(blocks: typing.List[catalog.BlockParam]):
    catalog_blocks = list(block.asdict() for block in blocks)
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_fts_blocks_for_eats_catalog',
        consumers=['eats-full-text-search/catalog-search'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'catalog_blocks': catalog_blocks},
            },
        ],
    )


CATALOG_PLACE_META = pytest.mark.experiments3(
    name='eats_fts_catalog_place_meta',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'show_rating': True},
        },
    ],
    is_config=True,
)


def eats_fts_communications(
        search_inside_shop_informers_enabled: bool = False,
        search_main_shops_informers_enabled: bool = False,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_fts_communications',
        consumers=['eats-full-text-search/search'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'search_inside_shop_informers_enabled': (
                        search_inside_shop_informers_enabled
                    ),
                    'search_main_shops_informers_enabled': (
                        search_main_shops_informers_enabled
                    ),
                },
            },
        ],
    )


EATS_FTS_SELECTOR = pytest.mark.experiments3(
    name='eats_fts_selector',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {
                'default': 'all',
                'selectors': [
                    {
                        'slug': 'all',
                        'text': 'Все',
                        'businesses': ['restaurant', 'shop', 'store'],
                    },
                    {
                        'slug': 'restaurant',
                        'text': 'Рестораны',
                        'businesses': ['restaurant', 'store'],
                    },
                    {
                        'slug': 'shop',
                        'text': 'Магазины',
                        'businesses': ['shop', 'store'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)
