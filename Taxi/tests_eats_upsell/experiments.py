import enum
import typing

import pytest

CONSUMER_PROMOTER = 'eats-upsell/promoter'
CONSUMER_UPSELL = 'eats-upsell-upsell'
CONSUMER_RECOMMENDATIONS = 'eats-upsell/retail/v1/menu/recommendations'
CONSUMER_RETAIL_SWITCHER = 'eats-upsell-retail-switcher'


class SourceType(str, enum.Enum):
    COMPLEMENT = 'complement'
    ADVERT = 'advert'


def upsell_sources(source_types: typing.List[SourceType]):
    value = []
    for source_type in source_types:
        value.append({'type': source_type})

    return pytest.mark.experiments3(
        name='eats_upsell_sources',
        consumers=[CONSUMER_UPSELL],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'sources': value},
            },
        ],
        is_config=True,
    )


def upsell_retail_switcher(on_off: bool):
    return pytest.mark.experiments3(
        name='eats_upsell_enable_retail',
        consumers=[CONSUMER_RETAIL_SWITCHER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': on_off},
            },
        ],
        is_config=True,
    )


def upsell_dj_settings(enabled: bool, exp_name: str):
    return pytest.mark.experiments3(
        name='eats_upsell_enable_dj',
        consumers=[CONSUMER_UPSELL],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled, 'experiment': exp_name},
            },
        ],
        is_config=False,
    )


def get_upsell_complement(
        min_pair_npmi: float = 0,
        min_suggest_size: int = 3,
        max_suggest_size: int = 1000,
        max_candidates_num_per_item: int = 10,
        sort_by: str = 'npmi',
):
    value = {
        'min_pair_npmi': min_pair_npmi,
        'min_suggest_size': min_suggest_size,
        'max_suggest_size': max_suggest_size,
        'max_candidates_num_per_item': max_candidates_num_per_item,
        'sort_by': sort_by,
    }
    return pytest.mark.experiments3(
        name='eats_upsell_complement',
        consumers=[CONSUMER_UPSELL],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
        is_config=True,
    )


def get_recommend_settings_exp(
        limit: int = None, min_items: int = None, enabled: bool = True,
):
    value = {}
    if limit is not None:
        value['limit'] = limit
    if min_items is not None:
        value['min'] = min_items

    return pytest.mark.experiments3(
        name='eats_upsell_recommendations_settings',
        consumers=[CONSUMER_UPSELL],
        match={'predicate': {'type': 'true'}, 'enabled': enabled},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
        is_config=True,
    )


def create_promo_experiment(name: str, promo: dict):
    """
    Создаеет промо-эксперимент.
    """
    promo_prefix: str = 'eats_upsell_promo_'

    return pytest.mark.experiments3(
        name=promo_prefix + name,
        consumers=['eats-upsell/promoter'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': promo,
            },
        ],
    )


def create_promotion(
        name: str,
        consumers: typing.List[str] = None,
        priority: typing.Optional[int] = None,
):
    promo_prefix: str = 'eats_upsell_promo_'
    default_consumers: list = [
        CONSUMER_PROMOTER,
        CONSUMER_UPSELL,
        CONSUMER_RECOMMENDATIONS,
    ]

    value: dict = {'promo_name': name}
    if priority:
        value['priority'] = priority

    return pytest.mark.experiments3(
        name=promo_prefix + name,
        consumers=consumers or default_consumers,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
    )


def use_retail_new_flow(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_upsell_retail_new_flow',
        is_config=True,
        consumers=[CONSUMER_UPSELL],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )


def promo_settings(
        positions: typing.List[int] = None, unlimited: bool = False,
):
    return pytest.mark.experiments3(
        name='eats_upsell_promo_settings',
        is_config=True,
        consumers=[CONSUMER_UPSELL, CONSUMER_RECOMMENDATIONS],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'positions': positions or [],
                    'unlimited': unlimited,
                },
            },
        ],
    )


def create_rest_menu_storage_exp():
    return pytest.mark.experiments3(
        name='eats_upsell_use_rest_menu_storage',
        consumers=[CONSUMER_UPSELL],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def eats_discounts_promo_types_info(value):
    return pytest.mark.experiments3(
        name='eats_discounts_promo_types_info',
        consumers=['eats-discounts-applicator/user'],
        is_config=True,
        default_value=value,
    )


def dynamic_prices(default_percent: int, items_percents: dict = None):
    items = {'__default__': default_percent}
    if items_percents:
        items.update(items_percents)
    return pytest.mark.experiments3(
        name='eats_dynamic_price_by_user',
        consumers=['eats_smart_prices/user'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': True,
                    'calculate_method': 'by_place_percent',
                    'modification_percent': items,
                },
            },
        ],
    )


def disable_adverts():
    return pytest.mark.experiments3(
        name='eats_switching_off_advertising',
        consumers=[
            'eats-upsell-upsell',
            'eats-upsell/retail/v1/menu/recommendations',
        ],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
        is_config=True,
    )
