# pylint: disable=import-error
import pytest


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_assortments.sql'],
)
async def test_categories_snapshots_export(stq_runner, testpoint):
    place_id = 1

    logged_categories = []
    logged_categories_relations = []
    logged_categories_products = []

    @testpoint('yt-logger-categories-snapshot')
    def _yt_logger_categories(data):
        assert data['place_id'] == place_id
        del data['place_id']
        del data['timestamp']
        logged_categories.append(data)

    @testpoint('yt-logger-categories-relations-snapshot')
    def _yt_logger_categories_relations(data):
        assert data['place_id'] == place_id
        del data['place_id']
        del data['timestamp']
        logged_categories_relations.append(data)

    @testpoint('yt-logger-categories-products-snapshot')
    def _yt_logger_categories_products(data):
        assert data['place_id'] == place_id
        del data['place_id']
        del data['timestamp']
        logged_categories_products.append(data)

    await stq_runner.eats_nomenclature_export_categories_snapshots.call(
        task_id=str(place_id), args=[], kwargs={'place_id': place_id},
    )

    assert (
        get_sorted_categories(logged_categories) == get_expected_categories()
    )
    assert (
        get_sorted_categories_relations(logged_categories_relations)
        == get_expected_cat_relations()
    )
    assert (
        get_sorted_categories_products(logged_categories_products)
        == get_expected_cat_products()
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_assortments.sql'],
)
async def test_stq_error_limit(taxi_config, stq_runner, testpoint):
    @testpoint('export-categories-snapshots-injected-error')
    def task_testpoint(param):
        return {'inject_failure': True}

    place_id = 1
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    for i in range(max_retries_on_error):
        await stq_runner.eats_nomenclature_export_categories_snapshots.call(
            task_id=str(place_id),
            args=[],
            kwargs={'place_id': place_id},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_nomenclature_export_categories_snapshots.call(
        task_id=str(place_id),
        args=[],
        kwargs={'place_id': place_id},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


def get_expected_categories():
    return [
        {
            'assortment_name': 'assortment_name_1',
            'id': '1',
            'name': 'base_custom_category_1',
            'category_type': 'custom_base',
            'image_urls': ['processed_url_1'],
            'product_types': [],
            'tags': ['Тег 1'],
        },
        {
            'assortment_name': 'assortment_name_1',
            'id': '2',
            'name': 'base_custom_category_2',
            'category_type': 'custom_base',
            'image_urls': ['processed_url_2'],
            'product_types': ['молоко', 'мороженое'],
            'tags': ['Тег 2', 'Тег 3'],
        },
        {
            'assortment_name': 'assortment_name_1',
            'id': '3',
            'name': 'base_custom_category_3',
            'category_type': 'custom_base',
            'image_urls': ['processed_url_3'],
            'product_types': ['эскимо', 'говядина'],
            'tags': ['Тег 1', 'Тег 3'],
        },
        {
            'assortment_name': 'assortment_name_1',
            'id': '4',
            'name': 'promo_custom_category_4',
            'category_type': 'custom_promo',
            'image_urls': ['processed_url_4', 'processed_url_5'],
            'product_types': [],
            'tags': [],
        },
        {
            'assortment_name': 'partner',
            'id': '5',
            'name': 'base_partner_category_5',
            'category_type': 'partner',
            'image_urls': ['processed_url_1', 'processed_url_2'],
            'product_types': [],
            'tags': [],
        },
        {
            'assortment_name': 'partner',
            'id': '6',
            'name': 'base_partner_category_6',
            'category_type': 'partner',
            'image_urls': [],
            'product_types': [],
            'tags': [],
        },
    ]


def get_expected_cat_relations():
    return [
        {'assortment_name': 'assortment_name_1', 'category_id': '1'},
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '2',
            'parent_category_id': '1',
        },
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '3',
            'parent_category_id': '1',
        },
        {'assortment_name': 'assortment_name_1', 'category_id': '4'},
        {'assortment_name': 'partner', 'category_id': '5'},
        {
            'assortment_name': 'partner',
            'category_id': '6',
            'parent_category_id': '5',
        },
    ]


def get_expected_cat_products():
    return [
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '2',
            'product_id': '11111111-1111-1111-1111-111111111111',
        },
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '2',
            'product_id': '22222222-2222-2222-2222-222222222222',
        },
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '3',
            'product_id': '33333333-3333-3333-3333-333333333333',
        },
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '4',
            'product_id': '44444444-4444-4444-4444-444444444444',
        },
        {
            'assortment_name': 'assortment_name_1',
            'category_id': '4',
            'product_id': '55555555-5555-5555-5555-555555555555',
        },
        {
            'assortment_name': 'partner',
            'category_id': '6',
            'product_id': '11111111-1111-1111-1111-111111111111',
        },
        {
            'assortment_name': 'partner',
            'category_id': '6',
            'product_id': '22222222-2222-2222-2222-222222222222',
        },
        {
            'assortment_name': 'partner',
            'category_id': '6',
            'product_id': '33333333-3333-3333-3333-333333333333',
        },
    ]


def get_sorted_categories(categories):
    return sorted(
        categories, key=lambda item: (item['assortment_name'], item['id']),
    )


def get_sorted_categories_relations(categories_relations):
    return sorted(
        categories_relations,
        key=lambda item: (item['assortment_name'], item['category_id']),
    )


def get_sorted_categories_products(categories_products):
    return sorted(
        categories_products,
        key=lambda item: (
            item['assortment_name'],
            item['category_id'],
            item['product_id'],
        ),
    )
