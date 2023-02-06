import datetime as dt

import psycopg2
import pytest
import pytz

PERIODIC_NAME = 'eats_nomenclature-processing-errors-metrics'
METRICS_NAME = 'processing-errors-metrics'
PER_PLACE_METRICS_NAME = 'processing-errors-metrics-per-place'
PER_BRAND_METRICS_NAME = 'processing-errors-metrics-per-brand'
DATE_FORMAT = '%Y-%m-%d'

BRAND_ID_WITH_BRAND_SETTINGS = '2'
BRAND_SLUG_WITH_BRAND_SETTINGS = 'brand' + BRAND_ID_WITH_BRAND_SETTINGS

SOMETHING_FAILED_ERROR_TYPE = 1
DB_ERROR_TYPE = 2
# deprecated error, stays for mapping structure
# NON_DEFAULT_ASSORTMENT_IS_POTENTIALLY_DESTRUCTIVE = 3
TOO_MUCH_UNAVAILABLE_PRODUCTS = 4
TOO_MUCH_ZERO_STOCKS = 5
TOO_MUCH_ZERO_PRICES = 6
TOO_MUCH_PRODUCTS_WITHOUT_IMAGES = 7
PARTNER_ASSORTMENT_IS_POTENTIALLY_DESTRUCTIVE = 8
DEFAULT_ASSORTMENT_IS_POTENTIALLY_DESTRUCTIVE = 9

OLD_ASSORTMENT = 'old_assortment'
OLD_PRICES = 'old_prices'
OLD_AVAILABILITIES = 'old_availabilities'
OLD_STOCKS = 'old_stocks'
VERY_OLD_STOCKS = 'very_old_stocks'
WITHOUT_ASSORTMENT = 'without_assortment'


@pytest.mark.config(
    EATS_NOMENCLATURE_VERIFICATION={
        '__default__': {
            'assortment_outdated_threshold_in_hours': 2,
            'place_prices_outdated_threshold_in_minutes': 70,
            'place_availabilities_outdated_threshold_in_minutes': 70,
            'place_stocks_outdated_threshold_in_minutes': 70,
            'place_on_enabled_delay_in_hours': 1,
        },
        '3': {
            'assortment_outdated_threshold_in_hours': 1000,
            'place_prices_outdated_threshold_in_minutes': 1000,
            'place_availabilities_outdated_threshold_in_minutes': 1000,
            'place_stocks_outdated_threshold_in_minutes': 1000,
            'place_on_enabled_delay_in_hours': 1000,
        },
    },
    EATS_NOMENCLATURE_PROCESSING_ERRORS_METRICS_SETTINGS={
        'period_in_sec': 60,
        'is_enabled': True,
        'brand_settings': {
            '__default__': {
                'flapping_reasons': [],
                'not_flapping_threshold_in_minutes': 61,
                'flapping_threshold_in_minutes': 61,
            },
            BRAND_ID_WITH_BRAND_SETTINGS: {
                'flapping_reasons': [
                    'DB error occurred while processing assortment',
                ],
                'not_flapping_threshold_in_minutes': 5,
                'flapping_threshold_in_minutes': 10,
            },
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_processing_errors_metrics_detailed(
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        assert_place_error_metric,
        assert_place_warning_metric,
        testpoint,
):
    @testpoint(f'eats_nomenclature::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    handle_finished.next_call()

    error_date_from = (dt.datetime.now() - dt.timedelta(hours=1)).astimezone(
        pytz.UTC,
    )
    warning_date_from = (dt.datetime.now() - dt.timedelta(hours=3)).astimezone(
        pytz.UTC,
    )

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_values = metrics[METRICS_NAME]

    place_to_brand = _get_place_to_brand()

    task_types = ['nomenclature', 'price', 'stock', 'availability']
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
    place_to_error_types = _get_place_to_errors(include_disabled=True)
    for place_id, brand_slug in place_to_brand.items():
        if place_id not in place_to_error_types:
            # if place has no errors,
            # it doesn't fall into error metrics
            for task_type in task_types:
                assert_place_error_metric(
                    metric_values[task_type][brand_slug],
                    place_id,
                    expect_exists=False,
                )
        else:
            task_type_to_error = place_to_error_types[place_id]
            for task_type in task_types:
                if task_type in task_type_to_error:
                    error_type = task_type_to_error[task_type]
                    assert_place_error_metric(
                        metric_values[task_type][brand_slug],
                        place_id,
                        error_type,
                        error_date_from,
                    )
                else:
                    assert_place_error_metric(
                        metric_values[task_type][brand_slug],
                        place_id,
                        expect_exists=False,
                    )

    # outdated processing warnings
    warning_type_to_task_type = _get_warning_to_task_type()
    place_to_warning_types = _get_place_to_warnings()
    for place_id, brand_slug in place_to_brand.items():
        if place_id not in place_to_warning_types:
            # if place has no warnings or it is disabled,
            # it doesn't fall into outdated processing warnings
            for task_type in task_types:
                assert_place_warning_metric(
                    metric_values[task_type][brand_slug],
                    place_id,
                    expect_exists=False,
                )
        else:
            for warning_type, task_type in warning_type_to_task_type.items():
                if warning_type in place_to_warning_types[place_id]:
                    assert_place_warning_metric(
                        metric_values[task_type][brand_slug],
                        place_id,
                        warning_type,
                        warning_date_from,
                    )
                else:
                    assert_place_warning_metric(
                        metric_values[task_type][brand_slug],
                        place_id,
                        warning_type,
                        expect_exists=False,
                    )

    # brand3 has no warnings because of config settings
    for task_type in task_types:
        assert 'brand3' not in metric_values[task_type]


@pytest.mark.config(
    EATS_NOMENCLATURE_VERIFICATION={
        '__default__': {
            'assortment_outdated_threshold_in_hours': 2,
            'place_prices_outdated_threshold_in_minutes': 70,
            'place_availabilities_outdated_threshold_in_minutes': 70,
            'place_stocks_outdated_threshold_in_minutes': 70,
            'place_on_enabled_delay_in_hours': 1,
        },
        '3': {
            'assortment_outdated_threshold_in_hours': 1000,
            'place_prices_outdated_threshold_in_minutes': 1000,
            'place_availabilities_outdated_threshold_in_minutes': 1000,
            'place_stocks_outdated_threshold_in_minutes': 1000,
            'place_on_enabled_delay_in_hours': 1000,
        },
    },
    EATS_NOMENCLATURE_PROCESSING_ERRORS_METRICS_SETTINGS={
        'period_in_sec': 60,
        'is_enabled': True,
        'brand_settings': {
            '__default__': {
                'flapping_reasons': [],
                'not_flapping_threshold_in_minutes': 61,
                'flapping_threshold_in_minutes': 61,
            },
            BRAND_ID_WITH_BRAND_SETTINGS: {
                'flapping_reasons': [
                    'DB error occurred while processing assortment',
                ],
                'not_flapping_threshold_in_minutes': 5,
                'flapping_threshold_in_minutes': 10,
            },
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_processing_errors_metrics_per_place(
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        testpoint,
        pgsql,
        taxi_config,
):
    @testpoint(f'eats_nomenclature::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    def assert_zero_or_missing(metric, brand_slug, place_id, field_name):
        assert (
            (brand_slug not in metric)
            or (place_id not in metric[brand_slug])
            or (field_name not in metric[brand_slug][place_id])
            or (metric[brand_slug][place_id][field_name] == 0)
        )

    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_values = metrics[PER_PLACE_METRICS_NAME]
    brand_settings = taxi_config.get(
        'EATS_NOMENCLATURE_PROCESSING_ERRORS_METRICS_SETTINGS',
    )['brand_settings']

    place_to_brand = _get_place_to_brand()
    enabled_place_ids = _get_enabled_place_ids(pgsql)

    task_types = ['nomenclature', 'price', 'stock', 'availability']
    for task_type in task_types:
        assert metric_values[task_type]['$meta'] == {
            'solomon_children_labels': 'brand',
        }
        assert metric_values[task_type]['brand2']['$meta'] == {
            'solomon_children_labels': 'place_id',
        }

    # errors
    place_to_error_types = _get_place_to_errors(include_disabled=False)
    for place_id, brand_slug in place_to_brand.items():
        if (place_id not in place_to_error_types) or (
                place_id not in enabled_place_ids
        ):
            # if place has no errors,
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
                places_with_errors = _find_places_with_errors(
                    pgsql,
                    'brand2',
                    task_type,
                    place_to_error_types,
                    place_to_brand,
                    enabled_place_ids,
                    brand_settings,
                )
                if (
                        task_type in task_type_to_error
                        and place_id in places_with_errors
                ):
                    assert (
                        metric_values[task_type][brand_slug][place_id][
                            'total_error_count'
                        ]
                        == 1
                    )
                else:
                    assert_zero_or_missing(
                        metric_values[task_type],
                        brand_slug,
                        place_id,
                        'total_error_count',
                    )

    # outdated processing warnings
    warning_type_to_task_type = _get_warning_to_task_type()
    place_to_warning_types = _get_place_to_warnings()
    for place_id, brand_slug in place_to_brand.items():
        if (place_id not in place_to_warning_types) or (
                place_id not in enabled_place_ids
        ):
            # if place has no warnings or it is disabled,
            # it doesn't fall into outdated processing warnings
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

    for task_type in task_types:
        # brand1 has no errors/warnings
        # because it has no enabled places with errors/warnings
        assert 'brand1' not in metric_values[task_type]
        # brand3 has no errors/warnings because of config settings
        assert 'brand3' not in metric_values[task_type]


@pytest.mark.config(
    EATS_NOMENCLATURE_VERIFICATION={
        '__default__': {
            'assortment_outdated_threshold_in_hours': 2,
            'place_prices_outdated_threshold_in_minutes': 70,
            'place_availabilities_outdated_threshold_in_minutes': 70,
            'place_stocks_outdated_threshold_in_minutes': 70,
            'place_on_enabled_delay_in_hours': 1,
        },
        '3': {
            'assortment_outdated_threshold_in_hours': 1000,
            'place_prices_outdated_threshold_in_minutes': 1000,
            'place_availabilities_outdated_threshold_in_minutes': 1000,
            'place_stocks_outdated_threshold_in_minutes': 1000,
            'place_on_enabled_delay_in_hours': 1000,
        },
    },
    EATS_NOMENCLATURE_PROCESSING_ERRORS_METRICS_SETTINGS={
        'period_in_sec': 60,
        'is_enabled': True,
        'brand_settings': {
            '__default__': {
                'flapping_reasons': [],
                'not_flapping_threshold_in_minutes': 61,
                'flapping_threshold_in_minutes': 61,
            },
            BRAND_ID_WITH_BRAND_SETTINGS: {
                'flapping_reasons': [
                    'DB error occurred while processing assortment',
                ],
                'not_flapping_threshold_in_minutes': 5,
                'flapping_threshold_in_minutes': 10,
            },
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_processing_errors_metrics_per_brand(
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        pgsql,
        taxi_config,
        testpoint,
):
    @testpoint(f'eats_nomenclature::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    def assert_zero_or_missing(metric, field_name):
        assert (field_name not in metric) or (metric[field_name] == 0)

    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_values = metrics[PER_BRAND_METRICS_NAME]

    place_to_brand = _get_place_to_brand()
    enabled_place_ids = _get_enabled_place_ids(pgsql)
    brand_settings = taxi_config.get(
        'EATS_NOMENCLATURE_PROCESSING_ERRORS_METRICS_SETTINGS',
    )['brand_settings']

    task_types = ['nomenclature', 'price', 'stock', 'availability']
    for task_type in task_types:
        assert metric_values[task_type]['$meta'] == {
            'solomon_children_labels': 'brand',
        }

    # errors
    place_to_error_types = _get_place_to_errors(include_disabled=False)

    for task_type in task_types:
        # brand1 has no enabled places with errors/warnings
        assert 'brand1' not in metric_values[task_type]

    # brand2
    for task_type in task_types:
        places_with_errors = _find_places_with_errors(
            pgsql,
            'brand2',
            task_type,
            place_to_error_types,
            place_to_brand,
            enabled_place_ids,
            brand_settings,
        )
        if places_with_errors:
            assert metric_values[task_type]['brand2'][
                'total_error_count'
            ] == len(places_with_errors)
        else:
            assert_zero_or_missing(
                metric_values[task_type]['brand2'], 'total_error_count',
            )

    # warnings

    warning_to_task_type = _get_warning_to_task_type()
    place_to_warning_types = _get_place_to_warnings()

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

    # brand2
    for task_type in task_types:
        assert metric_values[task_type]['brand2'][
            'total_warning_count'
        ] == count_places_with_warnings('brand2', task_type)

    for task_type in task_types:
        # brand3 has no errors/warnings because of config settings
        assert 'brand3' not in metric_values[task_type]


@pytest.mark.config(
    EATS_NOMENCLATURE_VERIFICATION={
        '__default__': {
            'place_stocks_outdated_threshold_in_minutes': 70,
            'place_stocks_very_outdated_threshold_in_minutes': 1440,
            'place_on_enabled_delay_in_hours': 1,
        },
    },
    EATS_NOMENCLATURE_PROCESSING_ERRORS_METRICS_SETTINGS={
        'period_in_sec': 60,
        'is_enabled': True,
        'brand_settings': {
            '__default__': {
                'flapping_reasons': [],
                'not_flapping_threshold_in_minutes': 5,
                'flapping_threshold_in_minutes': 60,
            },
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_very_old_stocks.sql'],
)
async def test_very_old_stocks_warning(
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        assert_place_warning_metric,
        testpoint,
):
    @testpoint(f'eats_nomenclature::{METRICS_NAME}')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()

    brand_slug = 'brand1'
    place_id_with_very_old_stocks = '1'
    place_id_with_old_stocks = '2'

    place_to_warnings = {
        place_id_with_very_old_stocks: {
            'warnings': [OLD_STOCKS, VERY_OLD_STOCKS],
            'date_from': (
                dt.datetime.now() - dt.timedelta(hours=25)
            ).astimezone(pytz.UTC),
        },
        place_id_with_old_stocks: {
            'warnings': [OLD_STOCKS],
            'date_from': (
                dt.datetime.now() - dt.timedelta(hours=23)
            ).astimezone(pytz.UTC),
        },
    }

    # very_old_stocks_warning_count is only in brand metrics
    per_brand_metric_values = metrics[PER_BRAND_METRICS_NAME]
    assert (
        per_brand_metric_values['stock'][brand_slug]['total_warning_count']
        == 2
    )
    assert (
        per_brand_metric_values['stock'][brand_slug][
            'very_old_stocks_warning_count'
        ]
        == 1
    )

    per_place_metric_values = metrics[PER_PLACE_METRICS_NAME]
    for place_id, warnings_data in place_to_warnings.items():
        assert per_place_metric_values['stock'][brand_slug][place_id][
            'total_warning_count'
        ] == len(warnings_data['warnings'])
        assert (
            'very_old_stocks_warning_count'
            not in per_place_metric_values['stock'][brand_slug][place_id]
        )

    detailed_metric_values = metrics[METRICS_NAME]
    for place_id, warnings_data in place_to_warnings.items():
        warning_date_from = warnings_data['date_from']
        for warning in warnings_data['warnings']:
            assert_place_warning_metric(
                detailed_metric_values['stock'][brand_slug],
                place_id_with_very_old_stocks,
                warning,
                warning_date_from,
            )


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)


def _find_places_with_errors(
        pgsql,
        brand_slug,
        task_type,
        place_to_error_types,
        place_to_brand,
        enabled_place_ids,
        brand_settings,
):
    brand_settings = brand_settings[
        BRAND_ID_WITH_BRAND_SETTINGS
        if brand_slug == BRAND_SLUG_WITH_BRAND_SETTINGS
        else '__default__'
    ]
    errors_dict = place_to_error_types.items()
    return [
        place_id
        for place_id, task_type_to_error in errors_dict
        if (place_to_brand[place_id] == brand_slug)
        and (place_id in enabled_place_ids)
        and (task_type in task_type_to_error)
        and _is_task_error_old_enough(
            pgsql, brand_settings, place_id, task_type,
        )
    ]


def _get_status_or_text_changed_at_and_task_error(pgsql, place_id, task_type):
    cursor = pgsql['eats_nomenclature'].cursor()
    if task_type == 'nomenclature':
        cursor.execute(
            f"""
            select status_or_text_changed_at, task_error
            from eats_nomenclature.place_assortments_processing_last_status
            where place_id = '{place_id}'
            """,
        )
    else:
        cursor.execute(
            f"""
            select status_or_text_changed_at, task_error
            from eats_nomenclature.places_processing_last_status_v2
            where place_id = '{place_id}' and task_type = '{task_type}'
            """,
        )
    result = list(cursor)[0]
    return result[0], result[1]


def _is_task_error_old_enough(pgsql, brand_settings, place_id, task_type):
    status_or_text_changed_at, task_error = (
        _get_status_or_text_changed_at_and_task_error(
            pgsql, place_id, task_type,
        )
    )
    threshold = brand_settings[
        'flapping_threshold_in_minutes'
        if task_error in brand_settings['flapping_reasons']
        else 'not_flapping_threshold_in_minutes'
    ]
    return status_or_text_changed_at < dt.datetime.now(
        psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
    ) - dt.timedelta(minutes=threshold)


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
            metric_date = dt.datetime.utcfromtimestamp(
                place_metric['date_from'] / 1000,
            )
            assert metric_date.strftime(
                DATE_FORMAT,
            ) == expected_date_from.strftime(DATE_FORMAT)
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
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id
        from eats_nomenclature.places
        where is_enabled = true
        """,
    )
    result = list(cursor)
    return set(str(row[0]) for row in result)


def _get_place_to_brand():
    return {
        '1': 'brand1',
        '2': 'brand1',
        '3': 'brand2',
        '4': 'brand2',
        '5': 'brand2',
        '6': 'brand2',
        '7': 'brand2',
        '8': 'brand2',
        '9': 'brand2',
        '10': 'brand2',
        '11': 'brand2',
        '13': 'brand2',
        '14': 'brand2',
        '15': 'brand2',
    }


def _get_place_to_errors(include_disabled):
    result = {
        '3': {'nomenclature': PARTNER_ASSORTMENT_IS_POTENTIALLY_DESTRUCTIVE},
        '4': {'nomenclature': TOO_MUCH_UNAVAILABLE_PRODUCTS},
        '5': {'nomenclature': TOO_MUCH_ZERO_STOCKS},
        '6': {'nomenclature': TOO_MUCH_ZERO_PRICES},
        '7': {'nomenclature': TOO_MUCH_PRODUCTS_WITHOUT_IMAGES},
        '13': {
            'price': DB_ERROR_TYPE,
            'stock': SOMETHING_FAILED_ERROR_TYPE,
            'availability': DB_ERROR_TYPE,
        },
        '14': {'nomenclature': DB_ERROR_TYPE},
        '15': {'nomenclature': DEFAULT_ASSORTMENT_IS_POTENTIALLY_DESTRUCTIVE},
    }
    if include_disabled:
        result['2'] = {
            'nomenclature': SOMETHING_FAILED_ERROR_TYPE,
            'price': DB_ERROR_TYPE,
            'stock': SOMETHING_FAILED_ERROR_TYPE,
            'availability': DB_ERROR_TYPE,
        }
    return result


def _get_warning_to_task_type():
    return {
        OLD_ASSORTMENT: 'nomenclature',
        OLD_PRICES: 'price',
        OLD_AVAILABILITIES: 'availability',
        OLD_STOCKS: 'stock',
        VERY_OLD_STOCKS: 'stock',
        WITHOUT_ASSORTMENT: 'nomenclature',
    }


def _get_place_to_warnings():
    return {
        # these are all enabled places
        '3': [OLD_ASSORTMENT, OLD_PRICES, OLD_AVAILABILITIES, OLD_STOCKS],
        '4': [OLD_ASSORTMENT],
        '5': [OLD_PRICES],
        '6': [OLD_AVAILABILITIES],
        '7': [OLD_STOCKS],
        '8': [WITHOUT_ASSORTMENT],
        '9': [OLD_PRICES, OLD_AVAILABILITIES, OLD_STOCKS, WITHOUT_ASSORTMENT],
        # place12 has no warnings because of config settings for brand3
    }
