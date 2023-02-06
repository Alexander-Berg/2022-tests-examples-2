import datetime as dt
import decimal
import math
import re
import xml.etree.ElementTree as ET

import pytest
import pytz

from . import models


PERIODIC_NAME = 'run-sitemaps-generation-periodic'
EDA_YANDEX_RU = 'eda.yandex.ru'
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)
BRAND_1_ID = '771'
BRAND_2_ID = '772'
BRAND_3_ID = '773'
BRAND_4_ID = '774'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
PLACE_3_ID = '1003'


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize('max_links_count_per_file', [3, 1, 100])
async def test_run_sitemaps_generation(
        load,
        mds_s3_storage,
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        # parametrize params
        max_links_count_per_file,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config, max_links_count_per_file)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [
        products,
        categories,
        generalized_places_products,
    ] = _generate_products_and_categories(brands)
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(generalized_places_products)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    # brands sitemaps

    sitemap_files_urls = []

    # brands that are in config and have products
    expected_brands_with_sitemap = [brands[BRAND_1_ID], brands[BRAND_2_ID]]
    for brand in expected_brands_with_sitemap:
        expected_raw_xml = load(f'{brand.slug}_sitemap.xml')
        [expected_xml, expected_urls_count] = _normalize_sitemap_xml(
            expected_raw_xml,
        )
        files_count = math.ceil(expected_urls_count / max_links_count_per_file)

        [raw_result_xml, brand_sitemap_files_urls] = _generate_brand_sitemap(
            mds_s3_storage,
            brand,
            files_count,
            max_links_count_per_file,
            expected_urls_count,
        )
        [result_xml, result_links_count] = _normalize_sitemap_xml(
            raw_result_xml,
        )

        assert result_links_count == expected_urls_count
        assert result_xml == expected_xml

        sitemap_files_urls += brand_sitemap_files_urls

    # common sitemap

    result_common_sitemap_xml = mds_s3_storage.storage[
        'sitemap/retail-common-sitemap.xml'
    ].data.decode('utf-8')
    expected_common_sitemap_xml = _generate_common_sitemap(sitemap_files_urls)
    assert _normalize_sitemap_xml(
        result_common_sitemap_xml,
    ) == _normalize_sitemap_xml(expected_common_sitemap_xml)

    assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
async def test_periodic_metrics(
        save_brands_to_db, update_taxi_config, verify_periodic_metrics,
):
    _set_configs(update_taxi_config, 100)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _set_configs(update_taxi_config, max_links_count_per_file):
    update_taxi_config(
        'EATS_RETAIL_SEO_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 86400}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_MASTER_TREE',
        {
            'master_tree_settings': {
                BRAND_1_ID: {'assortment_name': 'default_assortment'},
                BRAND_2_ID: {'assortment_name': 'default_assortment'},
                BRAND_3_ID: {'assortment_name': 'master_tree'},
            },
        },
    )
    update_taxi_config(
        'EATS_RETAIL_SEO_SITEMAPS_SETTINGS',
        {'max_links_count_per_file': max_links_count_per_file},
    )


def _generate_brands():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_1.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand_1.brand_id,
        ),
        PLACE_2_ID: models.Place(
            place_id=PLACE_2_ID, slug='place1002', brand_id=brand_1.brand_id,
        ),
    }

    brand_2 = models.Brand(
        brand_id=BRAND_2_ID,
        slug='auchan_gipermarket',
        name='Ашан Гипермаркет',
    )
    brand_2.places = {
        PLACE_3_ID: models.Place(
            place_id=PLACE_3_ID, slug='place1003', brand_id=brand_2.brand_id,
        ),
    }

    brand_3_no_products = models.Brand(
        brand_id=BRAND_3_ID, slug='vkusvill', name='ВкусВилл',
    )

    brand_4_not_in_config = models.Brand(
        brand_id=BRAND_4_ID, slug='azbuka_vkusa', name='Азбука Вкуса',
    )

    return {
        brand.brand_id: brand
        for brand in [
            brand_1,
            brand_2,
            brand_3_no_products,
            brand_4_not_in_config,
        ]
    }


def _generate_products_and_categories(brands):
    product_1 = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
    )
    product_2 = models.Product(
        nomenclature_id='45631b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name=f"""Конфеты&nbsp;M&m''s""",
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-2',
    )
    product_3 = models.Product(
        nomenclature_id='78931b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Колбаса',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-3',
    )
    product_4 = models.Product(
        nomenclature_id='89131b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Сервелат',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-4',
    )
    product_5_second_brand = models.Product(
        nomenclature_id='def31b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар другого бренда',
        brand=brands[BRAND_2_ID],
        origin_id='item-origin-id-5',
    )
    product_6_not_in_categories = models.Product(
        nomenclature_id='ghi31b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Товар вне категорий',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-6',
    )
    products = [
        product_1,
        product_2,
        product_3,
        product_4,
        product_5_second_brand,
        product_6_not_in_categories,
    ]

    category_1 = models.Category(category_id='1234', name='Молоко')
    category_1.set_products([product_1])
    category_2 = models.Category(category_id='123', name='Молоко & сыр')
    category_2.set_child_categories([category_1])
    category_3 = models.Category(
        category_id='789', name='Колбасные&nbsp;изделия',
    )
    category_3.set_products([product_3, product_4])
    category_4 = models.Category(category_id='12', name='Молочные продукты')
    category_4.set_child_categories([category_2, category_3])

    category_5 = models.Category(
        category_id='456', name='Конфеты&nbsp;<b>шоколадные</b>',
    )
    category_5.set_products([product_2, product_5_second_brand])
    category_6 = models.Category(category_id='45', name='Конфеты')
    category_6.set_child_categories([category_5])

    category_7_without_products = models.Category(
        category_id='1012', name='Категория без товаров',
    )
    category_8_without_products = models.Category(
        category_id='101', name='Родительская категория без товаров',
    )
    category_8_without_products.set_child_categories(
        [category_7_without_products],
    )

    categories = [category_4, category_6, category_8_without_products]

    generalized_places_product_1 = models.GeneralizedPlacesProduct(
        product=product_1, category=category_1, price=decimal.Decimal('100'),
    )
    generalized_places_product_2 = models.GeneralizedPlacesProduct(
        product=product_2, category=category_5, price=decimal.Decimal('100'),
    )
    generalized_places_product_3 = models.GeneralizedPlacesProduct(
        product=product_3, category=category_3, price=decimal.Decimal('100'),
    )
    generalized_places_product_4 = models.GeneralizedPlacesProduct(
        product=product_4, category=category_3, price=decimal.Decimal('100'),
    )
    generalized_places_product_5 = models.GeneralizedPlacesProduct(
        product=product_5_second_brand,
        category=category_5,
        price=decimal.Decimal('100'),
    )
    generalized_places_products = [
        generalized_places_product_1,
        generalized_places_product_2,
        generalized_places_product_3,
        generalized_places_product_4,
        generalized_places_product_5,
    ]

    return [products, categories, generalized_places_products]


def _generate_brand_sitemap_s3_path(brand: models.Brand, file_index: int):
    file_index_str = str(file_index if file_index > 1 else '')
    return f"""sitemap/retail-{brand.slug}-sitemap{file_index_str}.xml"""


def _generate_brand_sitemap_file_url(brand: models.Brand, file_index: int):
    file_index_str = str(file_index if file_index > 1 else '')
    return (
        f'https://{EDA_YANDEX_RU}/'
        f'retail-{brand.slug}-sitemap{file_index_str}.xml'
    )


def _sort_by_loc(x):
    for child in x:
        # ET changes tags
        # so they have prefixes
        if 'loc' in child.tag:
            return child.text
    return x.text


def _normalize_sitemap_xml(xml):
    no_indent_xml = re.sub(r'>\s+<', '>\n<', xml)
    urls = ET.fromstring(no_indent_xml)
    urls[:] = sorted(urls, key=_sort_by_loc)
    return [ET.tostring(urls, encoding='unicode', method='xml'), len(urls)]


def _get_urls_xml_from(xml):
    xml = re.sub(r'>\s+<', '>\n<', xml)
    urls = ET.fromstring(xml)
    xml = ''
    for url in urls:
        xml += ET.tostring(url, encoding='unicode', method='xml')
    return [xml, len(urls)]


def _generate_brand_sitemap(
        mds_s3_storage,
        brand,
        files_count,
        max_links_count_per_file,
        expected_urls_count,
):
    sitemap_files_urls = []
    result_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    )
    for i in range(files_count):
        chunk_xml = mds_s3_storage.storage[
            _generate_brand_sitemap_s3_path(brand, i + 1)
        ].data.decode('utf-8')
        [chunk_xml, chunk_links_count] = _get_urls_xml_from(chunk_xml)
        if i < files_count - 1:
            assert chunk_links_count == max_links_count_per_file
        else:
            if expected_urls_count % max_links_count_per_file != 0:
                left_count = (
                    expected_urls_count
                    - (expected_urls_count // max_links_count_per_file)
                    * max_links_count_per_file
                )
            else:
                left_count = max_links_count_per_file
            assert chunk_links_count == left_count
        result_xml += chunk_xml
        sitemap_files_urls.append(
            _generate_brand_sitemap_file_url(brand, i + 1),
        )
    result_xml += '</urlset>'
    return [result_xml, sitemap_files_urls]


def _generate_common_sitemap(files_urls):
    result_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    )
    for file_url in files_urls:
        result_xml += '<sitemap>\n' f'<loc>{file_url}</loc>\n' '</sitemap>\n'
    result_xml += '</sitemapindex>'
    return result_xml
