# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import re

import pytest


@pytest.mark.config(
    PRICING_ADMIN_HISTORY_ORDERS_VALIDATION_SETTINGS={
        'enabled': True,
        'min_days_ago': 2,
        'days_range': 0,
        'yql_request_timeout_sec': 30,
        'wait_between_checks_sec': 10,
        'random_sample_part': 0.9999,
        'orders_per_chunk': 100,
        'tables_time_lag_days_ago': 0,
        'tables_time_lag_days_forward': 0,
    },
)
@pytest.mark.yt(
    schemas=[
        'yt_order_verification_result_schema.yaml',
        'yt_taximeter_order_details_schema.yaml',
    ],
    dyn_table_data=[
        'yt_taximeter_order_details.yaml',
        'yt_order_verification_result.yaml',
    ],
)
@pytest.mark.config(PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=False)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2019-12-27T00:00:00+00:00')
async def test_history_orders_validation(
        taxi_pricing_admin,
        testpoint,
        yt_apply,
        order_archive_mock,
        load_json,
        open_file,
):

    backend_interpreter_validation = []
    tax_interpreter_validation = []

    # pylint: disable=invalid-name,unused-variable
    @testpoint('history_orders_validation_begin')
    def history_orders_validation_begin(data):
        yql_request = open_file('yql_request').read()
        assert re.match(yql_request, data['request'])

    # pylint: disable=invalid-name,unused-variable
    @testpoint('history_backend_interpretator_validation')
    def history_backend_interpretator_validation(data):
        backend_interpreter_validation.append(data)

    # pylint: disable=invalid-name,unused-variable
    @testpoint('history_taximeter_interpretator_validation')
    def history_taximeter_interpretator_validation(data):
        tax_interpreter_validation.append(data)

    # pylint: disable=invalid-name
    @testpoint('history_orders_validation_finished')
    def history_orders_validation_finished(data):
        pass

    order_archive_mock.set_order_proc(load_json('order_proc.json'))

    async with taxi_pricing_admin.spawn_task('history-orders-validation'):
        await history_orders_validation_finished.wait_call()
        assert backend_interpreter_validation == [
            {
                'expected_price': {'metadata': {'w': 80.0}, 'price': 562.0},
                'interpreted_price': {'metadata': {'w': 80.0}, 'price': 562.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000010',
                    'rounding_factor': 1.0,
                    'subject': 'user',
                },
            },
            {
                'expected_price': {'metadata': {'w': 38.0}, 'price': 496.0},
                'interpreted_price': {'metadata': {'w': 38.0}, 'price': 496.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000010',
                    'rounding_factor': 1.0,
                    'subject': 'driver',
                },
            },
            {
                'expected_price': {'metadata': {}, 'price': 200.0},
                'interpreted_price': {
                    'metadata': {'r': 150.0},
                    'price': 843.0,
                },
                'order_info': {
                    'order_id': '00000000000000000000000000000011',
                    'rounding_factor': 1.0,
                    'subject': 'user',
                },
            },
            {
                'expected_price': {'metadata': {}, 'price': 200.0},
                'interpreted_price': {'metadata': {'r': 49.0}, 'price': 747.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000011',
                    'rounding_factor': 1.0,
                    'subject': 'driver',
                },
            },
        ]

        assert tax_interpreter_validation == [
            {
                'expected_price': {'metadata': {'w': 80.0}, 'price': 562.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000010',
                    'rounding_factor': 1.0,
                    'subject': 'user',
                },
                'tax_price': 562.0,
            },
            {
                'expected_price': {'metadata': {'w': 38.0}, 'price': 496.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000010',
                    'rounding_factor': 1.0,
                    'subject': 'driver',
                },
                'tax_price': 496.0,
            },
            {
                'expected_price': {'metadata': {}, 'price': 200.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000011',
                    'rounding_factor': 1.0,
                    'subject': 'user',
                },
                'tax_price': 843.0,
            },
            {
                'expected_price': {'metadata': {}, 'price': 200.0},
                'order_info': {
                    'order_id': '00000000000000000000000000000011',
                    'rounding_factor': 1.0,
                    'subject': 'driver',
                },
                'tax_price': 747.0,
            },
        ]
