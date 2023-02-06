import pytest

from tests_eats_products import conftest

HANDLER = '/internal/v2/products/public_id'

PUBLIC_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
PUBLIC_ID_2 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002'


@pytest.mark.parametrize(
    ['core_ids', 'expected_ids'],
    (
        pytest.param(
            [1, 2],
            [
                {'core_id': 1, 'public_id': PUBLIC_ID_1},
                {'core_id': 2, 'public_id': PUBLIC_ID_2},
            ],
            id='all_public_ids',
        ),
        pytest.param(
            [1, 3],
            [{'core_id': 1, 'public_id': PUBLIC_ID_1}, {'core_id': 3}],
            id='some_public_ids',
        ),
        pytest.param(
            [100, 101],
            [{'core_id': 100}, {'core_id': 101}],
            id='no_public_ids',
        ),
        pytest.param([], [], id='empty'),
    ),
)
async def test_internal_products_public_id(
        taxi_eats_products, core_ids, expected_ids, add_place_products_mapping,
):
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=PUBLIC_ID_1,
            ),
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=PUBLIC_ID_2,
            ),
            conftest.ProductMapping(origin_id='item_id_3', core_id=3),
        ],
    )

    response = await taxi_eats_products.post(
        HANDLER, json={'core_ids': core_ids},
    )
    assert response.status_code == 200
    assert response.json()['products_ids'] == expected_ids
