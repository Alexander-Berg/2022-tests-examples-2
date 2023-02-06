import pytest


METRICS_NAME = 'handle-rps-data'

PLACE_ID = 1
CATEGORY_ID = '11'
PLACE_SLUG = 'slug'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_nomenclature(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/nomenclature'
    handle_id = f'{handle}_GET'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    await taxi_eats_nomenclature.tests_control(reset_metrics=True)
    # exception fail
    await taxi_eats_nomenclature.get(
        f'{handle}?slug={PLACE_SLUG}&category_id=category_1_origin',
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    @testpoint(f'eats-nomenclature_{handle_id}::wait')
    def nomenclature_get_wait(param):
        return {'sleep_time_in_seconds': 1}

    # 404 fail
    await taxi_eats_nomenclature.get(f'{handle}?slug=random_slug')
    # 200 ok
    await taxi_eats_nomenclature.get(
        f'{handle}?slug={PLACE_SLUG}&category_id=category_1_origin',
    )
    assert nomenclature_get_wait.has_calls

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 3,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '404': 1,
                },
                'execution-time_max': 900,
            },
        },
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS={
        'v2/place/assortment/details': {'max_items_count': 1},
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_place_assortment_details(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v2/place/assortment/details'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?slug=random_slug', json={'categories': [], 'products': []},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?slug=random_slug', json={'categories': [], 'products': []},
    )
    # 400 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?slug={PLACE_SLUG}',
        json={
            'categories': ['1', '2'],
            'products': [
                '11111111-1111-1111-1111-111111111111',
                '22222222-2222-2222-2222-222222222222',
            ],
        },
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?slug={PLACE_SLUG}',
        json={
            'categories': ['1'],
            'products': ['11111111-1111-1111-1111-111111111111'],
        },
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 4,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '400': 1,
                    '404': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_place_products_info(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/place/products/info'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'product_ids': []},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id=99999', json={'product_ids': []},
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}',
        json={'product_ids': ['11111111-1111-1111-1111-111111111111']},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 3,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '404': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_place_products_sku_id(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/place/products/id-by-sku-id'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'sku_ids': []},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 400 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'sku_ids': []},
    )
    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id=99999', json={'sku_ids': []},
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}',
        json={'sku_ids': ['11111111-1111-1111-1111-111111111111']},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 4,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '400': 1,
                    '404': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_products_info(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/products/info'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(f'{handle}', json={'product_ids': []})
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}',
        json={'product_ids': ['11111111-1111-1111-1111-111111111111']},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 2,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_places_categories(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/places/categories'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}',
        json={
            'places_categories': [
                {'place_id': PLACE_ID, 'categories': ['1', '2']},
            ],
        },
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}',
        json={
            'places_categories': [
                {'place_id': PLACE_ID, 'categories': ['1', '2']},
            ],
        },
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 2,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_categories_get_children(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/place/categories/get_children'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'category_ids': ['1', '2']},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id=99999', json={'category_ids': ['1', '2']},
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'category_ids': ['1', '2']},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 3,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '404': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_categories_get_parent(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/place/categories/get_parent'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'category_ids': ['1', '2']},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id=99999', json={'category_ids': ['1', '2']},
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'category_ids': ['1', '2']},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 3,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '404': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_products_search_by_barcode_or_vendor_code(
        mockserver,
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        testpoint,
):
    handle = '/v1/place/products/search-by-barcode-or-vendor-code'
    handle_id = f'{handle}_POST'

    @mockserver.handler('/eats-core-retail/v1/place/max-overweight/retrieve')
    def _mock(request):
        return mockserver.make_response(
            json={'max_overweight_in_percent': 0}, status=200,
        )

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}',
        json={'items': [{'vendor_code': '1', 'barcode': None}]},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 400 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}', json={'items': []},
    )
    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id=99999',
        json={'items': [{'vendor_code': '1', 'barcode': None}]},
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}',
        json={'items': [{'vendor_code': '1', 'barcode': None}]},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 4,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '400': 1,
                    '404': 1,
                },
            },
        },
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_rps_metrics_category_products_filtered(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, testpoint,
):
    handle = '/v1/place/category_products/filtered'
    handle_id = f'{handle}_POST'

    @testpoint(f'eats-nomenclature_handle-rps-data::use-current-epoch')
    def use_current_epoch(param):
        return {'use_current_epoch': True}

    inject_failure = True

    @testpoint(f'eats-nomenclature_{handle_id}::fail')
    def handle_inject_failure(param):
        return {'inject_failure': inject_failure}

    # exception fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}&category_id={CATEGORY_ID}',
        json={'filters': []},
    )
    assert handle_inject_failure.has_calls

    inject_failure = False

    # 400 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}&category_id={CATEGORY_ID}',
        json={
            'filters': [
                {
                    'id': 'fat_content',
                    'type': 'multiselect',
                    'chosen_options': ['not_decimal_value'],
                },
            ],
        },
    )
    # 404 fail
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id=99999&category_id={CATEGORY_ID}',
        json={'filters': []},
    )
    # 200 ok
    await taxi_eats_nomenclature.post(
        f'{handle}?place_id={PLACE_ID}&category_id={CATEGORY_ID}',
        json={'filters': []},
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    assert use_current_epoch.has_calls
    _verify_metrics(
        [handle_id],
        metrics[METRICS_NAME],
        rps_data_expected={
            handle_id: {
                'starts': 4,
                'oks': 1,
                'fails': {
                    '$meta': {'solomon_children_labels': 'error_code'},
                    'exception': 1,
                    '400': 1,
                    '404': 1,
                },
            },
        },
    )


def _verify_metrics(handle_names, metric_values, rps_data_expected):
    for handle_name in handle_names:
        assert metric_values['$meta'] == {
            'solomon_children_labels': 'handle_name',
        }
        assert metric_values[handle_name]['$meta'] == {
            'solomon_children_labels': 'source_name',
        }
        assert (
            metric_values[handle_name]['unknown']['starts']
            == rps_data_expected[handle_name]['starts']
        )
        assert (
            metric_values[handle_name]['unknown']['fails']
            == rps_data_expected[handle_name]['fails']
        )
        assert (
            metric_values[handle_name]['unknown']['oks']
            == rps_data_expected[handle_name]['oks']
        )
        for percentile in [
                'p0',
                'p50',
                'p90',
                'p95',
                'p98',
                'p99',
                'p99_6',
                'p99_9',
                'p100',
        ]:
            assert (
                metric_values[handle_name]['unknown']['timings']['1min'][
                    percentile
                ]
                >= 0
            )
