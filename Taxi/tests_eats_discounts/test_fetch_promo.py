import copy
import random
from typing import FrozenSet
from typing import List
from typing import Optional
import uuid

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


FUTURE_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-10T10:01:00+00:00',
            'is_start_utc': True,
            'is_end_utc': True,
            'end': '2021-01-01T00:00:00+00:00',
        },
    ],
}

REGION = 123

BRAND_1 = 321
BRAND_2 = 322

PLACE_1_1 = 456
PLACE_1_2 = 457
PLACE_2_1 = 458
PLACE_2_2 = 459


BRANDS = {BRAND_1: (PLACE_1_1, PLACE_1_2), BRAND_2: (PLACE_2_1, PLACE_2_2)}


def _make_promo(name_suffix: Optional[str] = None) -> dict:
    promo = common.get_discount_meta()['promo']
    if name_suffix is None:
        return promo
    promo['name'] = promo['name'] + '_' + name_suffix
    return promo


def _common_expected_response(
        hierarchy_names: List[str], add_rules_data: dict, region: dict,
) -> dict:
    hierarchies_promos = []
    promos: list = []
    if region['id'] != REGION:
        return {'hierarchy_promos': [], 'promos': []}
    brands = {brand['id'] for brand in region['brands']}
    for brand in BRANDS:
        if brand not in brands:
            return {'hierarchy_promos': [], 'promos': []}
    if FUTURE_ACTIVE_PERIOD in list(add_rules_data.values())[0][0]['rules']:
        return {'hierarchy_promos': [], 'promos': []}

    hierarchy_names = sorted(set(hierarchy_names) & set(add_rules_data.keys()))
    for hierarchy_name in hierarchy_names:
        if not promos:
            promos.append(_make_promo())
        hierarchy_promos: dict = {'hierarchy_name': hierarchy_name}
        place_promos = [
            {'id': PLACE_1_1, 'promo_indexes': [len(promos), 0]},
            {'id': PLACE_1_2, 'promo_indexes': [len(promos)]},
            {'id': PLACE_2_1, 'promo_indexes': [len(promos), 0]},
            {'id': PLACE_2_2, 'promo_indexes': [len(promos)]},
        ]
        promos.append(_make_promo(hierarchy_name))
        hierarchy_promos['place_promos'] = place_promos
        hierarchies_promos.append(hierarchy_promos)

    return {'hierarchy_promos': hierarchies_promos, 'promos': promos}


async def _check_fetch_promo(
        client,
        request: dict,
        expected_status_code: int,
        expected_response: dict,
):
    expected_response = copy.deepcopy(expected_response)

    response = await client.post(
        'v1/fetch-promo/', request, headers=common.get_headers(),
    )

    assert response.status_code == expected_status_code, response.text

    response_json = response.json()

    if expected_status_code != 200:
        assert expected_response == response_json
        return

    promos = response_json['promos']
    assert (
        sorted(promos, key=lambda x: x['name']) == expected_response['promos']
    )

    hierarchy_promos = response_json['hierarchy_promos']
    assert len({item['hierarchy_name'] for item in hierarchy_promos}) <= len(
        set(request['hierarchy_names']),
    )
    hierarchy_promos.sort(key=lambda x: x['hierarchy_name'])
    expected_hierarchy_promos = expected_response['hierarchy_promos']
    assert len(hierarchy_promos) == len(expected_hierarchy_promos)
    for h_promos, expected_h_promos in zip(
            hierarchy_promos, expected_hierarchy_promos,
    ):
        assert (
            h_promos['hierarchy_name'] == expected_h_promos['hierarchy_name']
        )
        place_promos = h_promos['place_promos']
        assert len({item['id'] for item in place_promos}) == len(place_promos)
        place_promos.sort(key=lambda x: x['id'])
        assert len(place_promos) == len(expected_h_promos['place_promos'])
        for place_promos, expected_place_promos in zip(
                h_promos['place_promos'], expected_h_promos['place_promos'],
        ):
            assert place_promos['id'] == expected_place_promos['id']
            assert len(place_promos['promo_indexes']) == len(
                expected_place_promos['promo_indexes'],
            )
            for promo_index, expected_promo_index in zip(
                    place_promos['promo_indexes'],
                    expected_place_promos['promo_indexes'],
            ):
                assert (
                    promos[promo_index]
                    == expected_response['promos'][expected_promo_index]
                )


def _get_add_rules_data(
        active_period: Optional[dict] = None,
        hierarchy_names: FrozenSet[str] = frozenset(
            (
                'cart_discounts',
                'menu_discounts',
                'payment_method_discounts',
                'place_delivery_discounts',
                'yandex_delivery_discounts',
            ),
        ),
) -> dict:
    def _make_conditions(
            hierarchy_name: str,
            hirules: List[dict],
            other_rules: List[dict],
            name: str,
            other_name: str,
            discount_getter,
    ) -> List[dict]:
        other_condition = {
            'rules': other_rules,
            'discount': discount_getter(other_name),
            'series_id': str(uuid.uuid4()),
        }
        meta = other_condition['discount']['discount_meta']
        meta['promo'] = _make_promo(hierarchy_name)

        return [
            {
                'rules': rules,
                'discount': discount_getter(name),
                'series_id': str(uuid.uuid4()),
            },
            other_condition,
        ]

    if active_period is None:
        active_period = common.VALID_ACTIVE_PERIOD

    result: dict = {hierarchy_name: [] for hierarchy_name in hierarchy_names}
    hierarchies_discounts = {
        'cart_discounts': common.small_cart_discount,
        'menu_discounts': common.small_menu_discount,
        'payment_method_discounts': common.small_payment_method_discount,
        'place_delivery_discounts': common.small_place_delivery_discount,
        'yandex_delivery_discounts': common.small_yandex_delivery_discount,
    }
    for brand, places in BRANDS.items():
        other_rules = [
            active_period,
            {'condition_name': 'brand', 'values': [brand]},
            {'condition_name': 'region', 'values': [REGION]},
        ]
        rules = [
            active_period,
            {'condition_name': 'brand', 'values': [brand]},
            {'condition_name': 'place', 'values': [places[0]]},
            {'condition_name': 'region', 'values': [REGION]},
        ]
        name = '1'
        other_name = '2'
        for hierarchy_name in hierarchy_names:
            result[hierarchy_name] += _make_conditions(
                hierarchy_name,
                rules,
                other_rules,
                name,
                other_name,
                hierarchies_discounts[hierarchy_name],
            )

    return result


FETCH_TIME = '2020-01-10T10:00:00+0000'  # Friday


@pytest.mark.parametrize(
    'hierarchy_names',
    (
        pytest.param(
            [
                'menu_discounts',
                'cart_discounts',
                'payment_method_discounts',
                'yandex_delivery_discounts',
                'place_delivery_discounts',
            ],
            id='all_hierarchies',
        ),
        pytest.param(['menu_discounts'], id='menu_discounts_hierarchy'),
        pytest.param(['cart_discounts'], id='cart_discounts_hierarchy'),
        pytest.param(
            ['payment_method_discounts'],
            id='payment_method_discounts_hierarchy',
        ),
        pytest.param(
            ['cart_discounts', 'cart_discounts', 'menu_discounts'],
            id='duplicate_hierarchy',
        ),
    ),
)
@pytest.mark.parametrize(
    'add_rules_data, region',
    (
        pytest.param(
            _get_add_rules_data(),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [
                    {
                        'id': BRAND_1,
                        'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}],
                    },
                    {
                        'id': BRAND_2,
                        'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}],
                    },
                ],
            },
            id='add_all_hierarchies_discounts',
        ),
        pytest.param(
            _get_add_rules_data(),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [{'id': 323, 'places': [{'id': 460}, {'id': 461}]}],
            },
            id='another_brand',
        ),
        pytest.param(
            _get_add_rules_data(),
            {
                'id': 124,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [{'id': 324, 'places': [{'id': 462}, {'id': 463}]}],
            },
            id='another_region',
        ),
        pytest.param(
            _get_add_rules_data(None, frozenset(('menu_discounts',))),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [
                    {
                        'id': BRAND_1,
                        'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}],
                    },
                    {
                        'id': BRAND_2,
                        'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}],
                    },
                ],
            },
            id='add_menu_hierarchy_discount',
        ),
        pytest.param(
            _get_add_rules_data(None, frozenset(('cart_discounts',))),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [
                    {
                        'id': BRAND_1,
                        'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}],
                    },
                    {
                        'id': BRAND_2,
                        'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}],
                    },
                ],
            },
            id='add_cart_hierarchy_discount',
        ),
        pytest.param(
            _get_add_rules_data(
                None, frozenset(('payment_method_discounts',)),
            ),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [
                    {
                        'id': BRAND_1,
                        'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}],
                    },
                    {
                        'id': BRAND_2,
                        'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}],
                    },
                ],
            },
            id='add_payment_method_hierarchy_discount',
        ),
        pytest.param(
            _get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'UTC',
                'brands': [
                    {
                        'id': BRAND_1,
                        'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}],
                    },
                    {
                        'id': BRAND_2,
                        'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}],
                    },
                ],
            },
            id='add_future_discounts',
        ),
        pytest.param(
            _get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            {
                'id': REGION,
                'time': FETCH_TIME,
                'time_zone': 'Europe/Moscow',
                'brands': [
                    {
                        'id': BRAND_1,
                        'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}],
                    },
                    {
                        'id': BRAND_2,
                        'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}],
                    },
                ],
            },
            id='add_future_discounts_time_zone',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_fetch_promo(
        client,
        pgsql,
        add_rules,
        add_rules_data,
        hierarchy_names: List[str],
        region: dict,
) -> None:
    await common.init_bin_sets(client)

    await add_rules(add_rules_data)

    await client.invalidate_caches()

    random.shuffle(hierarchy_names)  # order insufficient

    await _check_fetch_promo(
        client,
        {'hierarchy_names': hierarchy_names, 'region': region},
        200,
        _common_expected_response(hierarchy_names, add_rules_data, region),
    )


@pytest.mark.parametrize(
    'missing_hierarchy_name',
    (
        pytest.param(
            'cart_discounts',
            marks=discounts_match.remove_hierarchies('cart_discounts'),
            id='missing_cart_discounts',
        ),
        pytest.param(
            'menu_discounts',
            marks=discounts_match.remove_hierarchies('menu_discounts'),
            id='missing_menu_discounts',
        ),
        pytest.param(
            'payment_method_discounts',
            marks=discounts_match.remove_hierarchies(
                'payment_method_discounts',
            ),
            id='missing_payment_method_discounts',
        ),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_fetch_promo_missing_hierarchy(
        client, add_rules, missing_hierarchy_name: str,
) -> None:
    await common.init_bin_sets(client)

    hierarchy_names = [
        'menu_discounts',
        'cart_discounts',
        'payment_method_discounts',
    ]
    add_rules_data = _get_add_rules_data(
        hierarchy_names=frozenset(
            set(hierarchy_names) - {missing_hierarchy_name},
        ),
    )
    await add_rules(add_rules_data)

    random.shuffle(hierarchy_names)  # order insufficient
    await client.invalidate_caches()

    region = {
        'id': REGION,
        'time': FETCH_TIME,
        'time_zone': 'UTC',
        'brands': [
            {'id': BRAND_1, 'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}]},
            {'id': BRAND_2, 'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}]},
        ],
    }

    expected_response = _common_expected_response(
        [
            hierarchy_name
            for hierarchy_name in hierarchy_names
            if hierarchy_name != missing_hierarchy_name
        ],
        add_rules_data,
        region,
    )

    await _check_fetch_promo(
        client,
        {'hierarchy_names': hierarchy_names, 'region': region},
        200,
        expected_response,
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('cart_discounts', id='cart_discounts'),
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param(
            'payment_method_discounts', id='payment_method_discounts',
        ),
    ),
)
@pytest.mark.parametrize(
    'max_tasks_count, min_places_in_task',
    (
        pytest.param(None, None, id='no_task_no_places'),
        pytest.param(None, 3, id='no_task_few_places'),
        pytest.param(4, None, id='few_task_no_places'),
        pytest.param(1, 100, id='one_task_many_places'),
        pytest.param(100, 1, id='many_tasks_one_place'),
        pytest.param(5, 2, id='few_tasks_and_places'),
    ),
)
@pytest.mark.parametrize(
    'max_places, max_promos_per_place',
    (
        pytest.param(None, 1, id='places_unlimited_promos_limited'),
        pytest.param(1, None, id='places_limited_promos_unlimited'),
    ),
)
@pytest.mark.parametrize(
    'tvm_service_name',
    (
        pytest.param('another_service_name', id='another_service_name'),
        pytest.param('mock', id='mock'),
    ),
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_fetch_promo_settings(
        client,
        pgsql,
        add_rules,
        taxi_config,
        hierarchy_name: str,
        tvm_service_name: str,
        max_places: Optional[int],
        max_promos_per_place: Optional[int],
        max_tasks_count: Optional[int],
        min_places_in_task: Optional[int],
) -> None:
    config: dict = {
        '__default__': {
            'limits': {'hierarchy_limits': {'__default__': {}}},
            'client_limits': {'hierarchy_limits': {'__default__': {}}},
        },
        tvm_service_name: {
            'limits': {'hierarchy_limits': {'__default__': {}}},
            'client_limits': {'hierarchy_limits': {'__default__': {}}},
        },
    }
    limits: dict = config[tvm_service_name]['limits']
    if max_places is not None:
        limits['max_places'] = max_places
    if max_places is not None:
        limits['hierarchy_limits'][hierarchy_name] = {
            'max_promos_per_place': max_promos_per_place,
        }

    if max_tasks_count is not None or min_places_in_task is not None:
        limits['async_settings'] = {}
    if max_tasks_count is not None:
        limits['async_settings']['max_tasks_count'] = max_tasks_count

    if min_places_in_task is not None:
        limits['async_settings']['min_places_in_task'] = min_places_in_task

    taxi_config.set(EATS_DISCOUNTS_FETCH_PROMO_SETTINGS=config)

    await common.init_bin_sets(client)

    add_rules_data = _get_add_rules_data()
    await add_rules(add_rules_data)

    hierarchy_names = [
        'menu_discounts',
        'cart_discounts',
        'payment_method_discounts',
    ]

    random.shuffle(hierarchy_names)  # order insufficient

    await client.invalidate_caches()

    region = {
        'id': REGION,
        'time': FETCH_TIME,
        'time_zone': 'UTC',
        'brands': [
            {'id': BRAND_1, 'places': [{'id': PLACE_1_1}, {'id': PLACE_1_2}]},
            {'id': BRAND_2, 'places': [{'id': PLACE_2_1}, {'id': PLACE_2_2}]},
        ],
    }

    expected_response = _common_expected_response(
        hierarchy_names, add_rules_data, region,
    )
    expected_status_code = 200

    if tvm_service_name == 'mock':
        if max_places is not None:
            expected_status_code = 400
            expected_response = {
                'code': 'Validation error',
                'message': f'Places count exceeds {max_places}',
            }
        else:
            if max_promos_per_place is not None:
                expected_response = _common_expected_response(
                    hierarchy_names, add_rules_data, region,
                )
                for hierarchy_promos in expected_response['hierarchy_promos']:
                    if hierarchy_promos['hierarchy_name'] == hierarchy_name:
                        for place_promos in hierarchy_promos['place_promos']:
                            promo_indexes = place_promos['promo_indexes']
                            promo_indexes = promo_indexes[
                                0 : min(
                                    len(promo_indexes), max_promos_per_place,
                                )
                            ]

    else:
        expected_response = _common_expected_response(
            hierarchy_names, add_rules_data, region,
        )

    await _check_fetch_promo(
        client,
        {'hierarchy_names': hierarchy_names, 'region': region},
        expected_status_code,
        expected_response,
    )


@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_fetch_promo_async_settings(
        client, pgsql, add_rules, taxi_config, load_json,
) -> None:
    taxi_config.set(
        EATS_DISCOUNTS_FETCH_PROMO_SETTINGS={
            '__default__': {
                'limits': {
                    'hierarchy_limits': {'__default__': {}},
                    'async_settings': {
                        'max_tasks_count': 2,
                        'min_places_in_task': 1,
                    },
                },
                'client_limits': {'hierarchy_limits': {'__default__': {}}},
            },
        },
    )

    await add_rules(load_json('add_rules_data.json'))

    await client.invalidate_caches()

    await _check_fetch_promo(
        client, load_json('request_1.json'), 200, load_json('response.json'),
    )
    await _check_fetch_promo(
        client, load_json('request_2.json'), 200, load_json('response.json'),
    )
