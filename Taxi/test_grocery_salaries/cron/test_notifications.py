# pylint: disable=redefined-outer-name
# flake8: noqa: E501
import datetime as dt

import pytest

from grocery_salaries.salaries.notifications.send_neto_notifications import (
    NetoNotificator,
)
from grocery_salaries.salaries.notifications.send_self_employed_notifications import (
    SENotificator,
)


@pytest.mark.now('2022-07-04 11:00:00')
@pytest.mark.yt(static_table_data=['yt/salaries_self_employed.yaml'])
async def test_send_self_employed_notifications(
        patch, cron_context, yt_apply, mock_yt,
):
    result = {
        'performer_id': (
            '00000000000000000000000000000000_11111111111111111111111111111111'
        ),
        'title': {
            'key': 'performer_income_israel_self_employed_weekly_report_title',
            'args': [],
        },
        'text': {
            'key': (
                'performer_income_israel_self_employed_weekly_report_template'
            ),
            'args': [
                {
                    'name': 'period_start',
                    'value': {'value': '27.06', 'type': 'string'},
                },
                {
                    'name': 'period_end',
                    'value': {'value': '10.07', 'type': 'string'},
                },
                {'name': 'order_count', 'value': {'value': 8, 'type': 'int'}},
                {
                    'name': 'hours_total',
                    'value': {'value': '6.06', 'type': 'string'},
                },
                {
                    'name': 'total_income',
                    'value': {
                        'value': '330.25',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'weekdays_hours',
                    'value': {'value': '6.06', 'type': 'string'},
                },
                {
                    'name': 'weekdays_duration_income',
                    'value': {
                        'value': '236.34',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'weekdays_orders',
                    'value': {'value': 8, 'type': 'int'},
                },
                {
                    'name': 'weekdays_orders_income',
                    'value': {
                        'value': '64',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'weekdays_income',
                    'value': {
                        'value': '300.34',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'weekends_hours',
                    'value': {'value': '0.0', 'type': 'string'},
                },
                {
                    'name': 'weekends_duration_income',
                    'value': {
                        'value': '0.0',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'weekends_orders',
                    'value': {'value': 0, 'type': 'int'},
                },
                {
                    'name': 'weekends_orders_income',
                    'value': {
                        'value': '0',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'weekends_income',
                    'value': {
                        'value': '0.0',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'tips',
                    'value': {
                        'value': '29.91',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'adjustment',
                    'value': {
                        'value': '0.0',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {'name': 'rainy_orders', 'value': {'value': 0, 'type': 'int'}},
            ],
        },
        'depot_id': '12345',
        'feeds_service': 'contractor-money',
    }
    test_result = {}

    @patch(
        'grocery_salaries.salaries.notifications.send_self_employed_notifications.'
        'SENotificator._send_message',
    )
    async def _send_message(task_id, message):
        test_result.update(message)

    first_date = dt.date(year=2022, month=6, day=27)
    last_date = dt.date(year=2022, month=7, day=10)

    notificator = SENotificator(cron_context, first_date, last_date)
    await notificator.run()

    assert result == test_result


@pytest.mark.now('2022-07-04 11:00:00')
@pytest.mark.yt(static_table_data=['yt/salaries_neto.yaml'])
async def test_send_neto_notifications(patch, cron_context, yt_apply, mock_yt):
    result = {
        'performer_id': (
            '00000000000000000000000000000000_11111111111111111111111111111111'
        ),
        'title': {
            'key': 'performer_income_israel_neto_weekly_report_title',
            'args': [],
        },
        'text': {
            'key': 'performer_income_israel_neto_weekly_report_template',
            'args': [
                {
                    'name': 'period_start',
                    'value': {'value': '01.07', 'type': 'string'},
                },
                {
                    'name': 'period_end',
                    'value': {'value': '31.07', 'type': 'string'},
                },
                {'name': 'order_count', 'value': {'value': 17, 'type': 'int'}},
                {
                    'name': 'hours_total',
                    'value': {'value': '8.03', 'type': 'string'},
                },
                {
                    'name': 'weekdays_orders',
                    'value': {'value': 0, 'type': 'int'},
                },
                {
                    'name': 'weekdays_hours',
                    'value': {'value': '0.0', 'type': 'string'},
                },
                {
                    'name': 'weekdays_hours_100',
                    'value': {'value': '0.0', 'type': 'string'},
                },
                {
                    'name': 'weekdays_hours_125',
                    'value': {'value': '0.0', 'type': 'string'},
                },
                {
                    'name': 'weekdays_hours_150',
                    'value': {'value': '0.0', 'type': 'string'},
                },
                {
                    'name': 'weekends_orders',
                    'value': {'value': 17, 'type': 'int'},
                },
                {
                    'name': 'weekends_hours',
                    'value': {'value': '8.03', 'type': 'string'},
                },
                {
                    'name': 'weekends_hours_100',
                    'value': {'value': '8.0', 'type': 'string'},
                },
                {
                    'name': 'weekends_hours_125',
                    'value': {'value': '0.03', 'type': 'string'},
                },
                {
                    'name': 'weekends_hours_150',
                    'value': {'value': '0.0', 'type': 'string'},
                },
                {
                    'name': 'tips',
                    'value': {
                        'value': '68.37',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {
                    'name': 'adjustment',
                    'value': {
                        'value': '0.0',
                        'type': 'price',
                        'currency': 'ILS',
                    },
                },
                {'name': 'rainy_orders', 'value': {'value': 0, 'type': 'int'}},
            ],
        },
        'depot_id': '12345',
        'feeds_service': 'contractor-money',
    }
    test_result = {}

    @patch(
        'grocery_salaries.salaries.notifications.send_neto_notifications.'
        'NetoNotificator._send_message',
    )
    async def _send_message(task_id, message):
        test_result.update(message)

    first_date = dt.date(year=2022, month=7, day=1)
    last_date = dt.date(year=2022, month=7, day=31)

    notificator = NetoNotificator(cron_context, first_date, last_date)
    await notificator.run()

    assert result == test_result
