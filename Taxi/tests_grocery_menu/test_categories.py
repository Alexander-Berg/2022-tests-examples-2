import pytest

from tests_grocery_menu.plugins import pigeon_layout as pigeon


def format_menu_category(category_id, subcategories=None):
    return {
        'virtual_category_id': pigeon.CATEGORY_LEGACY_ID.format(category_id),
        'alias': pigeon.CATEGORY_ALIAS.format(category_id),
        'title_tanker_key': pigeon.LONG_TITLE.format(category_id),
        'short_title_tanker_key': pigeon.SHORT_TITLE.format(category_id),
        'item_meta': pigeon.DEFAULT_META,
        'deep_link': pigeon.DEEPLINK.format(category_id),
        'special_category': pigeon.SPECIAL_CATEGORY.format(category_id),
        'subcategories': [{'category_id': subcat} for subcat in subcategories],
    }


async def test_categories(taxi_grocery_menu, overlord_catalog, mockserver):
    @mockserver.json_handler('/pigeon/internal/catalog/v1/categories')
    def _mock_categories(request):
        return {
            'cursor': 0,
            'items': [
                pigeon.format_pigeon_category(
                    1, ['pigeon_id', 'pigeon_id_not_found'],
                ),
            ],
        }

    overlord_catalog.add_category_data(
        category_id='wms_id', external_id='pigeon_id', title='test-1',
    )

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/categories-data', json={'limit': 1, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['categories'] == [
        format_menu_category(1, ['wms_id']),
    ]


async def test_categories_data_chunked(taxi_grocery_menu, mockserver):
    @mockserver.json_handler('/pigeon/internal/catalog/v1/categories')
    def _mock_categories(request):
        return {
            'cursor': 0,
            'items': [pigeon.format_pigeon_category(i) for i in range(4)],
        }

    response_len = [2, 2, 0]
    categories = []
    limit = 2
    cursor = 0
    for length in response_len:
        response = await taxi_grocery_menu.post(
            '/internal/v1/menu/v1/categories-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['categories']) == length
        categories.extend(response.json()['categories'])

    categories_ids_set = set()
    prev_category_id = None
    for item in categories:
        category_id = item['virtual_category_id']
        categories_ids_set.add(category_id)
        if prev_category_id:
            assert category_id > prev_category_id
        prev_category_id = category_id

    assert len(categories) == len(categories_ids_set)
    assert len(categories) == sum(response_len)


@pytest.mark.config(
    GROCERY_PRODUCTS_SPECIAL_CATEGORY_MAP={
        pigeon.CATEGORY_LEGACY_ID.format(1): 'custom-special-category',
    },
)
async def test_special_category_by_config(taxi_grocery_menu, mockserver):
    @mockserver.json_handler('/pigeon/internal/catalog/v1/categories')
    def _mock_categories(request):
        return {'cursor': 0, 'items': [pigeon.format_pigeon_category(1)]}

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/categories-data', json={'limit': 1, 'cursor': 0},
    )
    assert response.status_code == 200
    assert (
        response.json()['categories'][0]['special_category']
        == 'custom-special-category'
    )
