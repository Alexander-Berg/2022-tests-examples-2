import pytest

EXP_BLOCKED_YANDEX_UID = 'exp_blocked_yandex_uid'
EXP_BLOCKED_DEPOT_ID = 'store22xx'
EXP_BLOCKED_COUNTRY = 'GBR'
EXP_DEPOT_ID_IN_BLOCKED_COUNTRY = 'store33xx'

CATEGORY_EXPERIMENT = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    consumers=['grocery-caas/client_library'],
    name='lavka_selloncogs',
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
        {
            'title': 'disable_country',
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': [EXP_BLOCKED_COUNTRY],
                    'arg_name': 'country_iso3',
                    'set_elem_type': 'string',
                },
            },
            'value': {'enabled': False},
        },
    ],
    default_value={'enabled': True},
)


@CATEGORY_EXPERIMENT
async def test_markdown_smoke_ok(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_markdown,
        default_auth_headers,
):
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'store11xx', 'category': 'markdown'},
        headers=default_auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json() == grocery_caas_markdown.category_data
    assert grocery_caas_markdown.times_called == 1


@CATEGORY_EXPERIMENT
async def test_markdown_smoke_not_found(
        mockserver,
        taxi_grocery_caas_sample_consumer,
        grocery_caas_markdown,
        default_auth_headers,
):
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'unknown_depot', 'category': 'markdown'},
        headers=default_auth_headers,
    )
    assert resp.status_code == 404
    assert not grocery_caas_markdown.has_calls

    #  blocked depot by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': EXP_BLOCKED_DEPOT_ID, 'category': 'markdown'},
        headers=default_auth_headers,
    )
    assert resp.status_code == 404
    assert not grocery_caas_markdown.has_calls

    #  blocked yandex_uid by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={'depot_id': 'store11xx', 'category': 'markdown'},
        headers={
            **default_auth_headers,
            'X-Yandex-UID': EXP_BLOCKED_YANDEX_UID,
        },
    )
    assert resp.status_code == 404
    assert not grocery_caas_markdown.has_calls

    #  blocked country_iso3 by experiment
    resp = await taxi_grocery_caas_sample_consumer.post(
        '/lavka/v1/caas-sample-consumer/v2/category',
        json={
            'depot_id': EXP_DEPOT_ID_IN_BLOCKED_COUNTRY,
            'category': 'markdown',
        },
        headers=default_auth_headers,
    )
    assert resp.status_code == 404
    assert not grocery_caas_markdown.has_calls
