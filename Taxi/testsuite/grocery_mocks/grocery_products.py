import copy
import json

import pytest

LAYOUT_ID = 'layout-{}'

CATEGORY_GROUP_ID = 'category-group-{}'
CATEGORY_GROUP_TANKER = 'category_group_title_{}'
CATEGORY_GROUP_SHORT_TANKER = 'category_group_short_title_{}'
CATEGORY_GROUP_IMAGE = 'image-group-{}'

VIRTUAL_CATEGORY_ID = 'virtual-category-{}'
VIRTUAL_CATEGORY_ALIAS = 'virtual-category-{}-alias'
VIRTUAL_CATEGORY_TANKER = 'virtual_category_title_{}'
VIRTUAL_CATEGORY_SHORT_TANKER = 'virtual_category_short_title_{}'
VIRTUAL_CATEGORY_IMAGE = 'image-category-{}'


def _safe_json_parse(data):
    try:
        data = json.loads(data)
        if isinstance(data, dict):
            return data
    except ValueError:
        return {}
    return {}


class Layout:
    def __init__(self, test_id, grocery_products, meta=None):
        self._layout_id = LAYOUT_ID.format(test_id)
        self._grocery_products = grocery_products
        self._meta = meta
        if self._meta is None:
            self._meta = '{"layout-meta-property": "layout-meta-value"}'
        self._groups = {}
        self._group_ids_ordered = []

    def add_category_group(
            self,
            *,
            test_id,
            add_short_title=False,
            image=None,
            item_meta=None,
            layout_meta=None,
            title_tanker_key=None,
    ):
        category_group = CategoryGroup(
            test_id=test_id,
            grocery_products=self._grocery_products,
            add_short_title=add_short_title,
            image=image,
            item_meta=item_meta,
            layout_meta=layout_meta,
            title_tanker_key=title_tanker_key,
        )
        assert category_group.category_group_id not in self._groups

        self._group_ids_ordered.append(category_group.category_group_id)
        self._groups[category_group.category_group_id] = category_group
        self._grocery_products.add_category_group(category_group)
        return category_group

    def get_data_json(self):
        layout_data = {'layout_id': self._layout_id, 'meta': self._meta}

        if self._group_ids_ordered:
            groups = []
            for group_id in self._group_ids_ordered:
                groups.append(self._groups[group_id].get_layout_data_json())
            layout_data['groups'] = groups

        return layout_data

    def get_pigeon_data_json(self):
        layout_data = {
            'layout_id': self._layout_id,
            'meta': _safe_json_parse(self._meta),
        }

        groups = []
        for group_id in self._group_ids_ordered:
            groups.append(self._groups[group_id].get_pigeon_layout_data_json())
        layout_data['groups'] = groups

        return layout_data

    @property
    def layout_id(self):
        return self._layout_id

    @property
    def group_ids_ordered(self):
        return self._group_ids_ordered

    @property
    def groups(self):
        return self._groups


class CategoryGroup:
    def __init__(
            self,
            test_id,
            grocery_products,
            add_short_title=False,
            image=None,
            item_meta=None,
            layout_meta=None,
            title_tanker_key=None,
    ):
        self._category_group_id = CATEGORY_GROUP_ID.format(test_id)
        self._short_title_tanker_key = (
            CATEGORY_GROUP_SHORT_TANKER.format(test_id)
            if add_short_title
            else None
        )
        self._title_tanker_key = (
            title_tanker_key
            if title_tanker_key
            else CATEGORY_GROUP_TANKER.format(test_id)
        )
        self._item_meta = item_meta
        if self._item_meta is None:
            self._item_meta = (
                '{"item-meta-property": "item-meta-value-'
                + self._category_group_id
                + '"}'
            )
        self._layout_meta = layout_meta
        if self._layout_meta is None:
            self._layout_meta = (
                '{"layout-meta-property": "layout-meta-value-'
                + self._category_group_id
                + '"}'
            )
        self._properties = {
            'item_meta': self._item_meta,
            'layout_meta': self._layout_meta,
        }
        self._size = '2x2'
        self._dimensions = {'height': 2, 'width': 6}
        self._categories = {}
        self._category_ids_ordered = []
        self._grocery_products = grocery_products
        self._image_url_template = image
        if self._image_url_template is None:
            self._image_url_template = CATEGORY_GROUP_IMAGE.format(test_id)

    def add_virtual_category(
            self,
            *,
            test_id,
            item_meta=None,
            layout_meta=None,
            add_short_title=False,
            alias=None,
            deep_link=None,
            special_category=None,
            title_tanker_key=None,
    ):
        virtual_category = VirtualCategory(
            test_id=test_id,
            item_meta=item_meta,
            layout_meta=layout_meta,
            add_short_title=add_short_title,
            alias=alias,
            deep_link=deep_link,
            special_category=special_category,
            title_tanker_key=title_tanker_key,
        )
        assert virtual_category.virtual_category_id not in self._categories

        self._category_ids_ordered.append(virtual_category.virtual_category_id)
        self._categories[
            virtual_category.virtual_category_id
        ] = virtual_category
        self._grocery_products.add_virtual_category(virtual_category)
        return virtual_category

    def get_categories(self):
        return self._categories.values()

    @property
    def categories(self):
        return self._categories

    def get_data_json(self):
        ret = {
            'category_group_id': self._category_group_id,
            'title_tanker_key': self._title_tanker_key,
            'item_meta': self._item_meta,
        }
        if self._short_title_tanker_key:
            ret['short_title_tanker_key'] = self._short_title_tanker_key
        return ret

    def get_pigeon_data_json(self):
        ret = self.get_data_json()
        ret['item_meta'] = _safe_json_parse(self._item_meta)
        return ret

    def get_layout_data_json(self):
        categories = []
        for category_id in self._category_ids_ordered:
            categories.append(
                self._categories[category_id].get_layout_data_json(),
            )

        return {
            'category_group_id': self._category_group_id,
            'image_url_template': self._image_url_template,
            'layout_meta': self._layout_meta,
            'dimensions': self._dimensions,
            'categories': categories,
        }

    def get_pigeon_layout_data_json(self):
        categories = []
        for category_id in self._category_ids_ordered:
            categories.append(
                self._categories[category_id].get_pigeon_layout_data_json(),
            )

        return {
            'category_group_id': self._category_group_id,
            'image_url_template': self._image_url_template,
            'layout_meta': _safe_json_parse(self._layout_meta),
            'dimensions': self._dimensions,
            'categories': categories,
        }

    @property
    def category_group_id(self):
        return self._category_group_id

    @property
    def layout_meta(self):
        return self._layout_meta

    @layout_meta.setter
    def layout_meta(self, value):
        self._layout_meta = value


class VirtualCategory:
    def __init__(
            self,
            test_id,
            item_meta=None,
            layout_meta=None,
            add_short_title=False,
            alias=None,
            deep_link=None,
            special_category=None,
            title_tanker_key=None,
            pigeon_id_prefix='',
    ):
        self._test_id = test_id
        self._virtual_category_id = VIRTUAL_CATEGORY_ID.format(test_id)
        self._pigeon_id_prefix = pigeon_id_prefix
        self._alias = alias
        if self._alias is None:
            self._alias = VIRTUAL_CATEGORY_ALIAS.format(test_id)
        self._short_title_tanker_key = (
            VIRTUAL_CATEGORY_SHORT_TANKER.format(test_id)
            if add_short_title
            else None
        )
        self._title_tanker_key = (
            VIRTUAL_CATEGORY_TANKER.format(test_id)
            if title_tanker_key is None
            else title_tanker_key
        )
        self._subcategories = []
        self._item_meta = item_meta
        self._layout_meta = layout_meta
        if self._layout_meta is None:
            self._layout_meta = (
                '{"layout-meta-property": "layout-meta-value-'
                + self._virtual_category_id
                + '"}'
            )
        if self._item_meta is None:
            self._item_meta = (
                '{"item-meta-property": "item-meta-value-'
                + self._virtual_category_id
                + '"}'
            )
        self._properties = {
            'item_meta': self._item_meta,
            'layout_meta': self._layout_meta,
        }
        self._deep_link = deep_link
        self._special_category = special_category
        self._images = []

    def add_image(self, *, image=None, dimensions=None):
        image_url_template = image
        if image_url_template is None:
            image_url_template = VIRTUAL_CATEGORY_IMAGE.format(self._test_id)
        if dimensions is None:
            image_dimensions = [{'width': 2, 'height': 2}]
        else:
            image_dimensions = copy.deepcopy(dimensions)
        self._images.append(
            {
                'image_url_template': image_url_template,
                'dimensions': image_dimensions,
            },
        )

    def add_subcategory(self, *, subcategory_id):
        self._subcategories.append({'category_id': subcategory_id})

    def get_data_json(self):
        ret = {
            'virtual_category_id': self._virtual_category_id,
            'alias': self._alias,
            'title_tanker_key': self._title_tanker_key,
            'subcategories': self._subcategories,
            'item_meta': self._item_meta,
        }
        if self._short_title_tanker_key:
            ret['short_title_tanker_key'] = self._short_title_tanker_key
        if self._deep_link:
            ret['deep_link'] = self._deep_link
        if self._special_category:
            ret['special_category'] = self._special_category
        return ret

    def get_pigeon_data_json(self):
        ret = self.get_data_json()
        ret['item_meta'] = _safe_json_parse(self._item_meta)
        ret['virtual_category_id'] = (
            self._pigeon_id_prefix + ret['virtual_category_id']
        )
        return ret

    def get_layout_data_json(self):
        if not self._images:
            self.add_image()
        return {
            'virtual_category_id': self._virtual_category_id,
            'images': self._images,
            'layout_meta': self._layout_meta,
        }

    def get_pigeon_layout_data_json(self):
        ret = self.get_layout_data_json()
        ret['layout_meta'] = _safe_json_parse(self._layout_meta)
        ret['virtual_category_id'] = (
            self._pigeon_id_prefix + ret['virtual_category_id']
        )
        return ret

    @property
    def virtual_category_id(self):
        return self._virtual_category_id

    @property
    def item_meta(self):
        return self._item_meta

    @item_meta.setter
    def item_meta(self, value):
        self._item_meta = value

    @property
    def layout_meta(self):
        return self._layout_meta

    @layout_meta.setter
    def layout_meta(self, value):
        self._layout_meta = value


# мокаем ответ ручек grocery-products и grocery-menu. После переезда
# только на grocery-menu удалим мок grocery-products.
@pytest.fixture(name='grocery_products', autouse=True)
def mock_grocery_products(mockserver):
    layouts = {}
    category_groups = {}
    virtual_categories = {}

    def _get_cursor_answer(request, data, get_object, response_field):
        if 'cursor' in request.json:
            cursor = request.json['cursor']
        else:
            cursor = 0
        limit = request.json['limit']

        response_data = []
        response_cursor = min(cursor + limit, len(data))
        for item_id in sorted(data.keys())[cursor:response_cursor]:
            response_data.append(get_object(data[item_id]))
        return {'cursor': response_cursor, response_field: response_data}

    @mockserver.json_handler(
        '/grocery-products/internal/v1/products/v1/categories-data',
    )
    def _mock_grocery_products_categories_data(request):
        return _get_cursor_answer(
            request,
            virtual_categories if context.products_response_enabled else {},
            VirtualCategory.get_data_json,
            'categories',
        )

    @mockserver.json_handler(
        '/grocery-products/internal/v1/products/v1/groups-data',
    )
    def _mock_grocery_products_groups_data(request):
        return _get_cursor_answer(
            request,
            category_groups if context.products_response_enabled else {},
            CategoryGroup.get_data_json,
            'groups',
        )

    @mockserver.json_handler(
        '/grocery-products/internal/v1/products/v2/layouts-data',
    )
    def _mock_grocery_products_layouts_data(request):
        return _get_cursor_answer(
            request,
            layouts if context.products_response_enabled else {},
            Layout.get_data_json,
            'layouts',
        )

    @mockserver.json_handler(
        '/grocery-menu/internal/v1/menu/v1/categories-data',
    )
    def _mock_grocery_menu_categories_data(request):
        return _get_cursor_answer(
            request,
            virtual_categories if context.menu_response_enabled else {},
            VirtualCategory.get_pigeon_data_json,
            'categories',
        )

    @mockserver.json_handler('/grocery-menu/internal/v1/menu/v1/groups-data')
    def _mock_grocery_menu_groups_data(request):
        return _get_cursor_answer(
            request,
            category_groups if context.menu_response_enabled else {},
            CategoryGroup.get_pigeon_data_json,
            'groups',
        )

    @mockserver.json_handler('/grocery-menu/internal/v1/menu/v1/layouts-data')
    def _mock_grocery_menu_layouts_data(request):
        return _get_cursor_answer(
            request,
            layouts if context.menu_response_enabled else {},
            Layout.get_pigeon_data_json,
            'layouts',
        )

    class Context:
        def __init__(self):
            self._menu_response_enabled = True
            self._products_response_enabled = True

        def add_virtual_category(self, virtual_category):
            if virtual_category.virtual_category_id in virtual_categories:
                old_virtual_category = virtual_categories[
                    virtual_category.virtual_category_id
                ]
                assert (
                    old_virtual_category.get_data_json()
                    == virtual_category.get_data_json()
                )
            else:
                virtual_categories[
                    virtual_category.virtual_category_id
                ] = virtual_category

        def add_category_group(self, category_group):
            assert category_group.category_group_id not in category_groups
            category_groups[category_group.category_group_id] = category_group

        def add_layout(self, *, test_id, meta=None):
            layout = Layout(test_id=test_id, grocery_products=self, meta=meta)
            assert layout.layout_id not in layouts

            layouts[layout.layout_id] = layout
            return layout

        def get_layout(self, layout_id):
            assert layout_id in layouts
            return layouts[layout_id]

        @property
        def menu_response_enabled(self):
            return self._menu_response_enabled

        @property
        def products_response_enabled(self):
            return self._products_response_enabled

        @menu_response_enabled.setter
        def menu_response_enabled(self, value):
            self._menu_response_enabled = value

        @products_response_enabled.setter
        def products_response_enabled(self, value):
            self._products_response_enabled = value

    context = Context()
    return context
