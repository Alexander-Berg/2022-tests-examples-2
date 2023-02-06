import pytest

BASE_V2_URL = '/v2/admin/shortcuts/grocery'

SHORTCUTS_ADMIN_GROCERY_CATEGORIES_MAPPING = {
    'ab64ffec621e4a4e92ed70d7ddc4671b000300010000': 'freekadelki',
}

SHORTCUTS_ADMIN_GROCERY_METACATEGORIES_PROPERTIES = {
    'freekadelki': {
        'image_tags': ['freekadelki_tag'],
        'relevance': 123,
        'title': 'Фрикадельки',
    },
}


@pytest.mark.config(
    SHORTCUTS_ADMIN_CONSTANTS={
        'default_eats_shortcut_color': '',  # not used
        'default_eats_shortcut_image_tag': '',  # not used
        'eats_brand_black_list': [],  # not used
        'default_grocery_shortcut_color': '#AABBCC',
    },
    SHORTCUTS_ADMIN_GROCERY_CATEGORIES_MAPPING={
        **SHORTCUTS_ADMIN_GROCERY_CATEGORIES_MAPPING,
    },
    SHORTCUTS_ADMIN_GROCERY_METACATEGORIES_PROPERTIES={
        **SHORTCUTS_ADMIN_GROCERY_METACATEGORIES_PROPERTIES,
    },
)
async def test_v2_list(taxi_shortcuts_admin, mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/overlord-catalog/admin/categories/v1/search/root',
    )
    def root_mock(_):
        return load_json('grocery_search_root.json')

    @mockserver.json_handler(
        '/overlord-catalog/admin/categories/v1/search/suggest',
    )
    def suggest_mock(req):
        root_categories = {
            root['category_id']
            for root in load_json('grocery_search_root.json')['result']
        }
        assert req.json['root_id'] in root_categories
        return load_json('grocery_search_suggest.json')

    response = await taxi_shortcuts_admin.get(f'{BASE_V2_URL}/list')
    assert response.status_code == 200

    shortcuts = response.json()['shortcuts']
    for shortcut in shortcuts:
        category_id = shortcut['category_id']
        if category_id in SHORTCUTS_ADMIN_GROCERY_CATEGORIES_MAPPING:
            metacategory_id = SHORTCUTS_ADMIN_GROCERY_CATEGORIES_MAPPING[
                category_id
            ]
            properties = SHORTCUTS_ADMIN_GROCERY_METACATEGORIES_PROPERTIES[
                metacategory_id
            ]
            assert shortcut['color'] == '#AABBCC'
            assert shortcut['image_tags'] == properties['image_tags']
            assert shortcut['relevance'] == properties['relevance']
            if 'title' in properties:
                assert shortcut['title'] == properties['title']
