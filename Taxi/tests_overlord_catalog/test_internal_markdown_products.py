import pytest

from testsuite.utils import ordered_object

# test POST /internal/v1/catalog/v1/category-tree/list
# get markdown products for all depots
@pytest.mark.pgsql(
    'overlord_catalog', files=['menu.sql', 'refresh_wms_views.sql'],
)
async def test_markdown_products_list(
        taxi_overlord_catalog, pgsql, load_json, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-menu.json', 'gdepots-zones-menu.json',
    )
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/markdown-products',
        json={'limit': 100, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['cursor'] == 2
    ordered_object.assert_eq(
        response.json()['depot_markdown_products'],
        [
            load_json('markdown_products_list_response_1.json'),
            load_json('markdown_products_list_response_2.json'),
        ],
        ['products'],
    )


# test POST /internal/v1/catalog/v1/category-tree/list
# get markdown products for every depot apart
@pytest.mark.pgsql(
    'overlord_catalog', files=['menu.sql', 'refresh_wms_views.sql'],
)
async def test_markdown_products_list_consistently(
        taxi_overlord_catalog, load_json, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-menu.json', 'gdepots-zones-menu.json',
    )
    response_length = [1, 1, 0]
    expected_response = [
        'markdown_products_list_response_1.json',
        'markdown_products_list_response_2.json',
    ]
    cursor = 0
    for length in response_length:
        response = await taxi_overlord_catalog.post(
            '/internal/v1/catalog/v1/markdown-products',
            json={'limit': 1, 'cursor': cursor},
        )
        assert response.status_code == 200
        if length == 0:
            assert response.json()['cursor'] == cursor
            assert response.json()['depot_markdown_products'] == []
        else:
            ordered_object.assert_eq(
                response.json()['depot_markdown_products'],
                [load_json(expected_response[cursor])],
                ['products'],
            )
            cursor = response.json()['cursor']
