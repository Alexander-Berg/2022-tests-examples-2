import datetime as dt

import pytest
import pytz


METRICS_NAME = 'task-errors-metrics'
PER_PLACE_METRICS_NAME = 'task-errors-metrics-per-place'
PER_BRAND_METRICS_NAME = 'task-errors-metrics-per-brand'
DATE_FORMAT = '%Y-%m-%d'
TIMEOUT_REASONS = [
    'Connection timeout while fetch menu',
    'Connection timeout while fetch availability',
]
REASONS_TO_RETRY = ['Fail menu synchronization', 'Fetch menu fail']

ALL_OK = 0
SOMETHING_FAILED_ERROR_TYPE = 1
TIMEOUT_ERROR_TYPE = 2
FAILED_FETCH_500_ERROR_TYPE = 3
NOMENCLATURE_NO_CATEGORIES_ERROR_TYPE = 4
NOMENCLATURE_NO_PRODUCTS_ERROR_TYPE = 5
NOMENCLATURE_NEGATIVE_WEIGHT_ERROR_TYPE = 6
PRICE_NO_PRICES_ERROR_TYPE = 7
PRICE_ALL_PRICES_ARE_ZERO_ERROR_TYPE = 8
PRICE_NEGATIVE_PRICE_ERROR_TYPE = 9
STOCK_NO_STOCK_ERROR_TYPE = 10
STOCK_ALL_STOCKS_ARE_ZERO_ERROR_TYPE = 11
AVAILABILITY_NO_AVAILABILITY_ERROR_TYPE = 13
AVAILABILITY_ALL_AVAILABILITIES_FALSE_ERROR_TYPE = 14
EMPTY_MENU_IN_PLACE_ERROR_TYPE = 15
EMPTY_STOP_LIST_ERROR_TYPE = 16
UNSUPPORTED_AVAILABILITY_AGGREGATOR_ERROR_TYPE = 17
NEW_MENU_IS_MUCH_SMALLER_THAN_PREVIOUS = 18
FAILED_FETCH_400_ERROR_TYPE = 19
INCORRECT_DATA_FROM_PARTNER_ERROR_TYPE = 20
INTEGRATION_FAILED_ERROR_TYPE = 21
STOCK_TOO_BIG_STOCKS_ERROR_TYPE = 22
CONTENT_ERROR_TYPE = 23

CLIENT_CATEGORY_WITHOUT_ORIGIN_ID = 'client_category_without_origin_id'
NOT_EXISTING_PARENT_CATEGORY = 'not_existing_parent_category'
NO_CLIENT_CATEGORY_FOR_ORIGIN_ID = 'no_client_category_for_origin_id'
SKIPPED_ITEMS_WITH_NO_CLIENT_CATEGORIES = (
    'skipped_items_with_no_client_categories'
)
ITEMS_WITH_NOT_EXISTING_CATEGORY = 'items_with_not_existing_category'
MISMATCHED_ITEMS_WITH_SAME_ORIGIN_ID = 'mismatched_items_with_same_origin_id'


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_SCHEDULERS_SETTINGS={
        '__default__': {
            'enabled': True,
            'period_in_sec': 60,
            'batch_size': 1000,
            'max_attempts_count': 3,
            'attempts_period_in_sec': 300,
            'timeout_reasons': TIMEOUT_REASONS,
            'reasons_to_retry': REASONS_TO_RETRY,
        },
    },
)
async def test_task_errors_metrics_detailed(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        assert_place_error_metric,
        assert_place_warning_metric,
        update_taxi_config,
):
    _set_error_mapping_config(update_taxi_config)

    @testpoint(f'eats_nomenclature_collector::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{METRICS_NAME}',
    )
    handle_finished.next_call()

    expected_date_from = (
        dt.datetime.now() - dt.timedelta(hours=1)
    ).astimezone(pytz.UTC)

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    metric_values = metrics[METRICS_NAME]

    task_types = ['nomenclature', 'price', 'stock', 'availability']
    place_to_brand = _get_place_to_enabled_brand()
    place_to_error_types = _get_place_to_error_types(include_all=True)

    # common labels
    for task_type in task_types:
        assert metric_values[task_type]['$meta'] == {
            'solomon_children_labels': 'brand',
        }
        assert metric_values[task_type]['brand1']['$meta'] == {
            'solomon_children_labels': 'place_id',
        }
        assert metric_values[task_type]['brand2']['$meta'] == {
            'solomon_children_labels': 'place_id',
        }

    # errors
    for task_type in task_types:
        for place_id, brand_slug in place_to_brand.items():
            if (place_id in place_to_error_types) and (
                    task_type in place_to_error_types[place_id]
            ):
                assert_place_error_metric(
                    metric_values[task_type][brand_slug],
                    place_id,
                    place_to_error_types[place_id][task_type],
                    expected_date_from,
                )
            else:
                assert_place_error_metric(
                    metric_values[task_type][brand_slug],
                    place_id,
                    expect_exists=False,
                )

    # warnings
    warning_to_task_type = _get_warning_to_task_type()
    place_to_warning_types = _get_place_to_warning_types()
    for place_id, brand_slug in place_to_brand.items():
        if place_id not in place_to_warning_types:
            for task_type in task_types:
                assert_place_warning_metric(
                    metric_values[task_type][brand_slug],
                    place_id,
                    expect_exists=False,
                )
        else:
            for warning_type, task_type in warning_to_task_type.items():
                if warning_type in place_to_warning_types[place_id]:
                    assert_place_warning_metric(
                        metric_values[task_type][brand_slug],
                        place_id,
                        warning_type,
                        expected_date_from,
                    )
                else:
                    assert_place_warning_metric(
                        metric_values[task_type][brand_slug],
                        place_id,
                        warning_type,
                        expect_exists=False,
                    )

    # disabled brand
    for task_type in task_types:
        assert 'brand3' not in metric_values[task_type]


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_SCHEDULERS_SETTINGS={
        '__default__': {
            'enabled': True,
            'period_in_sec': 60,
            'batch_size': 1000,
            'max_attempts_count': 3,
            'attempts_period_in_sec': 300,
            'timeout_reasons': TIMEOUT_REASONS,
            'reasons_to_retry': REASONS_TO_RETRY,
        },
    },
)
@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_TASK_ERRORS_METRICS_SETTINGS={
        'period_in_sec': 60,
        'brand_settings': {
            '__default__': {
                'not_flapping_threshold_in_minutes': 10,
                'flapping_reasons': TIMEOUT_REASONS + REASONS_TO_RETRY,
                'flapping_threshold_in_minutes': 10,
            },
        },
    },
)
async def test_task_errors_metrics_per_place(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        pgsql,
):
    def assert_zero_or_missing(metric, brand_slug, place_id, field_name):
        assert (
            (brand_slug not in metric)
            or (place_id not in metric[brand_slug])
            or (field_name not in metric[brand_slug][place_id])
            or (metric[brand_slug][place_id][field_name] == 0)
        )

    @testpoint(f'eats_nomenclature_collector::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{METRICS_NAME}',
    )
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    metric_values = metrics[PER_PLACE_METRICS_NAME]

    task_types = ['nomenclature', 'price', 'stock', 'availability']
    place_to_brand = _get_place_to_enabled_brand()
    enabled_place_ids = _get_enabled_place_ids(pgsql)

    for task_type in task_types:
        assert metric_values[task_type]['$meta'] == {
            'solomon_children_labels': 'brand',
        }
        assert metric_values[task_type]['brand1']['$meta'] == {
            'solomon_children_labels': 'place_id',
        }
        assert metric_values[task_type]['brand2']['$meta'] == {
            'solomon_children_labels': 'place_id',
        }

    place_to_error_types = _get_place_to_error_types()
    for place_id, brand_slug in place_to_brand.items():
        if (place_id not in place_to_error_types) or (
                place_id not in enabled_place_ids
        ):
            # if place has no errors or it is disabled,
            # it doesn't fall into error metrics
            for task_type in task_types:
                assert_zero_or_missing(
                    metric_values[task_type],
                    brand_slug,
                    place_id,
                    'total_error_count',
                )
        else:
            task_type_to_error = place_to_error_types[place_id]
            for task_type in task_types:
                if task_type not in task_type_to_error:
                    assert_zero_or_missing(
                        metric_values[task_type],
                        brand_slug,
                        place_id,
                        'total_error_count',
                    )
                else:
                    assert metric_values[task_type][brand_slug][place_id][
                        'total_error_count'
                    ] == (1 if task_type_to_error[task_type] != ALL_OK else 0)

    warning_type_to_task_type = _get_warning_to_task_type()
    place_to_warning_types = _get_place_to_warning_types()
    for place_id, brand_slug in place_to_brand.items():
        if (place_id not in place_to_warning_types) or (
                place_id not in enabled_place_ids
        ):
            # if place has no warnings or it is disabled,
            # it doesn't fall into warnings
            for task_type in task_types:
                assert_zero_or_missing(
                    metric_values[task_type],
                    brand_slug,
                    place_id,
                    'total_warning_count',
                )
        else:
            for task_type in task_types:
                warnings_count = sum(
                    [
                        1
                        for warning in place_to_warning_types[place_id]
                        if warning_type_to_task_type[warning] == task_type
                    ],
                )
                if warnings_count == 0:
                    assert_zero_or_missing(
                        metric_values[task_type],
                        brand_slug,
                        place_id,
                        'total_warning_count',
                    )
                else:
                    assert (
                        metric_values[task_type][brand_slug][place_id][
                            'total_warning_count'
                        ]
                        == warnings_count
                    )

    # disabled brand
    for task_type in task_types:
        assert 'brand3' not in metric_values[task_type]


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_SCHEDULERS_SETTINGS={
        '__default__': {
            'enabled': True,
            'period_in_sec': 60,
            'batch_size': 1000,
            'max_attempts_count': 3,
            'attempts_period_in_sec': 300,
            'timeout_reasons': TIMEOUT_REASONS,
            'reasons_to_retry': REASONS_TO_RETRY,
        },
    },
)
@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_TASK_ERRORS_METRICS_SETTINGS={
        'period_in_sec': 60,
        'brand_settings': {
            '__default__': {
                'not_flapping_threshold_in_minutes': 10,
                'flapping_reasons': TIMEOUT_REASONS + REASONS_TO_RETRY,
                'flapping_threshold_in_minutes': 10,
            },
        },
    },
)
async def test_task_errors_metrics_per_brand(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        pgsql,
):
    def assert_zero_or_missing(metric, field_name):
        assert (field_name not in metric) or (metric[field_name] == 0)

    @testpoint(f'eats_nomenclature_collector::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{METRICS_NAME}',
    )
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    metric_values = metrics[PER_BRAND_METRICS_NAME]

    task_types = ['nomenclature', 'price', 'stock', 'availability']

    place_to_brand = _get_place_to_enabled_brand()
    enabled_place_ids = _get_enabled_place_ids(pgsql)

    for task_type in task_types:
        assert metric_values[task_type]['$meta'] == {
            'solomon_children_labels': 'brand',
        }

    # errors
    place_to_error_types = _get_place_to_error_types()

    def count_places_with_errors(brand_slug, task_type):
        errors_dict = place_to_error_types.items()
        return sum(
            [
                1
                if (place_to_brand[place_id] == brand_slug)
                and (task_type in task_type_to_error)
                and (task_type_to_error[task_type] != ALL_OK)
                else 0
                for place_id, task_type_to_error in errors_dict
            ],
        )

    for brand_slug in ['brand1', 'brand2']:
        for task_type in task_types:
            assert metric_values[task_type][brand_slug][
                'total_error_count'
            ] == count_places_with_errors(brand_slug, task_type)

    # warnings
    warning_to_task_type = _get_warning_to_task_type()
    place_to_warning_types = _get_place_to_warning_types()

    def count_places_with_warnings(brand_slug, task_type):
        return sum(
            [
                1
                if (place_to_brand[place_id] == brand_slug)
                and (place_id in enabled_place_ids)
                and any(
                    warning_to_task_type[warning] == task_type
                    for warning in warnings
                )
                else 0
                for place_id, warnings in place_to_warning_types.items()
            ],
        )

    # brand1
    for task_type in task_types:
        assert_zero_or_missing(
            metric_values[task_type]['brand1'], 'total_warning_count',
        )

    # brand2
    for task_type in task_types:
        if task_type == 'nomenclature':
            assert metric_values[task_type]['brand2'][
                'total_warning_count'
            ] == count_places_with_warnings('brand2', task_type)
        else:
            assert_zero_or_missing(
                metric_values[task_type]['brand2'], 'total_warning_count',
            )

    # disabled brand
    for task_type in task_types:
        assert 'brand3' not in metric_values[task_type]


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(
        f'eats-nomenclature-collector_{METRICS_NAME}', is_distlock=False,
    )


def _set_error_mapping_config(update_taxi_config):
    update_taxi_config(
        'EATS_NOMENCLATURE_COLLECTOR_ERROR_MAPPING_SETTINGS',
        {
            'error_text_mapping': {
                'content_error': [
                    'Wrong place group, cannot find place',
                    'Empty field origin_id',
                    'Not found parser name to processing',
                ],
                'empty_menu': ['Empty menu in place'],
                'empty_stop_list': ['Empty stop list'],
                'failed_fetch_400': [
                    'Fetch data fail 400',
                    'Fetch data fail 401',
                    'Fetch data fail 403',
                    'Fetch data fail 404',
                    'Fetch data fail 429',
                ],
                'failed_fetch_500': [
                    'Fetch menu fail',
                    'Stocks fetch fail',
                    'Fetch data fail 500',
                    'Fetch data fail 501',
                    'Fetch data fail 502',
                    'Fetch data fail 503',
                    'Fetch data fail 504',
                ],
                'false_availability': ['All availability false'],
                'incorrect_data_from_partner': [
                    'Incorrect data from partner',
                    'New error from partner',  # test value
                ],
                'integration_failed': [
                    'Fail menu synchronization',
                    'Fail synchronization',
                    'Task is abandoned and was stopped',
                    '',
                ],
                'negative_prices': ['Has negative prices'],
                'negative_weight': ['Negative weight in nomenclature'],
                'no_availability': ['No availability'],
                'no_categories': ['No categories in nomenclature'],
                'no_prices': ['No prices'],
                'no_products': ['No products in nomenclature'],
                'no_stocks': ['No stocks'],
                'too_big_stocks': ['Stock value is too big'],
                'smaller_menu': ['New menu is much smaller than previous'],
                'timeout': [
                    'Connection timeout while fetch menu',
                    'Connection timeout while fetch availability',
                ],
                'unsupported_availability_aggregator': [
                    'Unsupported availability aggregator',
                ],
                'zero_prices': ['All prices are zero'],
                'zero_stocks': ['All stocks are zero'],
            },
        },
    )


@pytest.fixture(name='assert_place_error_metric')
def _assert_place_error_metric():
    def do_assert_place_error_metric(
            brand_metric,
            place_id,
            expected_error_type=None,
            expected_date_from=None,
            expect_exists=True,
    ):
        if expect_exists:
            place_metric = brand_metric[place_id]
            assert place_metric['error_type'] == expected_error_type
            if expected_error_type != ALL_OK and expected_date_from:
                metric_date = dt.datetime.utcfromtimestamp(
                    place_metric['date_from'] / 1000,
                )
                assert metric_date.strftime(
                    DATE_FORMAT,
                ) == expected_date_from.strftime(DATE_FORMAT)
            else:
                assert 'date_from' not in place_metric
        else:
            assert (place_id not in brand_metric) or (
                'error_type' not in brand_metric[place_id]
            )

    return do_assert_place_error_metric


@pytest.fixture(name='assert_place_warning_metric')
def _assert_place_warning_metric():
    def do_assert_place_warning_metric(
            brand_metric,
            place_id,
            expected_warning_type=None,
            expected_date_from=None,
            expect_exists=True,
    ):
        if expect_exists:
            place_metric = brand_metric[place_id]
            assert expected_warning_type in place_metric['warning_types']
            result_date_from = place_metric['warning_types'][
                expected_warning_type
            ]
            metric_date = dt.datetime.utcfromtimestamp(result_date_from / 1000)
            assert metric_date.strftime(
                DATE_FORMAT,
            ) == expected_date_from.strftime(DATE_FORMAT)
        else:
            assert (
                (place_id not in brand_metric)
                or ('warning_types' not in brand_metric[place_id])
                or (
                    expected_warning_type
                    not in brand_metric[place_id]['warning_types']
                )
            )

    return do_assert_place_warning_metric


def _get_enabled_place_ids(pgsql):
    cursor = pgsql['eats_nomenclature_collector'].cursor()
    cursor.execute(
        f"""
        select id
        from eats_nomenclature_collector.places
        where is_enabled = true
        """,
    )
    result = list(cursor)
    return set(row[0] for row in result)


def _get_place_to_enabled_brand():
    return {
        '1': 'brand1',
        '2': 'brand1',
        '3': 'brand1',
        '4': 'brand1',
        '5': 'brand1',
        '6': 'brand2',
        '7': 'brand2',
        '8': 'brand2',
        '9': 'brand2',
        '10': 'brand2',
        '11': 'brand2',
        '12': 'brand2',
        '13': 'brand2',
        '14': 'brand2',
        '15': 'brand2',
        '16': 'brand2',
        '18': 'brand2',
    }


def _get_place_to_error_types(include_all=False):
    result = {
        '1': {},
        '3': {
            'nomenclature': FAILED_FETCH_500_ERROR_TYPE,
            'price': FAILED_FETCH_500_ERROR_TYPE,
            'stock': FAILED_FETCH_500_ERROR_TYPE,
            'availability': FAILED_FETCH_500_ERROR_TYPE,
        },
        '4': {
            'nomenclature': SOMETHING_FAILED_ERROR_TYPE,
            'price': SOMETHING_FAILED_ERROR_TYPE,
            'stock': SOMETHING_FAILED_ERROR_TYPE,
            'availability': SOMETHING_FAILED_ERROR_TYPE,
        },
        '5': {
            'nomenclature': SOMETHING_FAILED_ERROR_TYPE,
            'price': SOMETHING_FAILED_ERROR_TYPE,
            'stock': SOMETHING_FAILED_ERROR_TYPE,
            'availability': SOMETHING_FAILED_ERROR_TYPE,
        },
        '6': {
            'nomenclature': NOMENCLATURE_NO_CATEGORIES_ERROR_TYPE,
            'price': PRICE_NO_PRICES_ERROR_TYPE,
            'stock': STOCK_NO_STOCK_ERROR_TYPE,
            'availability': AVAILABILITY_NO_AVAILABILITY_ERROR_TYPE,
        },
        '7': {
            'nomenclature': NOMENCLATURE_NO_PRODUCTS_ERROR_TYPE,
            'price': PRICE_ALL_PRICES_ARE_ZERO_ERROR_TYPE,
            'stock': STOCK_ALL_STOCKS_ARE_ZERO_ERROR_TYPE,
            'availability': AVAILABILITY_ALL_AVAILABILITIES_FALSE_ERROR_TYPE,
        },
        '8': {
            'nomenclature': NOMENCLATURE_NEGATIVE_WEIGHT_ERROR_TYPE,
            'price': PRICE_NEGATIVE_PRICE_ERROR_TYPE,
            'stock': ALL_OK,
            'availability': ALL_OK,
        },
        '10': {
            'nomenclature': ALL_OK,
            'price': ALL_OK,
            'stock': EMPTY_STOP_LIST_ERROR_TYPE,
            'availability': ALL_OK,
        },
        '11': {
            'nomenclature': ALL_OK,
            'price': PRICE_ALL_PRICES_ARE_ZERO_ERROR_TYPE,
            'stock': ALL_OK,
            'availability': ALL_OK,
        },
        '14': {
            'nomenclature': NEW_MENU_IS_MUCH_SMALLER_THAN_PREVIOUS,
            'price': ALL_OK,
            'stock': ALL_OK,
            'availability': ALL_OK,
        },
        '15': {
            'nomenclature': INTEGRATION_FAILED_ERROR_TYPE,
            'price': FAILED_FETCH_400_ERROR_TYPE,
            'stock': INCORRECT_DATA_FROM_PARTNER_ERROR_TYPE,
            'availability': INCORRECT_DATA_FROM_PARTNER_ERROR_TYPE,
        },
        '16': {
            'nomenclature': ALL_OK,
            'price': ALL_OK,
            'stock': STOCK_TOO_BIG_STOCKS_ERROR_TYPE,
            'availability': ALL_OK,
        },
        '18': {
            'nomenclature': CONTENT_ERROR_TYPE,
            'price': ALL_OK,
            'stock': ALL_OK,
            'availability': ALL_OK,
        },
    }
    if include_all:
        result['2'] = {
            'nomenclature': TIMEOUT_ERROR_TYPE,
            'price': TIMEOUT_ERROR_TYPE,
            'stock': TIMEOUT_ERROR_TYPE,
            'availability': TIMEOUT_ERROR_TYPE,
        }
        result['9'] = {
            'nomenclature': EMPTY_MENU_IN_PLACE_ERROR_TYPE,
            'price': ALL_OK,
            'stock': ALL_OK,
            'availability': UNSUPPORTED_AVAILABILITY_AGGREGATOR_ERROR_TYPE,
        }
    return result


def _get_warning_to_task_type():
    return {
        CLIENT_CATEGORY_WITHOUT_ORIGIN_ID: 'nomenclature',
        NOT_EXISTING_PARENT_CATEGORY: 'nomenclature',
        NO_CLIENT_CATEGORY_FOR_ORIGIN_ID: 'nomenclature',
        SKIPPED_ITEMS_WITH_NO_CLIENT_CATEGORIES: 'nomenclature',
        ITEMS_WITH_NOT_EXISTING_CATEGORY: 'nomenclature',
        MISMATCHED_ITEMS_WITH_SAME_ORIGIN_ID: 'nomenclature',
    }


def _get_place_to_warning_types():
    return {
        '11': [
            CLIENT_CATEGORY_WITHOUT_ORIGIN_ID,
            NOT_EXISTING_PARENT_CATEGORY,
            NO_CLIENT_CATEGORY_FOR_ORIGIN_ID,
        ],
        '12': [
            CLIENT_CATEGORY_WITHOUT_ORIGIN_ID,
            SKIPPED_ITEMS_WITH_NO_CLIENT_CATEGORIES,
            ITEMS_WITH_NOT_EXISTING_CATEGORY,
        ],
        '13': [MISMATCHED_ITEMS_WITH_SAME_ORIGIN_ID],
    }
