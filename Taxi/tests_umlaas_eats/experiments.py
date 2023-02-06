import typing

import pytest


CONSUMER_CATALOG_V1 = 'umlaas-eats-catalog'
CONSUMER_ETA = 'umlaas-eats-eta'
CONSUMER_SEARCH_RANKING = 'umlaas-eats-search-ranking'


def helper(name, value, consumers, is_config: bool = False):
    return pytest.mark.experiments3(
        is_config=is_config,
        name=name,
        consumers=consumers,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


ENABLE_ETA_CALCULATION = helper(
    name='eats_eta_ml',
    value={'tag': 'eta_test', 'enabled': True},
    consumers=[CONSUMER_CATALOG_V1],
)

ENABLE_EATS_ETA = helper(
    name='eats_eta_ml',
    value={
        'tag': 'eta_test',
        'enabled': True,
        'taxi_routing_enabled': True,
        'shift_taxi_delivery_time': 10,
    },
    consumers=[CONSUMER_CATALOG_V1],
)

ENABLE_BIGB = helper(
    is_config=True,
    name='umlaas_eats_bigb',
    value={'enabled': True},
    consumers=[CONSUMER_CATALOG_V1, CONSUMER_SEARCH_RANKING],
)


def deduplication(priority_tag: typing.Optional[str] = None):
    return helper(
        is_config=True,
        name='umlaas_eats_deduplication',
        value={
            'strategy': 'delivery_time_priority',
            'rules': [],
            'priority_tag': priority_tag,
        },
        consumers=[CONSUMER_CATALOG_V1],
    )


DEDUPLICATION_DELIVERY_TIME_PRIORITY = deduplication()


def personal_block(size: int = 6, should_limit: bool = False):
    value = {'tag': 'catalog_test', 'personal_block_size': size}

    if should_limit:
        value['limit_block_size'] = True

    return helper(
        name='eats_catalog_personal_rec_model_params',
        value=value,
        consumers=[CONSUMER_CATALOG_V1],
    )


def promo_ranking(eta_max: int = 60, rating: float = 4.5):
    return helper(
        name='eats_promo_ranking',
        value={
            'tag': 'promo_ranking',
            'enabled': True,
            'eta_max': eta_max,
            'rating': rating,
        },
        consumers=[CONSUMER_CATALOG_V1],
    )


def grocery_eta(eta_min: int = 5, eta_max: int = 15):
    return helper(
        name='eats_lavka_eta',
        value={
            'tag': 'grocery_test',
            'ml_enabled': True,
            'eta_min': eta_min,
            'eta_max': eta_max,
        },
        consumers=[CONSUMER_CATALOG_V1],
    )


def retail_eats_eta(slug: str = 'const'):
    return helper(
        name='eats_retail_eta_ml',
        value={
            'tag': 'eta_retail_ml',
            'slug': slug,
            'enabled': True,
            'shift_total_time': 0,
            'shift_cooking_time': 0,
            'custom_brands': [],
            'shift_const_cooking_time': 0,
            'proxy_umlaas_eats': False,
            'region_offset': 20,
        },
        consumers=[CONSUMER_CATALOG_V1],
    )


def router_limit(
        limit: typing.Optional[int] = None,
        percent: typing.Optional[float] = None,
):
    return helper(
        is_config=True,
        name='umlaas_eats_catalog_router',
        value={'limit': {'max_size': limit, 'percent': percent}},
        consumers=[CONSUMER_CATALOG_V1],
    )


def recommender(name: str):
    return helper(
        name='umlaas_eats_recommender',
        value={'enabled': True, 'experiment_name': name},
        consumers=[CONSUMER_CATALOG_V1],
    )


def eats_retail_suggest(
        enabled: bool,
        enable_fallback: bool = None,
        enable_history: bool = None,
        enable_category_suggest: bool = None,
        tag: str = None,
        min_pair_npmi: float = None,
        min_suggest_size: int = None,
        max_suggest_size: int = None,
):
    value: dict = {'enabled': enabled}
    value['enable_fallback'] = enable_fallback
    value['enable_history'] = enable_history
    value['enable_category_suggest'] = enable_category_suggest
    if tag:
        value['tag'] = tag

    if min_pair_npmi is not None:
        value['min_pair_npmi'] = min_pair_npmi

    if min_suggest_size is not None:
        value['min_suggest_size'] = min_suggest_size

    if max_suggest_size is not None:
        value['max_suggest_size'] = max_suggest_size

    return helper(
        name='umlaas_eats_retail_suggest',
        is_config=True,
        consumers=['umlaas-eats-retail-suggest'],
        value=value,
    )


def orders_history(
        tag: typing.Optional[str] = None,
        orders_num_limit: typing.Optional[int] = 100,
        days_num_limit: typing.Optional[int] = 60,
        feedback_threshold: typing.Optional[int] = 0,
):
    return helper(
        name='eats_catalog_orders_history',
        value={
            'tag': tag,
            'orders_num_limit': orders_num_limit,
            'days_num_limit': days_num_limit,
            'feedback_threshold': feedback_threshold,
        },
        consumers=[CONSUMER_CATALOG_V1],
    )


def personal_block_with_mcd_subst(
        size: int = 6,
        should_limit: bool = False,
        substitute_mcd: bool = False,
):
    value = {'tag': 'catalog_test', 'personal_block_size': size}

    if should_limit:
        value['limit_block_size'] = True
    if substitute_mcd:
        value['substitute_mcd'] = True

    return helper(
        name='eats_catalog_personal_rec_model_params',
        value=value,
        consumers=[CONSUMER_CATALOG_V1],
    )
