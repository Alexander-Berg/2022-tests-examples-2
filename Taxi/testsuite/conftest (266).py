# pylint: disable=redefined-outer-name
import pytest

# root conftest for service eats-picker-item-categories
pytest_plugins = ['eats_picker_item_categories_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_picker_item_categories'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_item(get_cursor):
    def do_create_item(place_id=1, eats_item_id='1', synchronized_at=None):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_item_categories.items'
            '(place_id, eats_item_id, synchronized_at) '
            'VALUES(%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))'
            'RETURNING id',
            [place_id, eats_item_id, synchronized_at],
        )

        item_id = cursor.fetchone()[0]
        return item_id

    return do_create_item


@pytest.fixture()
def create_category(get_cursor):
    def do_create_category(
            public_id='category-1',
            name='Category Name',
            public_parent_id=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_item_categories.categories'
            '(public_id, name, public_parent_id) '
            'VALUES(%s, %s, %s)'
            'RETURNING id',
            [public_id, name, public_parent_id],
        )

        category_id = cursor.fetchone()[0]
        return category_id

    return do_create_category


@pytest.fixture()
def create_item_category(get_cursor):
    def do_create_item_category(
            item_id, category_id, level, hierarchy_number=0,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_item_categories.item_categories'
            '(item_id, category_id, level, hierarchy_number) '
            'VALUES(%s, %s, %s, %s)',
            [item_id, category_id, level, hierarchy_number],
        )

    return do_create_item_category


@pytest.fixture()
def get_categories_for_all_items(get_cursor):
    def do_get_categories_for_all_items():
        cursor = get_cursor()
        cursor.execute(
            'SELECT items.eats_item_id, categories.name, '
            'categories.public_id, categories.public_parent_id '
            'FROM eats_picker_item_categories.categories categories '
            'INNER JOIN eats_picker_item_categories.item_categories '
            'item_categories '
            'ON categories.id = item_categories.category_id '
            'INNER JOIN eats_picker_item_categories.items items '
            'ON item_categories.item_id = items.id '
            'ORDER BY items.eats_item_id, item_categories.hierarchy_number, '
            'item_categories.level',
        )
        return cursor.fetchall()

    return do_get_categories_for_all_items


@pytest.fixture()
def get_item_categories(get_cursor):
    def do_get_item_categories(eats_item_id: str):
        cursor = get_cursor()
        cursor.execute(
            'SELECT items.eats_item_id, categories.public_id, '
            'categories.name, categories.public_parent_id, '
            'item_categories.hierarchy_number, item_categories.level '
            'FROM eats_picker_item_categories.item_categories '
            'INNER JOIN eats_picker_item_categories.items '
            'ON items.id = item_categories.item_id '
            'INNER JOIN eats_picker_item_categories.categories '
            'ON categories.id = item_categories.category_id '
            'WHERE items.eats_item_id = %s '
            'ORDER BY item_categories.hierarchy_number, '
            'item_categories.level',
            [eats_item_id],
        )
        return cursor.fetchall()

    return do_get_item_categories
