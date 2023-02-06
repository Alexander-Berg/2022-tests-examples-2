import pytest


HANDLER = '/v1/manage/brand/custom_categories_groups/assortments'
BRAND_ID = 1


@pytest.mark.parametrize(
    """
    brand_id,
    custom_group_public_id,
    expected_response_data,
    expected_response_status
    """,
    [
        pytest.param(
            10,
            '33333333-3333-3333-3333-333333333333',
            {'message': 'Brand 10 not found'},
            404,
            id='unknown_brand',
        ),
        pytest.param(
            2,
            '11133333-3333-3333-3333-333333333333',
            {
                'message': (
                    'Custom categories group '
                    '11133333-3333-3333-3333-333333333333 '
                    'not found'
                ),
            },
            404,
            id='unknown_group',
        ),
        pytest.param(
            1,
            '77777777-7777-7777-7777-777777777777',
            {'assortments': []},
            200,
            id='brand_with_given_group_but_without_assortments',
        ),
        pytest.param(
            1,
            '33333333-3333-3333-3333-333333333333',
            {'assortments': ['default_assortment', 'test_1']},
            200,
            id='normal_response',
        ),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_custom_categories_groups_assortments(
        taxi_eats_nomenclature,
        brand_id,
        custom_group_public_id,
        expected_response_status,
        expected_response_data,
):
    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={brand_id}'
        f'&custom_categories_group_id={custom_group_public_id}',
    )
    assert response.status_code == expected_response_status
    assert response.json() == expected_response_data
