# pylint: disable=redefined-outer-name, protected-access

import pytest

from eats_supply_orders_bot.crontasks import display_orders
from eats_supply_orders_bot.generated.cron import run_cron
from eats_supply_orders_bot.internal import percent_change


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
async def test_should_correct_run_from_cron(
        cron_runner, mysql, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_DISPLAY_ORDERS_SETTINGS': load_json(
                'default_display_orders_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.display_orders', '-t', '0'],
    )


async def test_should_correct_return_query_settings(cron_context, load_json):

    worker = display_orders.DisplayOrdersWorker(
        cron_context.mysql.bigfood,
        cron_context.sqlt,
        cron_context.stq,
        cron_context.secdist,
        load_json('default_display_orders_notify_settings.json'),
        {},
    )
    assert list(worker.query_settings) == load_json(
        'correct_query_settings.json',
    )


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql', 'display_orders.sql'])
@pytest.mark.now('2021-02-01 02:40:00')
async def test_should_send_message_correct_times(
        cron_context, load_json, mysql, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_DISPLAY_ORDERS_SETTINGS': load_json(
                'default_display_orders_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.display_orders', '-t', '0'],
    )
    assert stq.orders_bot_send_message.times_called == 1


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
async def test_should_not_send_message_if_disable(
        cron_context, load_json, mysql, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_DISPLAY_ORDERS_SETTINGS': load_json(
                'disabled_display_orders_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.display_orders', '-t', '0'],
    )
    assert stq.orders_bot_send_message.times_called == 0


def test_should_correct_merge_data():
    current_data = [
        {'brand_id': 1, 'brand_name': 1, 'orders_count': 1, 'cte': 13},
    ]

    previous_data = [
        {'brand_id': 1, 'brand_name': 1, 'orders_count': 3, 'cte': 26},
    ]

    records = percent_change.apply(current_data, previous_data)

    assert len(records) == 1
    row = records[0]
    assert row['brand_id'] == 1
    assert row['brand_name'] == 1
    assert row['current_orders_count'] == current_data[0]['orders_count']
    assert row['current_cte'] == current_data[0]['cte']
    assert row['previous_orders_count'] == previous_data[0]['orders_count']
    assert row['previous_cte'] == previous_data[0]['cte']
    assert row['percent_change'] == -67
