import pytest

from tests_grocery_menu.plugins import pigeon_layout as pigeon


LAYOUT_LEGACY_ID = 'layout-id-{}'
LAYOUT_ALIAS = 'layout-alias-{}'
LONG_TITLE = 'long-title-{}'
SHORT_TITLE = 'short-title-{}'
DEFAULT_META = {'test-key': 'test-value'}
GROUP_IMAGE = 'group-image-{}'
CATEGORY_IMAGE = 'category-image-{}'

GROUP_DIMENSIONS = {'height': 2, 'width': 6}


def format_dimension(size):
    return {'height': size, 'width': size}


def format_image_with_size(category_id, size):
    return {
        'imageUrlTemplate': CATEGORY_IMAGE.format(category_id),
        'dimensions': format_dimension(size),
    }


def format_pigeon_layout_category(category_id):
    return {
        'id': category_id,
        'layoutMeta': DEFAULT_META,
        'images': [format_image_with_size(category_id, 1)],
    }


def format_pigeon_layout_group(group_id):
    return {
        'id': group_id,
        'imageUrlTemplate': GROUP_IMAGE.format(group_id),
        'dimensions': format_dimension(1),
        'layoutMeta': DEFAULT_META,
        'categories': [format_pigeon_layout_category(group_id)],
    }


def format_pigeon_layout(layout_id):
    return {
        'id': layout_id,
        'legacyId': LAYOUT_LEGACY_ID.format(layout_id),
        'alias': LAYOUT_ALIAS.format(layout_id),
        'longTitleTankerKey': {
            'keyset': 'test-keyset',
            'key': LONG_TITLE.format(layout_id),
        },
        'shortTitleTankerKey': {
            'keyset': 'test-keyset',
            'key': SHORT_TITLE.format(layout_id),
        },
        'meta': DEFAULT_META,
        'groups': [format_pigeon_layout_group(1)],
    }


def format_layout_image(category_id):
    return {
        'image_url_template': CATEGORY_IMAGE.format(category_id),
        'dimensions': [format_dimension(1)],
    }


def format_menu_layout_category(category_id):
    return {
        'virtual_category_id': pigeon.CATEGORY_LEGACY_ID.format(category_id),
        'layout_meta': DEFAULT_META,
        'images': [format_layout_image(category_id)],
    }


def format_menu_layout_group(group_id, categories_count):
    return {
        'category_group_id': pigeon.GROUP_LEGACY_ID.format(group_id),
        'image_url_template': GROUP_IMAGE.format(group_id),
        'layout_meta': DEFAULT_META,
        'dimensions': GROUP_DIMENSIONS,
        'categories': [
            format_menu_layout_category(i + 1) for i in range(categories_count)
        ],
    }


def format_menu_layout(layout_id, groups_count, categories_count):
    return {
        'layout_id': LAYOUT_LEGACY_ID.format(layout_id),
        'meta': DEFAULT_META,
        'groups': [
            format_menu_layout_group(i + 1, categories_count)
            for i in range(groups_count)
        ],
    }


@pytest.mark.parametrize(
    'add_group,add_category', [(True, True), (True, False), (False, False)],
)
async def test_layouts(taxi_grocery_menu, mockserver, add_group, add_category):
    @mockserver.json_handler('/pigeon/internal/catalog/v1/layouts')
    def _mock_layouts(request):
        return {'cursor': 0, 'items': [format_pigeon_layout(1)]}

    @mockserver.json_handler('/pigeon/internal/catalog/v1/groups')
    def _mock_groups(request):
        return {
            'cursor': 0,
            'items': [pigeon.format_pigeon_group(1)] if add_group else [],
        }

    @mockserver.json_handler('/pigeon/internal/catalog/v1/categories')
    def _mock_categories(request):
        return {
            'cursor': 0,
            'items': (
                [pigeon.format_pigeon_category(1)] if add_category else []
            ),
        }

    response = await taxi_grocery_menu.post(
        '/internal/v1/menu/v1/layouts-data', json={'limit': 1, 'cursor': 0},
    )
    assert response.status_code == 200
    assert response.json()['layouts'] == [
        format_menu_layout(1, 1 if add_group else 0, 1 if add_category else 0),
    ]


async def test_layouts_data_chunked(taxi_grocery_menu, mockserver):
    @mockserver.json_handler('/pigeon/internal/catalog/v1/layouts')
    def _mock_layouts(request):
        return {
            'cursor': 0,
            'items': [format_pigeon_layout(i) for i in range(3)],
        }

    response_len = [2, 1, 0]
    layouts = []
    limit = 2
    cursor = 0
    for length in response_len:
        response = await taxi_grocery_menu.post(
            '/internal/v1/menu/v1/layouts-data',
            json={'limit': limit, 'cursor': cursor},
        )

        assert response.status_code == 200
        if length == 0:
            assert cursor == response.json()['cursor']
        else:
            cursor = response.json()['cursor']
        assert len(response.json()['layouts']) == length
        layouts.extend(response.json()['layouts'])

    layouts_ids_set = set()
    prev_layout_id = None
    for item in layouts:
        layout_id = item['layout_id']
        layouts_ids_set.add(layout_id)
        if prev_layout_id:
            assert layout_id > prev_layout_id
        prev_layout_id = layout_id

    assert len(layouts) == len(layouts_ids_set)
    assert len(layouts) == sum(response_len)
