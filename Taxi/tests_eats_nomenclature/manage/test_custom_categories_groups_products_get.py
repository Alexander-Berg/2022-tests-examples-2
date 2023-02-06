import pytest

HANDLER = '/v1/manage/custom_categories_groups/products'
EMPTY_CATEGORY = 2
FULL_CATEGORY = 1
UNKNOWN_CATEGORY = 123
MAX_LIMIT = 100


async def test_404_custom_category_not_found(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'category_id': UNKNOWN_CATEGORY},
    )
    assert response.status == 404
    assert response.json() == {
        'status': 404,
        'message': 'Custom category not found',
    }


@pytest.mark.parametrize(
    ['category_id', 'end_idx'],
    [
        pytest.param(EMPTY_CATEGORY, 0, id='empty'),
        pytest.param(FULL_CATEGORY, 4, id='full'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_products.sql', 'fill_additional_data.sql'],
)
async def test_200_empty_and_full(
        taxi_eats_nomenclature, load_json, category_id, end_idx,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'category_id': category_id},
    )
    assert response.status == 200
    expected_response = generate_expected_json(
        load_json, 0, end_idx, 0, end_idx, 100, '', 100, '',
    )
    assert response.json() == expected_response


@pytest.mark.parametrize('products_limit', [1, 2, (MAX_LIMIT - 1), MAX_LIMIT])
@pytest.mark.parametrize(
    'product_types_limit', [1, 2, (MAX_LIMIT - 1), MAX_LIMIT],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_products.sql', 'fill_additional_data.sql'],
)
async def test_200_cursor_limit(
        taxi_eats_nomenclature, load_json, products_limit, product_types_limit,
):
    products_cursor = None
    product_types_cursor = None
    start_products_idx = 0
    end_products_idx = products_limit
    start_product_types_idx = 0
    end_product_types_idx = product_types_limit

    while True:
        print(
            f'Current start index: Products:{start_products_idx} '
            f'ProductTypes:{start_product_types_idx}',
        )

        response = await taxi_eats_nomenclature.post(
            HANDLER,
            json={
                'category_id': FULL_CATEGORY,
                'products_limit': products_limit,
                'products_cursor': products_cursor,
                'product_types_limit': product_types_limit,
                'product_types_cursor': product_types_cursor,
            },
        )
        assert response.status_code == 200

        response_json = response.json()
        expected_json = generate_expected_json(
            load_json,
            start_products_idx=start_products_idx,
            end_products_idx=end_products_idx,
            start_product_types_idx=start_product_types_idx,
            end_product_types_idx=end_product_types_idx,
            expected_products_limit=products_limit,
            current_products_cursor=products_cursor,
            expected_product_types_limit=product_types_limit,
            current_product_types_cursor=product_types_cursor,
        )
        assert response_json == expected_json

        products_cursor = response_json['products_cursor']
        product_types_cursor = response_json['product_types_cursor']
        start_products_idx = end_products_idx
        end_products_idx += products_limit
        start_product_types_idx = end_product_types_idx
        end_product_types_idx += product_types_limit

        if (
                len(expected_json['products']) < products_limit
                and len(expected_json['product_types']) < product_types_limit
        ):
            break


def generate_expected_json(
        load_json,
        start_products_idx,
        end_products_idx,
        start_product_types_idx,
        end_product_types_idx,
        expected_products_limit,
        current_products_cursor,
        expected_product_types_limit,
        current_product_types_cursor,
):
    expected_data = load_json('full_response.json')

    expected_data['products'] = expected_data['products'][
        start_products_idx:end_products_idx
    ]
    if expected_data['products']:
        expected_data['products_cursor'] = expected_data['products'][-1][
            'cursor'
        ]
    else:
        expected_data['products_cursor'] = current_products_cursor
    for i in expected_data['products']:
        i.pop('cursor')
    expected_data['products_limit'] = expected_products_limit

    expected_data['product_types'] = expected_data['product_types'][
        start_product_types_idx:end_product_types_idx
    ]
    if expected_data['product_types']:
        expected_data['product_types_cursor'] = expected_data['product_types'][
            -1
        ]['cursor']
    else:
        expected_data['product_types_cursor'] = current_product_types_cursor
    for i in expected_data['product_types']:
        i.pop('cursor')
    expected_data['product_types_limit'] = expected_product_types_limit

    return expected_data
