# pylint: disable=no-member
import pytest

from grocery.catalog.api import export_data_pb2
from grocery.catalog.external import layout_item_pb2

from grocery_tasks.market_suggest.export_layout_items import run


MARKET_SUGGEST_SETTINGS = pytest.mark.config(
    GROCERY_MARKET_SUGGEST_SETTINGS={
        'yt-path': (
            '//home/lavka/testing/services/grocery-tasks/market/suggest'
        ),
        'items-limit': 200,
        'categories-keyset': 'virtual_catalog',
    },
)
TRANSLATIONS = pytest.mark.translations(
    virtual_catalog={'virtual_category_title_1': {'ru': 'Категория-1'}},
)


def _make_export_data_pb(
        virtual_category_id,
        virtual_category_title,
        layouts_ids=None,
        products_ids=None,
):
    virtual_category = layout_item_pb2.VirtualCategory()
    virtual_category.id = virtual_category_id
    virtual_category.title = virtual_category_title
    if layouts_ids:
        for layout_id in layouts_ids:
            virtual_category.layouts_ids.append(layout_id)
    if products_ids:
        for product_id in products_ids:
            virtual_category.products_ids.append(product_id)
    return export_data_pb2.ExportData(virtual_category=virtual_category)


def _check_virtual_category(
        row,
        *,
        item_id='virtual-category-1',
        title='Категория-1',
        layouts_ids=[],
        products_ids=[],
):
    assert row['item_id'.encode()] == item_id.encode()
    assert export_data_pb2.ExportData.FromString(
        row['data'.encode()],
    ) == _make_export_data_pb(item_id, title, layouts_ids, products_ids)


def _make_product_link(product_id, categories_ids):
    return {'product_id': product_id, 'categories_ids': categories_ids}


@MARKET_SUGGEST_SETTINGS
@TRANSLATIONS
async def test_existing_virtual_category_included(
        patch,
        mockserver,
        load_json,
        cron_context,
        overlord_catalog,
        grocery_products,
):
    """ Проверяет, что виртуальная категория выгружается в YT в искомом
        proto-формате. """

    @patch('grocery_tasks.market_suggest.export_layout_items._yt_upload')
    async def yt_upload(context, entries):
        pass

    grocery_products.add_virtual_category(test_id='1')

    await run(cron_context)

    entries = yt_upload.call['entries']

    assert len(entries) == 1
    _check_virtual_category(entries[0])


@MARKET_SUGGEST_SETTINGS
async def test_virtual_category_not_included_without_translation(
        patch,
        mockserver,
        load_json,
        cron_context,
        overlord_catalog,
        grocery_products,
):
    """ Проверяет, что категория без локализованного названия в танкере не
        выгружается. """

    @patch('grocery_tasks.market_suggest.export_layout_items._yt_upload')
    async def yt_upload(context, entries):
        pass

    grocery_products.add_virtual_category(test_id='1')

    await run(cron_context)

    entries = yt_upload.call['entries']
    assert not entries


@MARKET_SUGGEST_SETTINGS
@TRANSLATIONS
@pytest.mark.parametrize(
    'test_layouts_ids',
    [
        pytest.param([], id='no layouts'),
        pytest.param(['1'], id='one layout'),
        pytest.param(['1', '2', '3'], id='several layouts'),
    ],
)
async def test_virtual_category_included_with_layouts(
        patch,
        mockserver,
        load_json,
        cron_context,
        overlord_catalog,
        grocery_products,
        test_layouts_ids,
):
    # Проверяет, что для категории выгружаются сетки, в которых она есть.

    @patch('grocery_tasks.market_suggest.export_layout_items._yt_upload')
    async def yt_upload(context, entries):
        pass

    grocery_products.add_virtual_category(test_id='1')

    layouts = []
    for test_layout_id in test_layouts_ids:
        layouts.append(grocery_products.add_layout(test_id=test_layout_id))
    for num, layout in enumerate(layouts, start=1):
        layout.add_category_group(str(num)).add_virtual_category('1')

    await run(cron_context)

    entries = yt_upload.call['entries']
    assert len(entries) == 1
    _check_virtual_category(
        entries[0],
        layouts_ids=list(map(lambda layout: layout.layout_id, layouts)),
    )


@MARKET_SUGGEST_SETTINGS
@TRANSLATIONS
@pytest.mark.parametrize(
    'products_ids',
    [
        pytest.param([], id='no products'),
        pytest.param(['product-1'], id='one products'),
        pytest.param(
            ['product-1', 'product-2', 'product-3'], id='several products',
        ),
    ],
)
async def test_virtual_category_included_with_products(
        patch,
        mockserver,
        load_json,
        cron_context,
        overlord_catalog,
        grocery_products,
        products_ids,
):
    # Проверяет, что для категории выгружаются товары, которые в ней есть.

    @patch('grocery_tasks.market_suggest.export_layout_items._yt_upload')
    async def yt_upload(context, entries):
        pass

    products_links = []
    for product_id in products_ids:
        products_links.append(
            {'product_id': product_id, 'categories_ids': ['subcategory-1']},
        )

    overlord_catalog.add_products_links(new_products_links=products_links)
    virtual_category = grocery_products.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory-1')

    await run(cron_context)

    entries = yt_upload.call['entries']

    assert len(entries) == 1
    _check_virtual_category(entries[0], products_ids=products_ids)
