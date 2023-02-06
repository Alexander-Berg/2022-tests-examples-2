# pylint: disable=redefined-outer-name,protected-access,no-member

import pytest

from arc_market.idx.datacamp.proto.api import ExportMessage_pb2
from arc_market.idx.datacamp.proto.external import Offer_pb2
from arc_market.idx.datacamp.proto.offer import OfferMeta_pb2
from arc_market.idx.datacamp.proto.offer import OfferPictures_pb2

from grocery_tasks.market_idx.export_offers_v2 import (
    _convert_datetime_iso_format_to_timestamp,
)
from grocery_tasks.market_idx.export_offers_v2 import PRICE_FALLBACK_CURRENCY
from grocery_tasks.market_idx.export_offers_v2 import run

YT_BASEPATH = '//home/lavka/testing/services/grocery-tasks/market/offers-v2'

BASE_SETTINGS = {
    'yt-path': YT_BASEPATH,
    'categories-keyset': 'wms_items',
    'products-keyset': 'wms_items',
    'products-long-titles-keyset': 'wms_items',
    'products-ingredients-keyset': 'wms_items',
    'products-description-keyset': 'wms_items',
    'products-origin-country-keyset': 'wms_items',
    'products-tags-keyset': 'wms_items',
    'layout-categories-keyset': 'wms_items',
    'long-title-key-suffix': '_long_title',
    'ingredients-key-suffix': '_ingredients',
    'description-key-suffix': '_description',
    'tags-key-suffix': '_synonyms',
    'categories-name-suffix': '_name',
    'origin-country-pattern': 'country_of_origin.{}',
    'origin-country-delimiter': ' ',
    'tags-split-delimiter': ',',
    'tags-value-delimiter': ', ',
    'overlord-limit': 500,
    'g-products-limit': 500,
    'grocery-menu-limit': 500,
    'categories-path-delimiter': '\\',
}


@pytest.mark.now('2022-06-23T18:04:01')
@pytest.mark.config(
    GROCERY_MARKETIDX_V2_SETTINGS={
        **BASE_SETTINGS,  # type: ignore
        'supported-locales': ['ru', 'en'],
        'tags-representation': 'separately',
    },
)
@pytest.mark.translations(
    wms_items={
        'product-1_long_title': {
            'ru': 'продукт-1 полное название',
            'en': 'product-1 long title',
        },
        'product-1_ingredients': {
            'ru': 'ингредиенты для продукт-1',
            'en': 'product-1 ingredients',
        },
        'product-1_description': {
            'ru': 'описание продукт-1',
            'en': 'product-1-description',
        },
        'product-1_synonyms': {
            'ru': 'синоним-1 продукт-1,синоним-2 продукт-1',
            'en': 'synonym-1 product-1, synonym-2 product-1',
        },
        'product-1_origin_country': {'ru': 'Россия', 'en': 'Russia'},
        'product-2_long_title': {'ru': 'продукт-2 полное название'},
        'product-2_ingredients': {'ru': 'ингредиенты для продукт-2'},
        'product-2_description': {'ru': 'описание продукт-2'},
        'meta-product-1_long_title': {'en': 'meta-product-1 long title'},
        'meta-product-1_ingredients': {'en': 'meta-product-1 ingredients'},
        'country_of_origin.rus': {'ru': 'Россия', 'en': 'Russia'},
        'country_of_origin.blr': {'ru': 'Беларусь'},
    },
)
async def test_prepare_offers(
        patch,
        load_json,
        cron_context,
        overlord_catalog,
        grocery_products,
        mbi_api,
        grocery_depots,
        grocery_menu,
        mocked_time,
):
    grocery_menu.set_return_data(True)

    total_offers = 4

    fill_data(load_json, overlord_catalog, grocery_products, grocery_depots)

    @patch('grocery_tasks.market_idx.export_offers_v2._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']
    assert len(dict_entries) == total_offers

    expected_products = load_json('expected_export_messages.json')

    for export_message in dict_entries:
        export_message_id = export_message['offer_id'.encode()].decode()
        offer_data = ExportMessage_pb2.ExportMessage.FromString(
            export_message['data'.encode()],
        ).offer
        locale = offer_data.original_content.language_tag
        assert (
            _make_offer_data_proto(
                expected_products[export_message_id][locale]['offer'], locale,
            )
            == offer_data
        )


@pytest.mark.translations(
    wms_items={
        'product-1_long_title': {'en': 'product-1 long title'},
        'product-1_ingredients': {'en': 'product-1 ingredients'},
        'product-1_description': {'en': 'product-1-description'},
        'product-1_synonyms': {
            'en': 'synonym-1 product-1, synonym-2 product-1',
        },
        'country_of_origin.rus': {'en': 'Russia'},
    },
)
@pytest.mark.parametrize(
    'tags_representation,navigation_paths',
    [
        pytest.param(
            'separately',
            [
                {
                    'nodes': [
                        {'id': 1},
                        {'name': 'synonym-1 product-1'},
                        {'name': 'synonym-2 product-1'},
                    ],
                },
            ],
            id='separately',
        ),
        pytest.param(
            'together',
            [
                {
                    'nodes': [
                        {
                            'id': 1,
                            'name': 'synonym-1 product-1, synonym-2 product-1',
                        },
                    ],
                },
            ],
            id='together',
        ),
    ],
)
async def test_tags_representation(
        patch,
        load_json,
        cron_context,
        tags_representation,
        navigation_paths,
        overlord_catalog,
        grocery_products,
        mbi_api,
        grocery_depots,
):
    cron_context.config.GROCERY_MARKETIDX_V2_SETTINGS = {
        **BASE_SETTINGS,
        'supported-locales': ['en'],
        'tags-representation': tags_representation,
    }

    fill_data(load_json, overlord_catalog, grocery_products, grocery_depots)

    @patch('grocery_tasks.market_idx.export_offers_v2._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']

    expected_products = load_json('expected_export_messages.json')

    for export_message in dict_entries:
        export_message_id = export_message['offer_id'.encode()].decode()
        offer_data = ExportMessage_pb2.ExportMessage.FromString(
            export_message['data'.encode()],
        ).offer
        locale = offer_data.original_content.language_tag

        assert (
            _make_offer_data_proto(
                expected_products[export_message_id][locale]['offer'],
                locale,
                navigation_paths,
            )
            == offer_data
        )


@pytest.mark.config(
    GROCERY_MARKETIDX_V2_SETTINGS={
        **BASE_SETTINGS,  # type: ignore
        'supported-locales': ['en'],
        'tags-representation': 'together',
    },
)
@pytest.mark.translations(
    wms_items={
        'product-1_long_title': {'en': 'product-1 long title'},
        'product-1_ingredients': {'en': 'product-1 ingredients'},
        'product-1_description': {'en': 'product-1-description'},
        'product-5_long_title': {'en': 'product-5 long title'},
        'product-5_ingredients': {'en': 'product-5 ingredients'},
        'product-5_description': {'en': 'product-5-description'},
        'country_of_origin.rus': {'en': 'Russia', 'ru': 'Россия'},
        'country_of_origin.blr': {'ru': 'Беларусь'},
        'category-group-1': {'en': 'category group 1'},
        'category-1': {'en': 'category&dollar;1'},
        'category-2': {'en': 'category 2'},
        'category-1-subcategory-1_name': {
            'en': 'category 1 subcategory 1',
            'ru': 'категория 1 подкатегория 1',
        },
        'category-2-subcategory-1_name': {'en': 'category 2 subcategory 1'},
    },
)
@pytest.mark.parametrize(
    'representation',
    [pytest.param('full_path_per_node'), pytest.param('path_item_per_node')],
)
@pytest.mark.parametrize(
    'categories_source',
    [
        pytest.param('none'),
        pytest.param('layouts'),
        pytest.param('category_trees'),
        pytest.param('only_subcategories'),
    ],
)
async def test_include_categories_paths(
        patch,
        load_json,
        cron_context,
        representation,
        categories_source,
        overlord_catalog,
        grocery_products,
        mbi_api,
        grocery_depots,
):
    """
    Проверяем выгрузку категорийный путей тремя способами, а также
    способы выгрузки (по одной вершине в ноде или весь пусть сразу).
    Если пути нет, то navigation_paths пустые.
    HTML-символы вроде &dollar; должны меняться на то, что они представляют.
    """

    cron_context.config.GROCERY_MARKETIDX_CATEGORIES_PATH = {
        'categories_source': categories_source,
        'representation': representation,
        'join_delimiter': ' ',
    }

    fill_data(load_json, overlord_catalog, grocery_products, grocery_depots)

    @patch('grocery_tasks.market_idx.export_offers_v2._yt_upload')
    async def yt_upload(context, dict_entries):
        pass

    await run(cron_context)

    dict_entries = yt_upload.call['dict_entries']

    expected_products = load_json('expected_export_messages.json')

    for export_message in dict_entries:
        export_message_id = export_message['offer_id'.encode()].decode()
        offer_data = ExportMessage_pb2.ExportMessage.FromString(
            export_message['data'.encode()],
        ).offer
        locale = offer_data.original_content.language_tag
        navigation_paths = load_json(
            'expected_navigation_paths_trees_settings.json',
        )[export_message_id][representation][categories_source]

        assert (
            _make_offer_data_proto(
                expected_products[export_message_id][locale]['offer'],
                locale,
                navigation_paths,
            )
            == offer_data
        )


def _make_offer_data_proto(product, locale, navigation_paths=None):
    offer = Offer_pb2.Offer()
    offer.business_id = product['business_id']
    offer.offer_id = product['product_id']
    if 'external_id' in product:
        offer.original_sku = product['external_id']

    offer.original_content.language_tag = locale
    offer.original_content.name = product['long_title']
    offer.original_content.description = product['description']
    offer.original_pictures.append(
        OfferPictures_pb2.SourcePicture(
            url=product['image_url_template'],
            source=OfferPictures_pb2.PictureSource.YANDEX_SERVICE,
        ),
    )
    if 'shop_prices' in product:
        for shop_price in product['shop_prices']:
            offer.shop_prices.append(
                Offer_pb2.IdentifiedPrice(
                    meta=OfferMeta_pb2.UpdateMeta(
                        timestamp=_convert_datetime_iso_format_to_timestamp(
                            shop_price['meta']['timestamp'],
                        ),
                    ),
                    shop_id=shop_price['shop_id'],
                    price=Offer_pb2.OfferPrice(
                        currency=PRICE_FALLBACK_CURRENCY,
                        price=int(shop_price['price']['price'] * 1e7),
                    ),
                ),
            )
    if 'shop_statuses' in product:
        for shop_status in product['shop_statuses']:
            disable_status = {}
            disable_status[OfferMeta_pb2.DataSource.PUSH_PARTNER_API] = (
                OfferMeta_pb2.Flag(
                    meta=OfferMeta_pb2.UpdateMeta(
                        timestamp=_convert_datetime_iso_format_to_timestamp(
                            shop_status['disable_status']['meta']['timestamp'],
                        ),
                    ),
                    flag=shop_status['disable_status']['value'],
                )
            )
            offer.shop_statuses.append(
                Offer_pb2.IdentifiedStatus(
                    disable_status=disable_status,
                    shop_id=shop_status['shop_id'],
                ),
            )
    if 'barcodes' in product:
        for barcode in product['barcodes']:
            offer.original_content.barcode.append(barcode)
    if 'shop_category_path_ids' in product:
        offer.original_content.shop_category_path_ids = product[
            'shop_category_path_ids'
        ]
        offer.original_content.shop_category_path = product[
            'shop_category_path'
        ]

    if 'options' in product:
        if 'brand' in product['options']:
            offer.original_content.shop_vendor = product['options']['brand']
        if 'origin_country' in product['options']:
            offer.original_content.country_of_origin.append(
                product['options']['origin_country'],
            )
        if 'legal_restrictions' in product['options']:
            offer.original_content.adult = product['options'][
                'legal_restrictions'
            ]
        if 'ingredients' in product['options']:
            offer.original_content.ingredients.append(
                product['options']['ingredients'],
            )
        if 'measurements' in product['options']:
            if 'width' in product['options']['measurements']:
                offer.original_content.brutto_dimensions.width_mkm = (
                    product['options']['measurements']['width'] * 1000
                )
            if 'height' in product['options']['measurements']:
                offer.original_content.brutto_dimensions.height_mkm = (
                    product['options']['measurements']['height'] * 1000
                )
            if 'depth' in product['options']['measurements']:
                offer.original_content.brutto_dimensions.length_mkm = (
                    product['options']['measurements']['depth'] * 1000
                )
            if 'gross_weight' in product['options']['measurements']:
                offer.original_content.brutto_weight_in_grams = product[
                    'options'
                ]['measurements']['gross_weight']

    if navigation_paths is not None:
        product['navigation_paths'] = navigation_paths

    if 'navigation_paths' in product:
        for navigation_path in product['navigation_paths']:
            path = Offer_pb2.NavigationPath()
            for node in navigation_path['nodes']:
                navigation_node = Offer_pb2.NavigationNode()
                if 'id' in node:
                    navigation_node.id = node['id']
                if 'name' in node:
                    navigation_node.name = node['name']
                if 'url' in node:
                    navigation_node.url = node['url']
                path.nodes.append(navigation_node)
            offer.navigation_paths.append(path)

    return offer


def fill_data(load_json, overlord_catalog, grocery_products, grocery_depots):
    depots = load_json('grocery_depots_depots_data.json')
    for depot in depots:
        grocery_depots.add_depot(
            legacy_depot_id=depot['legacy_depot_id'],
            depot_id=depot['depot_id'],
            country_iso3=depot['country_iso3'],
            country_iso2=depot['country_iso2'],
            region_id=depot['region_id'],
            company_type=depot['company_type'],
            currency=depot['currency'],
            phone_number=depot['phone_number'],
            timezone=depot['timezone'],
        )

    products = load_json('overlord_products_data.json')
    for product in products:
        barcodes = None
        if 'barcodes' in product:
            barcodes = product['barcodes']
        overlord_catalog.add_product(
            product_id=product['product_id'],
            title=product['title'],
            long_title=product['long_title'],
            description=product['description'],
            image_url_template=product['image_url_template'],
            barcodes=barcodes,
            original_sku=product['original_sku'],
            private_label=product['private_label'],
            status=product['status'],
            options=product['options'],
        )

    category_trees = load_json('overlord_category_tree.json')
    for tree in category_trees:
        overlord_catalog.add_category_tree(
            depot_id=tree['depot_ids'], category_tree=tree,
        )

    categories_data = load_json('overlord_categories_data.json')
    overlord_catalog.add_categories_data(new_categories_data=categories_data)

    stocks = load_json('overlord_stocks_data.json')
    for stock in stocks:
        overlord_catalog.add_products_stocks(
            depot_id=stock['depot_id'], new_products_stocks=stock['stocks'],
        )

    layouts = load_json('g_products_layouts_data.json')
    for layout_data in layouts:
        layout = grocery_products.add_layout(
            test_id=layout_data['test_id'], meta=layout_data['meta'],
        )
        for group_data in layout_data['groups']:
            group = layout.add_category_group(
                test_id=group_data['test_id'],
                image=group_data['image_url_template'],
                layout_meta=group_data['layout_meta'],
                short_title_tanker_key=group_data['short_title_tanker_key'],
                title_tanker_key=group_data['title_tanker_key'],
            )
            for category_data in group_data['categories']:
                category = group.add_virtual_category(
                    virtual_category_id=category_data['virtual_category_id'],
                    layout_meta=category_data['layout_meta'],
                    title_tanker_key=category_data['title_tanker_key'],
                    alias=category_data['alias'],
                    item_meta=category_data['item_meta'],
                )
                for image in category_data['images']:
                    category.add_image(
                        image=image['image_url_template'],
                        dimensions=image['dimensions'],
                    )
                for subcategory in category_data['subcategories']:
                    category.add_subcategory(
                        subcategory_id=subcategory['category_id'],
                    )
