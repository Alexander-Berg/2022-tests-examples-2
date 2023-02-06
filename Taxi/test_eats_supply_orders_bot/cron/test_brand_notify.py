# pylint: disable=redefined-outer-name, protected-access

import pytest

from eats_supply_orders_bot.crontasks import brand_notify
from eats_supply_orders_bot.generated.cron import run_cron


def get_notification_count(pgsql):
    with pgsql['eats_supply_orders_bot'].cursor() as cursor:
        cursor.execute('select count(*) from order_history_notifications')
        count = list(row[0] for row in cursor)[0]
    return count


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
async def test_should_correct_run_from_cron(
        cron_runner, mysql, taxi_config, load_json,
):
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_BRAND_NOTIFY_SETTINGS': load_json(
                'default_brand_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.brand_notify', '-t', '0'],
    )


async def test_should_correct_return_query_settings(cron_context, load_json):
    worker = brand_notify.BrandNotifyWorker(
        cron_context.pg,
        cron_context.mysql.bigfood,
        cron_context.sqlt,
        cron_context.stq,
        cron_context.secdist,
        load_json('default_brand_notify_settings.json'),
        {},
    )
    assert list(worker.query_settings) == load_json(
        'correct_query_settings.json',
    )


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
async def test_should_send_message_correct_times(
        cron_context, load_json, mysql, stq, taxi_config, pgsql,
):
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_BRAND_NOTIFY_SETTINGS': load_json(
                'default_brand_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.brand_notify', '-t', '0'],
    )
    assert stq.orders_bot_send_message.times_called == 3


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
async def test_should_insert_notification_history_if_not_exist(
        cron_context, load_json, mysql, stq, taxi_config, pgsql,
):
    assert get_notification_count(pgsql) == 0
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_BRAND_NOTIFY_SETTINGS': load_json(
                'default_brand_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.brand_notify', '-t', '0'],
    )
    assert get_notification_count(pgsql) == 3


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
@pytest.mark.pgsql(
    'eats_supply_orders_bot', files=['notification_history.sql'],
)
async def test_should_find_not_sent_orders(
        cron_context, load_json, mysql, pgsql,
):
    worker = brand_notify.BrandNotifyWorker(
        cron_context.pg,
        cron_context.mysql.bigfood,
        cron_context.sqlt,
        cron_context.stq,
        cron_context.secdist,
        load_json('default_brand_notify_settings.json'),
        {},
    )
    message_data = [x async for x in worker._get_message_data()]
    assert len(message_data[0]['records']) == 2


@pytest.mark.mysql('bigfood', files=['my_bigfood.sql'])
async def test_should_not_send_message_if_disable(
        cron_context, load_json, mysql, stq, taxi_config, pgsql,
):
    taxi_config.set_values(
        {
            'EATS_SUPPLY_ORDERS_BOT_BRAND_NOTIFY_SETTINGS': load_json(
                'disabled_brand_notify_settings.json',
            ),
        },
    )
    await run_cron.main(
        ['eats_supply_orders_bot.crontasks.brand_notify', '-t', '0'],
    )
    assert stq.orders_bot_send_message.times_called == 0
