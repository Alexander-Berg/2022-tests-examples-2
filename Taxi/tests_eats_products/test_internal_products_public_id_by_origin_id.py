import pytest

from tests_eats_products import conftest
from tests_eats_products import utils

PUBLIC_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
PUBLIC_ID_2 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'


@pytest.mark.parametrize(
    ['origin_ids', 'expected_ids'],
    (
        pytest.param(
            ['item_id_1', 'item_id_2'],
            {'item_id_1': PUBLIC_ID_1, 'item_id_2': PUBLIC_ID_2},
            id='all_public_ids',
        ),
        pytest.param(
            ['item_id_1', 'item_id_1'],
            {'item_id_1': PUBLIC_ID_1},
            id='duplicate_origin_id',
        ),
        pytest.param(
            ['item_id_1', 'item_id_3'],
            {'item_id_1': PUBLIC_ID_1, 'item_id_3': None},
            id='some_public_ids',
        ),
        pytest.param(
            ['item_id_100', 'item_id_101'],
            {'item_id_100': None, 'item_id_101': None},
            id='no_public_ids',
        ),
        pytest.param([], {}, id='empty'),
    ),
)
async def test_internal_products_public_id_by_origin_id(
        taxi_eats_products,
        origin_ids,
        expected_ids,
        add_place_products_mapping,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', public_id=PUBLIC_ID_1,
            ),
            conftest.ProductMapping(
                origin_id='item_id_2', public_id=PUBLIC_ID_2,
            ),
        ],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.PUBLIC_ID_BY_ORIGIN_ID,
        json={'place_id': utils.PLACE_ID, 'origin_ids': origin_ids},
    )
    assert response.status_code == 200

    products_ids = {
        item.get('origin_id'): item.get('public_id')
        for item in response.json()['products_ids']
    }

    assert products_ids == expected_ids


async def test_internal_products_public_id_by_origin_id_unknown_place(
        taxi_eats_products,
):
    response = await taxi_eats_products.post(
        utils.Handlers.PUBLIC_ID_BY_ORIGIN_ID,
        json={'place_id': 2, 'origin_ids': ['item_id_1', 'item_id_2']},
    )
    assert response.status_code == 404


async def test_internal_products_public_id_by_origin_id_empty_mapping(
        taxi_eats_products,
):
    response = await taxi_eats_products.post(
        utils.Handlers.PUBLIC_ID_BY_ORIGIN_ID,
        json={
            'place_id': utils.PLACE_ID,
            'origin_ids': ['item_id_1', 'item_id_2'],
        },
    )
    assert response.status_code == 200

    products_ids = {
        item.get('origin_id'): item.get('public_id')
        for item in response.json()['products_ids']
    }

    assert products_ids == {'item_id_1': None, 'item_id_2': None}


@pytest.mark.parametrize(
    ['count', 'expected_code'],
    (
        pytest.param(1001, 400, id='no_config'),
        pytest.param(
            1001,
            400,
            marks=[
                pytest.mark.config(EATS_PRODUCTS_PUBLIC_ID_BY_ORIGIN_ID={}),
            ],
            id='default_config',
        ),
        pytest.param(
            6,
            400,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_PUBLIC_ID_BY_ORIGIN_ID={'max_items': 5},
                ),
            ],
            id='value_from_config',
        ),
        pytest.param(
            5,
            200,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_PUBLIC_ID_BY_ORIGIN_ID={'max_items': 5},
                ),
            ],
            id='value_from_config_correct_count',
        ),
    ),
)
async def test_internal_products_public_id_by_origin_id_too_much_ids(
        taxi_eats_products, count, expected_code,
):
    response = await taxi_eats_products.post(
        utils.Handlers.PUBLIC_ID_BY_ORIGIN_ID,
        json={
            'place_id': utils.PLACE_ID,
            'origin_ids': ['item_id_' + str(i) for i in range(count)],
        },
    )
    assert response.status_code == expected_code
