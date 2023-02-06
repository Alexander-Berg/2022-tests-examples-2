import copy

import pytest

from testsuite.utils import ordered_object


EXP_BLOCKED_YANDEX_UID = 'exp_blocked_yandex_uid'
EXP_BLOCKED_DEPOT_ID = 'store22xx'


def _create_category_experiment(experiments3, name, is_config):
    match = {'predicate': {'type': 'true'}, 'enabled': True}
    consumers = ['grocery-caas/client_library']
    clauses = [
        {
            'title': 'disable_depot',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': EXP_BLOCKED_DEPOT_ID,
                },
            },
            'value': {'enabled': False},
        },
        {
            'title': 'disable_user',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': [EXP_BLOCKED_YANDEX_UID],
                    'arg_name': 'yandex_uid',
                    'set_elem_type': 'string',
                },
            },
            'value': {'enabled': False},
        },
    ]

    if is_config:
        experiments3.add_config(
            match=match,
            consumers=consumers,
            name=name,
            clauses=clauses,
            default_value={'enabled': True},
        )
    else:
        experiments3.add_experiment(
            match=match,
            consumers=consumers,
            name=name,
            clauses=clauses,
            default_value={'enabled': True},
        )


@pytest.mark.parametrize(
    'category_name,experiment_name,is_config',
    [
        ('best-offers', 'grocery_caas_best_offers', True),
        ('promo-caas', 'grocery_caas_discounts', True),
        ('cashback-caas', 'grocery_cashback', False),
    ],
)
async def test_best_offers_smoke_ok(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_promo,
        experiments3,
        category_name,
        experiment_name,
        is_config,
        default_auth_headers,
):
    """ sample-consumer should return same response for categories
    as grocery-caas-promo service does """

    _create_category_experiment(experiments3, experiment_name, is_config)
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'store11xx', 'category': category_name},
        headers=default_auth_headers,
    )
    assert resp.status_code == 200
    expected_products = copy.deepcopy(grocery_caas_promo.category_data)
    for item in expected_products['subcategories']:
        del item['keyset_tanker_key']

    ordered_object.assert_eq(
        resp.json(), expected_products, ['products', 'categories'],
    )
    assert grocery_caas_promo.times_called(category_name) == 1


@pytest.mark.parametrize(
    'category_name,experiment_name,is_config',
    [
        ('best-offers', 'grocery_caas_best_offers', True),
        ('promo-caas', 'grocery_caas_discounts', True),
        ('cashback-caas', 'grocery_cashback', False),
    ],
)
async def test_promo_smoke_not_found(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_promo,
        experiments3,
        category_name,
        experiment_name,
        is_config,
        default_auth_headers,
):
    """ sample-consumer should return 404 if depot not found or
    experiment does not match """
    _create_category_experiment(experiments3, experiment_name, is_config)
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'unknown_depot', 'category': category_name},
        headers=default_auth_headers,
    )
    assert resp.status_code == 404
    assert not grocery_caas_promo.has_calls(category_name)

    #  blocked depot by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': EXP_BLOCKED_DEPOT_ID, 'category': category_name},
        headers=default_auth_headers,
    )
    assert resp.status_code == 404
    assert not grocery_caas_promo.has_calls(category_name)

    #  blocked yandex_uid by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'store11xx', 'category': category_name},
        headers={
            **default_auth_headers,
            'X-Yandex-UID': EXP_BLOCKED_YANDEX_UID,
        },
    )
    assert resp.status_code == 404
    assert not grocery_caas_promo.has_calls(category_name)
