import pytest

from tests_eats_retail_products_autodisable import models


HANDLER = '/v1/autodisable_info'
MOCK_NOW = '2021-09-20T15:00:00+03:00'
UNAVAILABLE_UNTIL_IN_FUTURE = '2021-09-20T16:00:00+03:00'
PLACE_ID_1 = 1
PLACE_ID_2 = 2
BRAND_ID_1 = 101
BRAND_ID_2 = 102
DEVICE_ID_1 = 'device_id_1'
DEVICE_ID_2 = 'device_id_2'
ORIGIN_ID_1 = 'item_origin_1'
ORIGIN_ID_2 = 'item_origin_2'
ALGORITHM_NAME_THRESHOLD = 'threshold'


@pytest.mark.now(MOCK_NOW)
async def test_full_schema(
        experiments3, taxi_eats_retail_products_autodisable,
):
    set_default_experiment(experiments3)

    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': PLACE_ID_1,
            'brand_id': BRAND_ID_1,
            'device_id': DEVICE_ID_1,
            'origin_ids': [ORIGIN_ID_1, ORIGIN_ID_2],
        },
    )

    assert response.status == 200
    response_json = response.json()
    response_json['autodisable_info'] = sorted(
        response_json['autodisable_info'], key=lambda k: k['origin_id'],
    )
    assert response_json == {
        'autodisable_info': [
            {'is_available': True, 'origin_id': ORIGIN_ID_1},
            {'is_available': True, 'origin_id': ORIGIN_ID_2},
        ],
    }


@pytest.mark.now(MOCK_NOW)
async def test_minimal_schema(
        experiments3, taxi_eats_retail_products_autodisable,
):
    set_default_experiment(experiments3)

    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': PLACE_ID_1,
            'brand_id': BRAND_ID_1,
            'origin_ids': [ORIGIN_ID_1, ORIGIN_ID_2],
        },
    )

    assert response.status == 200
    response_json = response.json()
    response_json['autodisable_info'] = sorted(
        response_json['autodisable_info'], key=lambda k: k['origin_id'],
    )
    assert response_json == {
        'autodisable_info': [
            {'is_available': True, 'origin_id': ORIGIN_ID_1},
            {'is_available': True, 'origin_id': ORIGIN_ID_2},
        ],
    }


@pytest.mark.parametrize(
    'items_availability',
    ['both_available', 'different_availability', 'both_unavailable'],
)
@pytest.mark.now(MOCK_NOW)
async def test_specific_availability_values(
        experiments3,
        save_autodisabled_products_to_db,
        taxi_eats_retail_products_autodisable,
        to_utc_datetime,
        # parametrize
        items_availability,
):
    set_default_experiment(experiments3)

    autodisabled_products = gen_autodisabled_products(to_utc_datetime)
    if items_availability == 'different_availability':
        save_autodisabled_products_to_db([autodisabled_products[0]])
    elif items_availability == 'both_unavailable':
        save_autodisabled_products_to_db(autodisabled_products)

    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': PLACE_ID_1,
            'brand_id': BRAND_ID_1,
            'origin_ids': [ORIGIN_ID_1, ORIGIN_ID_2],
        },
    )

    assert response.status == 200

    expected_autodisable_info = [
        {'is_available': True, 'origin_id': 'item_origin_1'},
        {'is_available': True, 'origin_id': 'item_origin_2'},
    ]
    if items_availability == 'different_availability':
        expected_autodisable_info[0]['is_available'] = False
    if items_availability == 'both_unavailable':
        expected_autodisable_info[0]['is_available'] = False
        expected_autodisable_info[1]['is_available'] = False

    actual_autodisable_info = response.json()['autodisable_info']
    assert (
        sorted(actual_autodisable_info, key=lambda k: k['origin_id'])
        == expected_autodisable_info
    )


@pytest.mark.experiments3(
    name='eats_retail_products_autodisable_algorithms',
    consumers=['eats-retail-products-autodisable/algorithms'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'algorithms_to_apply': []},
    clauses=[
        {
            'title': 'Title',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': PLACE_ID_1,
                    'arg_name': 'place_id',
                    'arg_type': 'int',
                },
            },
            'value': {'algorithms_to_apply': [ALGORITHM_NAME_THRESHOLD]},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize('place_id', [PLACE_ID_1, PLACE_ID_2])
@pytest.mark.now(MOCK_NOW)
async def test_experiment_differ_by_place_id(
        save_autodisabled_products_to_db,
        taxi_eats_retail_products_autodisable,
        to_utc_datetime,
        # parametrize
        place_id,
):

    autodisabled_products = gen_autodisabled_products_for_two_places(
        to_utc_datetime,
    )
    save_autodisabled_products_to_db(autodisabled_products)

    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': place_id,
            'brand_id': BRAND_ID_1,
            'origin_ids': [ORIGIN_ID_1],
        },
    )

    assert response.status == 200

    expected_autodisable_info = [
        {'is_available': False, 'origin_id': 'item_origin_1'},
    ]
    if place_id == PLACE_ID_2:
        # for PLACE_ID_2 enabled_algorithms is empty,
        # so autodisable won't be applied
        expected_autodisable_info[0]['is_available'] = True

    actual_autodisable_info = response.json()['autodisable_info']
    assert actual_autodisable_info == expected_autodisable_info


@pytest.mark.experiments3(
    name='eats_retail_products_autodisable_algorithms',
    consumers=['eats-retail-products-autodisable/algorithms'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'algorithms_to_apply': []},
    clauses=[
        {
            'title': 'Title',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': BRAND_ID_1,
                    'arg_name': 'brand_id',
                    'arg_type': 'int',
                },
            },
            'value': {'algorithms_to_apply': [ALGORITHM_NAME_THRESHOLD]},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize('brand_id', [BRAND_ID_1, BRAND_ID_2])
@pytest.mark.now(MOCK_NOW)
async def test_experiment_differ_by_brand_id(
        save_autodisabled_products_to_db,
        taxi_eats_retail_products_autodisable,
        to_utc_datetime,
        # parametrize
        brand_id,
):
    autodisabled_products = gen_autodisabled_products(to_utc_datetime)
    save_autodisabled_products_to_db([autodisabled_products[0]])

    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': PLACE_ID_1,
            'brand_id': brand_id,
            'origin_ids': [ORIGIN_ID_1],
        },
    )

    assert response.status == 200

    expected_autodisable_info = [
        {'is_available': False, 'origin_id': 'item_origin_1'},
    ]
    if brand_id == BRAND_ID_2:
        # for BRAND_ID_2 enabled_algorithms is empty,
        # so autodisable won't be applied
        expected_autodisable_info[0]['is_available'] = True

    actual_autodisable_info = response.json()['autodisable_info']
    assert actual_autodisable_info == expected_autodisable_info


@pytest.mark.experiments3(
    name='eats_retail_products_autodisable_algorithms',
    consumers=['eats-retail-products-autodisable/algorithms'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'algorithms_to_apply': []},
    clauses=[
        {
            'title': 'Title',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': DEVICE_ID_1,
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                },
            },
            'value': {'algorithms_to_apply': [ALGORITHM_NAME_THRESHOLD]},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize('device_id', [DEVICE_ID_1, DEVICE_ID_2])
@pytest.mark.now(MOCK_NOW)
async def test_experiment_differ_by_device_id(
        save_autodisabled_products_to_db,
        taxi_eats_retail_products_autodisable,
        to_utc_datetime,
        # parametrize
        device_id,
):
    autodisabled_products = gen_autodisabled_products(to_utc_datetime)
    save_autodisabled_products_to_db([autodisabled_products[0]])

    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': PLACE_ID_1,
            'brand_id': BRAND_ID_1,
            'device_id': device_id,
            'origin_ids': [ORIGIN_ID_1],
        },
    )

    assert response.status == 200

    expected_autodisable_info = [
        {'is_available': False, 'origin_id': 'item_origin_1'},
    ]
    if device_id == DEVICE_ID_2:
        # for DEVICE_ID_2 enabled_algorithms is empty,
        # so autodisable won't be applied
        expected_autodisable_info[0]['is_available'] = True

    actual_autodisable_info = response.json()['autodisable_info']
    assert actual_autodisable_info == expected_autodisable_info


def set_default_experiment(experiments3):
    experiments3.add_config(
        name='eats_retail_products_autodisable_algorithms',
        consumers=['eats-retail-products-autodisable/algorithms'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'algorithms_to_apply': [ALGORITHM_NAME_THRESHOLD]},
    )


def gen_autodisabled_products(to_utc_datetime):
    return [
        models.AutodisabledProduct(
            place_id=PLACE_ID_1,
            origin_id=ORIGIN_ID_1,
            force_unavailable_until=to_utc_datetime(
                UNAVAILABLE_UNTIL_IN_FUTURE,
            ),
            algorithm_name=ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        models.AutodisabledProduct(
            place_id=PLACE_ID_1,
            origin_id=ORIGIN_ID_2,
            force_unavailable_until=to_utc_datetime(
                UNAVAILABLE_UNTIL_IN_FUTURE,
            ),
            algorithm_name=ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
    ]


# pylint: disable=invalid-name
def gen_autodisabled_products_for_two_places(to_utc_datetime):
    return [
        models.AutodisabledProduct(
            place_id=PLACE_ID_1,
            origin_id=ORIGIN_ID_1,
            force_unavailable_until=to_utc_datetime(
                UNAVAILABLE_UNTIL_IN_FUTURE,
            ),
            algorithm_name=ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        models.AutodisabledProduct(
            place_id=PLACE_ID_2,
            origin_id=ORIGIN_ID_1,
            force_unavailable_until=to_utc_datetime(
                UNAVAILABLE_UNTIL_IN_FUTURE,
            ),
            algorithm_name=ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
    ]
