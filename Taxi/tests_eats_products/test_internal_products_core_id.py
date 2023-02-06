import pytest

from tests_eats_products import conftest
from tests_eats_products import utils

HANDLER = '/internal/v2/products/core_id'

CORE_ID_1 = 123
CORE_ID_2 = 456
PUBLIC_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
PUBLIC_ID_2 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'
PUBLIC_ID_3 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003'


@pytest.mark.parametrize(
    ['public_ids', 'expected_ids'],
    (
        pytest.param(
            [PUBLIC_ID_1, PUBLIC_ID_2],
            [
                {'public_id': PUBLIC_ID_1, 'core_id': CORE_ID_1},
                {'public_id': PUBLIC_ID_2, 'core_id': CORE_ID_2},
            ],
            id='all_core_ids',
        ),
        pytest.param(
            [PUBLIC_ID_1, PUBLIC_ID_3],
            [
                {'public_id': PUBLIC_ID_1, 'core_id': CORE_ID_1},
                {'public_id': PUBLIC_ID_3},
            ],
            id='some_core_ids',
        ),
        pytest.param(
            [PUBLIC_ID_3], [{'public_id': PUBLIC_ID_3}], id='no_core_ids',
        ),
        pytest.param([], [], id='empty'),
    ),
)
async def test_internal_products_core_id(
        taxi_eats_products,
        public_ids,
        expected_ids,
        add_place_products_mapping,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1',
                core_id=CORE_ID_1,
                public_id=PUBLIC_ID_1,
            ),
            conftest.ProductMapping(
                origin_id='item_id_2',
                core_id=CORE_ID_2,
                public_id=PUBLIC_ID_2,
            ),
            conftest.ProductMapping(
                origin_id='item_id_3', public_id=PUBLIC_ID_3,
            ),
        ],
    )

    response = await taxi_eats_products.post(
        HANDLER, json={'place_id': utils.PLACE_ID, 'public_ids': public_ids},
    )
    assert response.status_code == 200
    assert response.json()['products_ids'] == expected_ids


async def test_unknown_place(taxi_eats_products):
    response = await taxi_eats_products.post(
        HANDLER,
        json={'place_id': 999, 'public_ids': [PUBLIC_ID_1, PUBLIC_ID_2]},
    )
    assert response.status_code == 404


@pytest.mark.config(EATS_PRODUCTS_CORE_ID_BY_PUBLIC_ID={'max_items': 5})
async def test_internal_products_core_id_too_much_ids(taxi_eats_products):
    count = 10
    response = await taxi_eats_products.post(
        HANDLER,
        json={
            'place_id': utils.PLACE_ID,
            'public_ids': [str(i) for i in range(count)],
        },
    )
    assert response.status_code == 400
