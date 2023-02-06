import datetime as dt

import pytest
import pytz

from ... import models


PERIODIC_NAME = 'import-categories-products-from-yt-periodic'
BRAND_1_ID = '771'
BRAND_2_ID = '772'
BRAND_3_ID = '773'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
PLACE_3_ID = '1003'
PLACE_4_ID = '1004'
SNAPSHOT_CATEGORIES_PRODUCTS_TABLE_ID = 'categories_products'
SNAPSHOT_CATEGORIES_PRODUCTS_TABLE_PATH = '//nmn_yt/categories_products'
OLD_LAST_REFERENCED_AT = dt.datetime(2021, 2, 18, 1, 0, 0, tzinfo=pytz.UTC)
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_categories_products_schema.yaml'],
    static_table_data=['yt_categories_products_data.yaml'],
)
async def test_import_categories_products_from_yt(
        add_snapshot_table,
        assert_objects_lists,
        get_categories_from_db,
        save_brands_to_db,
        save_categories_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
):
    @testpoint('categories-products-importer-finished')
    def categories_products_import_finished(param):  # pylint: disable=C0103
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    add_snapshot_table()

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [products, categories] = _generate_products_and_categories(brands)
    [product_1, product_2, product_3, product_4_another_brand, _] = products
    [category_1, category_2, category_3] = categories
    save_products_to_db(products)
    save_categories_to_db(categories)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    # устаревшие связки удаляются отдельным периодиком
    category_1.set_category_products(
        [
            models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(product_2, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(
                product_4_another_brand, OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    category_2.set_category_products(
        [
            models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(product_2, OLD_LAST_REFERENCED_AT),
            models.CategoryProduct(product_3, OLD_LAST_REFERENCED_AT),
        ],
    )
    category_3.set_category_products(
        [
            models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(product_3, last_referenced_at=MOCK_NOW),
        ],
    )

    assert_objects_lists(
        get_categories_from_db(), [category_1, category_2, category_3],
    )

    assert categories_products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_categories_products_schema.yaml'],
    static_table_data=['yt_categories_products_data.yaml'],
)
async def test_import_with_retries(
        add_snapshot_table,
        assert_objects_lists,
        get_categories_from_db,
        save_brands_to_db,
        save_categories_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
):
    @testpoint('categories-products-importer-finished')
    def categories_products_import_finished(param):  # pylint: disable=C0103
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    add_snapshot_table()

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [products, categories] = _generate_products_and_categories(brands)
    [product_1, product_2, product_3, _, _] = products
    [category_1, category_2, category_3] = categories
    save_products_to_db(products)
    save_categories_to_db(categories)

    # первый батч будет пропущен из-за ошибки,
    # будет обработан только второй
    max_retries_count = 2
    update_taxi_config(
        'EATS_RETAIL_SEO_YT_SETTINGS',
        {
            PERIODIC_NAME: {
                'lookup_batch_size': 2,
                'batch_max_retries_count': max_retries_count,
                'batch_delay_between_retries': 100,
                'max_skipped_batches_count': 10,
                'max_total_batches_count': 20,
            },
        },
    )

    @testpoint('BatchReadTable::fail')
    def batch_read_table_failed(param):
        return {'inject_failure': True, 'failure_at_row': 0}

    @testpoint('ProcessWithRetries::retry')
    def batch_read_table_retries(param):
        pass

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    # первая категория останется с теми же товарами
    category_2.set_category_products(
        [
            models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(product_2, OLD_LAST_REFERENCED_AT),
            models.CategoryProduct(product_3, OLD_LAST_REFERENCED_AT),
        ],
    )
    category_3.set_category_products(
        [
            models.CategoryProduct(product_1, last_referenced_at=MOCK_NOW),
            models.CategoryProduct(product_3, last_referenced_at=MOCK_NOW),
        ],
    )

    assert_objects_lists(
        get_categories_from_db(), [category_1, category_2, category_3],
    )

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert categories_products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_categories_products_schema.yaml'],
    static_table_data=['yt_categories_products_data.yaml'],
)
async def test_exceed_max_skipped_batches(
        add_snapshot_table,
        assert_objects_lists,
        get_categories_from_db,
        save_brands_to_db,
        save_categories_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
):
    @testpoint('categories-products-importer-finished')
    def categories_products_import_finished(param):  # pylint: disable=C0103
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    add_snapshot_table()

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [old_products, old_categories] = _generate_products_and_categories(brands)
    save_products_to_db(old_products)
    save_categories_to_db(old_categories)

    max_retries_count = 2
    max_skipped_batches_count = 0
    update_taxi_config(
        'EATS_RETAIL_SEO_YT_SETTINGS',
        {
            PERIODIC_NAME: {
                'lookup_batch_size': 2,
                'batch_max_retries_count': max_retries_count,
                'batch_delay_between_retries': 100,
                'max_skipped_batches_count': max_skipped_batches_count,
                'max_total_batches_count': 20,
            },
        },
    )

    @testpoint('BatchReadTable::fail')
    def batch_read_table_failed(param):
        return {'inject_failure': True, 'failure_at_row': 0}

    @testpoint('ProcessWithRetries::retry')
    def batch_read_table_retries(param):
        pass

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert_objects_lists(get_categories_from_db(), old_categories)

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert not categories_products_import_finished.has_calls
    assert not periodic_finished.has_calls


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'has_products_path',
    [
        pytest.param(True, id='has_products_path'),
        pytest.param(False, id='no_products_path'),
    ],
)
@pytest.mark.parametrize(
    'products_path',
    [
        pytest.param(
            SNAPSHOT_CATEGORIES_PRODUCTS_TABLE_PATH, id='products_path_exist',
        ),
        pytest.param('//nmn_yt/some_path', id='products_path_doesnt_exist'),
    ],
)
@pytest.mark.yt(
    schemas=['yt_categories_products_schema.yaml'],
    static_table_data=['yt_categories_products_data.yaml'],
)
async def test_no_snapshot_tables(
        add_snapshot_table,
        assert_objects_lists,
        get_categories_from_db,
        save_brands_to_db,
        save_categories_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
        # parametrize params
        has_products_path,
        products_path,
):
    @testpoint('categories-products-importer-finished')
    def categories_products_import_finished(param):  # pylint: disable=C0103
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)

    if has_products_path:
        add_snapshot_table(table_path=products_path)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [old_products, old_categories] = _generate_products_and_categories(brands)
    save_products_to_db(old_products)
    save_categories_to_db(old_categories)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    products_ok = has_products_path and (
        products_path == SNAPSHOT_CATEGORIES_PRODUCTS_TABLE_PATH
    )

    if not products_ok:
        assert_objects_lists(get_categories_from_db(), old_categories)
        assert not categories_products_import_finished.has_calls
        assert not periodic_finished.has_calls
    else:
        assert categories_products_import_finished.times_called == 1
        assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_categories_products_schema.yaml'],
    static_table_data=['yt_categories_products_data.yaml'],
)
async def test_periodic_metrics(
        add_snapshot_table,
        save_brands_to_db,
        update_taxi_config,
        verify_periodic_metrics,
        yt_apply,
):
    _set_configs(update_taxi_config)
    add_snapshot_table()

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _set_configs(update_taxi_config):
    update_taxi_config(
        'EATS_RETAIL_SEO_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 86400}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_MASTER_TREE',
        {
            'master_tree_settings': {
                BRAND_1_ID: {'assortment_name': 'default_assortment'},
                BRAND_3_ID: {'assortment_name': 'master_tree'},
            },
        },
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
        brand_id=BRAND_2_ID, slug='ashan_gipermarket', name='Ашан Гипермаркет',
    )
    brand_2.places = {
        PLACE_3_ID: models.Place(
            place_id=PLACE_3_ID, slug='place1003', brand_id=brand_2.brand_id,
        ),
    }

    brand_3 = models.Brand(
        brand_id=BRAND_3_ID, slug='vkusvill', name='ВкусВилл',
    )
    brand_3.places = {
        PLACE_4_ID: models.Place(
            place_id=PLACE_4_ID, slug='place1004', brand_id=brand_3.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1, brand_2, brand_3]}


def _generate_products_and_categories(brands):
    product_1 = models.Product(
        nomenclature_id='bca9c5c2-81d3-42c6-975b-04d782127001',
        name='Молоко Простоквашино',
        brand=brands[BRAND_1_ID],
        origin_id='425643',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_2 = models.Product(
        nomenclature_id='bca9c5c2-81d3-42c6-975b-04d782127002',
        name='Яйца Домик в деревне',
        brand=brands[BRAND_1_ID],
        origin_id='235908',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_3 = models.Product(
        nomenclature_id='bca9c5c2-81d3-42c6-975b-04d782127003',
        name='Сыр Ламбер',
        brand=brands[BRAND_1_ID],
        origin_id='00035235525',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_4_another_brand = models.Product(
        nomenclature_id='bca9c5c2-81d3-42c6-975b-04d782127004',
        name='Молоко Домик в деревне',
        brand=brands[BRAND_2_ID],
        origin_id='76547',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_5_another_brand = models.Product(
        nomenclature_id='bca9c5c2-81d3-42c6-975b-04d782127005',
        name='Сыр плавленый',
        brand=brands[BRAND_2_ID],
        origin_id='875470',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    products = [
        product_1,
        product_2,
        product_3,
        product_4_another_brand,
        product_5_another_brand,
    ]

    category_1 = models.Category(
        category_id='801',
        name='Молоко и яйца',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_1.set_products(
        [product_1, product_4_another_brand], OLD_LAST_REFERENCED_AT,
    )
    category_2 = models.Category(
        category_id='802',
        name='Молочные продукты',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_2.set_products([product_2, product_3], OLD_LAST_REFERENCED_AT)
    category_3_no_products = models.Category(
        category_id='803',
        name='Сыры',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    categories = [category_1, category_2, category_3_no_products]

    return [products, categories]


@pytest.fixture(name='add_snapshot_table')
def _add_snapshot_table(save_snapshot_tables_to_db):
    def do_add_snapshot_table(
            table_id=SNAPSHOT_CATEGORIES_PRODUCTS_TABLE_ID,
            table_path=SNAPSHOT_CATEGORIES_PRODUCTS_TABLE_PATH,
    ):
        snapshot_table = models.SnapshotTable(table_id, table_path)
        save_snapshot_tables_to_db([snapshot_table])

    return do_add_snapshot_table
