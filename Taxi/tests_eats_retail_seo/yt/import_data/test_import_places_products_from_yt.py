import datetime as dt
import decimal

import pytest
import pytz

from ... import models


PERIODIC_NAME = 'import-places-products-from-yt-periodic'
BRAND_1_ID = '771'
BRAND_2_ID = '772'
BRAND_3_ID = '773'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
PLACE_3_ID = '1003'
SNAPSHOT_PLACES_PRODUCTS_TABLE_ID = 'places_products'
SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH = '//nmn_yt/places_products'
OLD_LAST_REFERENCED_AT = dt.datetime(2021, 2, 18, 1, 0, 0, tzinfo=pytz.UTC)
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_places_products_schema.yaml'],
    static_table_data=['yt_places_products_data.yaml'],
)
async def test_import_places_products_from_yt(
        add_snapshot_table,
        save_brands_to_db,
        save_products_to_db,
        get_products_from_db,
        assert_objects_lists,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        # don't delete it
        yt_apply,
):
    @testpoint('places-products-importer-finished')
    def places_products_import_finished(param):
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    add_snapshot_table(
        SNAPSHOT_PLACES_PRODUCTS_TABLE_ID, SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH,
    )

    initial_data = _generate_data()
    save_brands_to_db(list(initial_data['brands'].values()))
    save_products_to_db(initial_data['products'])

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    products_after_update = get_products_from_db()
    expected_products_after_update = _get_expected_data(
        initial_data['products'], initial_data['brands'],
    )
    assert_objects_lists(products_after_update, expected_products_after_update)

    assert places_products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_places_products_schema.yaml'],
    static_table_data=['yt_places_products_data.yaml'],
)
async def test_import_with_retries(
        add_snapshot_table,
        save_brands_to_db,
        save_products_to_db,
        get_products_from_db,
        assert_objects_lists,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
):
    @testpoint('places-products-importer-finished')
    def places_products_import_finished(param):
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    add_snapshot_table(
        SNAPSHOT_PLACES_PRODUCTS_TABLE_ID, SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH,
    )

    initial_data = _generate_data()
    save_brands_to_db(list(initial_data['brands'].values()))
    save_products_to_db(initial_data['products'])

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

    products_after_update = get_products_from_db()
    expected_products_after_update = _get_expected_data(
        initial_data['products'],
        initial_data['brands'],
        items_update_failed=2,
    )
    assert_objects_lists(products_after_update, expected_products_after_update)

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert places_products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_places_products_schema.yaml'],
    static_table_data=['yt_places_products_data.yaml'],
)
async def test_exceed_max_skipped_batches(
        add_snapshot_table,
        save_brands_to_db,
        save_products_to_db,
        get_products_from_db,
        assert_objects_lists,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
):
    @testpoint('places-products-importer-finished')
    def places_products_import_finished(param):
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    add_snapshot_table(
        SNAPSHOT_PLACES_PRODUCTS_TABLE_ID, SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH,
    )

    initial_data = _generate_data()
    save_brands_to_db(list(initial_data['brands'].values()))
    save_products_to_db(initial_data['products'])

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

    products_after_update = get_products_from_db()
    expected_products_after_update = initial_data['products']
    assert_objects_lists(products_after_update, expected_products_after_update)

    assert batch_read_table_failed.has_calls
    assert batch_read_table_retries.times_called == max_retries_count

    assert not places_products_import_finished.has_calls
    assert not periodic_finished.has_calls


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'places_products_path',
    [
        pytest.param(SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH),
        pytest.param('//nmn_yt/some_path'),
        pytest.param(''),
    ],
)
@pytest.mark.yt(
    schemas=['yt_places_products_schema.yaml'],
    static_table_data=['yt_places_products_data.yaml'],
)
async def test_no_snapshot_tables(
        add_snapshot_table,
        save_brands_to_db,
        save_products_to_db,
        get_products_from_db,
        assert_objects_lists,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        yt_apply,
        # parametrize params
        places_products_path,
):
    @testpoint('places-products-importer-finished')
    def places_products_import_finished(param):
        pass

    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)
    if places_products_path != '':
        add_snapshot_table(
            SNAPSHOT_PLACES_PRODUCTS_TABLE_ID, places_products_path,
        )

    initial_data = _generate_data()
    save_brands_to_db(list(initial_data['brands'].values()))
    save_products_to_db(initial_data['products'])

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    if places_products_path != SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH:
        products_after_update = get_products_from_db()
        expected_products_after_update = initial_data['products']

        assert_objects_lists(
            products_after_update, expected_products_after_update,
        )
        assert not places_products_import_finished.has_calls
        assert not periodic_finished.has_calls
    else:
        assert places_products_import_finished.times_called == 1
        assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_places_products_schema.yaml'],
    static_table_data=['yt_places_products_data.yaml'],
)
async def test_periodic_metrics(
        add_snapshot_table,
        update_taxi_config,
        verify_periodic_metrics,
        yt_apply,
):
    _set_configs(update_taxi_config)
    add_snapshot_table(
        SNAPSHOT_PLACES_PRODUCTS_TABLE_ID, SNAPSHOT_PLACES_PRODUCTS_TABLE_PATH,
    )
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


def _get_expected_data(initial_data, brands, items_update_failed=0):
    product_1_changed = models.Product(
        nomenclature_id='801',  # update price
        name='name-1',
        brand=brands[BRAND_1_ID],
        origin_id='origin1',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_1_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                is_available=True,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_2_changed = models.Product(
        nomenclature_id='802',  # update old_price and vat
        name='name-2',
        brand=brands[BRAND_1_ID],
        origin_id='origin2',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_2_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_3_changed = models.Product(
        nomenclature_id='803',  # update stocks
        name='name-3',
        brand=brands[BRAND_1_ID],
        origin_id='origin3',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_3_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=True,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=10,
                vat=10,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_4_changed = models.Product(
        nomenclature_id='804',  # update is_available and delete vat
        name='name-4',
        brand=brands[BRAND_1_ID],
        origin_id='origin4',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_4_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=True,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )

    product_5_not_in_config = models.Product(
        nomenclature_id='805',  # not in master-tree config
        name='name-5',
        brand=brands[BRAND_2_ID],
        origin_id='origin5',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_5_not_in_config.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_2_ID].places[PLACE_3_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )

    product_6_new = models.Product(
        nomenclature_id='806',  # add new
        name='name-6',
        brand=brands[BRAND_1_ID],
        origin_id='origin6',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_6_new.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                is_available=True,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_7_new = models.Product(
        nomenclature_id='807',  # add new
        name='name-7',
        brand=brands[BRAND_1_ID],
        origin_id='origin7',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_7_new.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                stocks=15,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_8_new = models.Product(
        nomenclature_id='808',  # add new
        name='name-8',
        brand=brands[BRAND_1_ID],
        origin_id='origin8',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_8_new.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=True,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                vat=10,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )

    product_9_not_changed = models.Product(
        nomenclature_id='809',  # don't update existing
        name='name-9',
        brand=brands[BRAND_1_ID],
        origin_id='origin9',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_9_not_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    fully_updated_data = [
        product_1_changed,
        product_2_changed,
        product_3_changed,
        product_4_changed,
        product_5_not_in_config,
        product_6_new,
        product_7_new,
        product_8_new,
        product_9_not_changed,
    ]

    if items_update_failed == 0:
        return fully_updated_data

    if items_update_failed > len(initial_data):
        return initial_data + fully_updated_data[items_update_failed:]

    return (
        initial_data[:items_update_failed]
        + fully_updated_data[items_update_failed:]
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
    return {brand.brand_id: brand for brand in [brand_1, brand_2]}


def _generate_data():
    brands = _generate_brands()

    product_1_will_be_changed = models.Product(
        nomenclature_id='801',
        name='name-1',
        brand=brands[BRAND_1_ID],
        origin_id='origin1',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_1_will_be_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                is_available=True,
                price=decimal.Decimal('100'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    product_2_will_be_changed = models.Product(
        nomenclature_id='802',
        name='name-2',
        brand=brands[BRAND_1_ID],
        origin_id='origin2',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_2_will_be_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_1_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('157'),
                stocks=15,
                vat=20,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    product_3_will_be_changed = models.Product(
        nomenclature_id='803',
        name='name-3',
        brand=brands[BRAND_1_ID],
        origin_id='origin3',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_3_will_be_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    product_4_will_be_changed = models.Product(
        nomenclature_id='804',
        name='name-4',
        brand=brands[BRAND_1_ID],
        origin_id='origin4',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_4_will_be_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    product_5_not_in_config = models.Product(
        nomenclature_id='805',
        name='name-5',
        brand=brands[BRAND_2_ID],
        origin_id='origin5',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_5_not_in_config.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_2_ID].places[PLACE_3_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    product_6_will_have_new = models.Product(
        nomenclature_id='806',
        name='name-6',
        brand=brands[BRAND_1_ID],
        origin_id='origin6',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_7_will_have_new = models.Product(
        nomenclature_id='807',
        name='name-7',
        brand=brands[BRAND_1_ID],
        origin_id='origin7',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_8_will_have_new = models.Product(
        nomenclature_id='808',
        name='name-8',
        brand=brands[BRAND_1_ID],
        origin_id='origin8',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_9_not_changed = models.Product(
        nomenclature_id='809',
        name='name-9',
        brand=brands[BRAND_1_ID],
        origin_id='origin9',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_9_not_changed.set_product_in_places(
        [
            models.ProductInPlace(
                place=brands[BRAND_1_ID].places[PLACE_2_ID],
                is_available=False,
                price=decimal.Decimal('153.3'),
                old_price=decimal.Decimal('154'),
                stocks=15,
                vat=10,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    products = [
        product_1_will_be_changed,
        product_2_will_be_changed,
        product_3_will_be_changed,
        product_4_will_be_changed,
        product_5_not_in_config,
        product_6_will_have_new,
        product_7_will_have_new,
        product_8_will_have_new,
        product_9_not_changed,
    ]

    return {'brands': brands, 'products': products}


@pytest.fixture(name='add_snapshot_table')
def _add_snapshot_table(save_snapshot_tables_to_db):
    def do_add_snapshot_table(table_id, table_path):
        snapshot_table = models.SnapshotTable(table_id, table_path)
        save_snapshot_tables_to_db([snapshot_table])

    return do_add_snapshot_table
