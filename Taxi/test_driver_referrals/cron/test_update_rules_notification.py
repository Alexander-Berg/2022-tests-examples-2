# pylint: disable=redefined-outer-name,unused-variable,global-statement
import datetime

import pytest

from driver_referrals.common import db
from driver_referrals.common import models
from driver_referrals.common import notification


NOW = '2019-03-15 10:10'


@pytest.mark.now(NOW)
@pytest.mark.config(
    DRIVER_REFERRALS_NOTIFICATIONS_RULES_UPDATED_PARAMS={
        'min_days_between_notifications': 3,
    },
)
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals_web.sql'])
@pytest.mark.parametrize(
    'days_before, can_send',
    (
        pytest.param(4, True, id='last notification was long ago'),
        pytest.param(2, False, id='last notification was recently'),
        pytest.param(3, False, id='last notification was in exact day'),
    ),
)
async def test_check_can_send_updates_rule_notification(
        cron_context, days_before, can_send,
):
    today = datetime.datetime.now(tz=datetime.timezone.utc)
    a_few_days_before = today - datetime.timedelta(days=days_before)
    await db.insert_dates_into_rules_update(
        cron_context, today, a_few_days_before,
    )
    result = await notification.can_send_new_rule_notification(cron_context)
    assert result == can_send


@pytest.mark.now(NOW)
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals_web.sql'])
@pytest.mark.parametrize(
    'field_to_update',
    (
        pytest.param('last_start_time', id='last_start_time'),
        pytest.param('last_notification_time', id='last_notification_time'),
    ),
)
async def test_update_last_start_time(cron_context, field_to_update):
    # Пустая таблица
    rules_update = await db.get_last_rules_update(cron_context)
    assert rules_update is None

    current_date = datetime.datetime.now(tz=datetime.timezone.utc)

    # Инициализируем таблицу текущей датой
    await db.insert_dates_into_rules_update(
        cron_context, current_date, current_date,
    )
    rules_update = await db.get_last_rules_update(cron_context)
    assert rules_update[field_to_update] == current_date

    # Добавляем завтрашнюю дату (поле должно обновиться)
    tommorow = current_date + datetime.timedelta(days=1)
    if field_to_update == 'last_start_time':
        await db.update_last_rule_start_time(cron_context, tommorow)
    if field_to_update == 'last_notification_time':
        await db.update_rules_update_notif_time(cron_context, tommorow)

    rules_update = await db.get_last_rules_update(cron_context)
    assert rules_update[field_to_update] == tommorow

    # Добавляем текущую дату (поле не должно обновиться)
    if field_to_update == 'last_start_time':
        await db.update_last_rule_start_time(cron_context, current_date)
    if field_to_update == 'last_notification_time':
        await db.update_rules_update_notif_time(cron_context, current_date)
    rules_update = await db.get_last_rules_update(cron_context)
    assert rules_update[field_to_update] == tommorow


@pytest.mark.now(NOW)
@pytest.mark.config(
    DRIVER_REFERRALS_NOTIFICATIONS_RULES_UPDATED_PARAMS={
        'min_days_between_notifications': 3,
    },
)
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals_web.sql'])
async def test_check_can_send_updates_rule_notification_init(cron_context):
    # таблица rules_update - пустая
    last_rules_update = await db.get_last_rules_update(cron_context)
    assert last_rules_update is None

    # Должно вернуться False и добавиться пустая строка
    can_send = await notification.can_send_new_rule_notification(cron_context)
    last_rules_update = await db.get_last_rules_update(cron_context)
    assert last_rules_update is not None
    assert can_send is False


# для параметризации конфига
def mark_config_driver(
        referrer_orders_providers, min_days_between_notifications,
):
    return pytest.mark.config(
        DRIVER_REFERRALS_NOTIFICATIONS_RULES_UPDATED_PARAMS={
            'min_days_between_notifications': min_days_between_notifications,
            'last_days_from_cache': 10,
        },
        DRIVER_REFERRALS_NOTIFICATIONS_BY_COUNTRIES={
            '__default__': {
                'eda': (
                    ['rules_updated']
                    if 'eda' in referrer_orders_providers
                    else []
                ),
                'taxi': (
                    ['rules_updated']
                    if 'taxi' in referrer_orders_providers
                    else []
                ),
            },
        },
    )


@pytest.mark.now(NOW)
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals_web.sql'])
@pytest.mark.parametrize(
    'number_of_notifications, notifications_result, last_exp_rule_start_time',
    [
        pytest.param(
            1,
            [('p0', 'd7')],
            '2019-03-13',
            marks=mark_config_driver(['eda'], 1),
            id='1',
        ),
        pytest.param(
            3,
            [('p0', 'd7'), ('p1', 'd5'), ('p0', 'd1')],
            '2019-03-13',
            marks=mark_config_driver(['eda', 'taxi'], 1),
            id='2',
        ),
        pytest.param(
            0,
            [],
            '2019-03-11',
            marks=mark_config_driver(['eda', 'taxi'], 4),
            id='3',
        ),
    ],
)
async def test_add_notifications_for_new_rules(
        cron_context,
        number_of_notifications,
        notifications_result,
        last_exp_rule_start_time,
):
    current_date = datetime.datetime.now(tz=datetime.timezone.utc)
    four_days_ago = current_date - datetime.timedelta(days=4)
    await db.insert_dates_into_rules_update(
        cron_context, four_days_ago, four_days_ago,
    )

    can_send_notification = await notification.can_send_new_rule_notification(
        cron_context,
    )

    # если можем, то добавляем нотификации, если есть новые правила
    if can_send_notification:
        await notification.add_notifications_for_new_rules(cron_context)

    last_rules_update = await db.get_last_rules_update(context=cron_context)
    assert (
        last_rules_update['last_start_time'].strftime('%Y-%m-%d')
        == last_exp_rule_start_time
    )

    notifications = await db.get_notifications(
        context=cron_context,
        notification_status=models.NotificationStatus.CREATED,
    )
    assert len(notifications) == number_of_notifications

    for notif in notifications:
        assert (
            notif.referrer_park_id,
            notif.referrer_driver_id,
        ) in notifications_result
