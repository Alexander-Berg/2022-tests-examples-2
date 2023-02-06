# pylint: disable = invalid-name,unused-variable
import datetime

import pytest

from eats_tips_payments.generated.cron import run_cron


def _insert_order(cursor, amount, status, updated_at, payment_type='b2p'):
    cursor.execute(
        """
        insert into eats_tips_payments.orders (
            payment_type,
            amount,
            status,
            updated_at
        ) values (
            %s, %s, %s, %s
        );""",
        (payment_type, amount, status, updated_at),
    )


@pytest.mark.now('2022-04-07 10:00:00+00:00')
async def test_send_stats_minutely(patch, pgsql, mockserver):
    updated_at_1_minute_ago = datetime.datetime(2022, 4, 7, 9, 59)
    updated_at_2_hour_ago = datetime.datetime(2022, 4, 7, 8, 0)
    updated_at_1_day_ago = datetime.datetime(2022, 4, 6, 10, 0)
    updated_at_last_month = datetime.datetime(2022, 3, 31, 0, 0)

    with pgsql['eats_tips_payments'].dict_cursor() as cursor:
        _insert_order(cursor, 100, 'COMPLETED', updated_at_1_minute_ago)
        _insert_order(cursor, 200, 'COMPLETED', updated_at_1_minute_ago)
        _insert_order(cursor, 10, 'FAILED', updated_at_1_minute_ago)
        _insert_order(cursor, 20, 'FAILED', updated_at_1_minute_ago)
        _insert_order(cursor, 50, 'COMPLETED', updated_at_2_hour_ago)
        _insert_order(cursor, 500, 'COMPLETED', updated_at_1_day_ago)
        _insert_order(cursor, 1000, 'COMPLETED', updated_at_last_month)

    values_by_sensor = {}

    @mockserver.json_handler('/solomon/')
    def _mock_solomon(request):
        for data in request.json['sensors']:
            values_by_sensor[data['labels']['sensor']] = data['value']
        return {}

    await run_cron.main(
        ['eats_tips_payments.crontasks.send_stats_minutely', '-t', '0'],
    )

    assert _mock_solomon.times_called == 3
    assert values_by_sensor['order_success_5m'] == 2
    assert int(values_by_sensor['order_fail_rate_5m'] * 2) == 1
    assert values_by_sensor['total_amount_cur_day'] == 350

    await run_cron.main(
        ['eats_tips_payments.crontasks.send_stats_daily', '-t', '0'],
    )

    assert values_by_sensor['total_amount_last_day'] == 500
    assert values_by_sensor['total_amount_cur_month'] == 850
    assert values_by_sensor['total_amount_last_month'] == 1000
