import pytest


EXP_BLOCKED_YANDEX_UID = 'exp_blocked_yandex_uid'
EXP_BLOCKED_DEPOT_ID = 'store22xx'

CATEGORY_EXPERIMENT = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    consumers=['grocery-caas/client_library'],
    name='grocery_caas_recent_products',
    is_config=True,
    clauses=[
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
    ],
    default_value={'enabled': True},
)


@CATEGORY_EXPERIMENT
async def test_recent_products_smoke_ok(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_recent_products,
        default_auth_headers,
):
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/v1/grocery-caas-sample-consumer/v1/category',
        json={'depot_id': 'store11xx', 'category': 'recent-purchases'},
        headers=default_auth_headers,
    )

    expected = {
        'products': [
            {'product_id': 'some_id1'},
            {'product_id': 'some_id2'},
            {'product_id': 'some_id3'},
            {'product_id': 'some_id4'},
        ],
        'subcategories': [],
    }

    assert resp.status_code == 200
    assert resp.json() == expected
    assert grocery_caas_recent_products.times_called_presence == 1
    assert grocery_caas_recent_products.times_called == 1


@CATEGORY_EXPERIMENT
async def test_recent_products_smoke_not_found(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_recent_products,
        default_auth_headers,
):
    #  blocked yandex_uid by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/v1/grocery-caas-sample-consumer/v1/category',
        json={'depot_id': 'store11xx', 'category': 'recent-purchases'},
        headers={
            **default_auth_headers,
            'X-Yandex-UID': EXP_BLOCKED_YANDEX_UID,
        },
    )
    assert resp.status_code == 404
    assert not grocery_caas_recent_products.has_calls

    #  blocked depot by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/v1/grocery-caas-sample-consumer/v1/category',
        json={
            'depot_id': EXP_BLOCKED_DEPOT_ID,
            'category': 'recent-purchases',
        },
        headers=default_auth_headers,
    )
    assert resp.status_code == 404
    assert not grocery_caas_recent_products.has_calls
