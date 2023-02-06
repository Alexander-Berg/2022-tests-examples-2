# pylint: disable=redefined-outer-name
import fleet_notifications_telegram_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'fleet_notifications_telegram_bot.generated.service.pytest_plugins',
    'test_fleet_notifications_telegram_bot.plugins.mock_personal',
    'test_fleet_notifications_telegram_bot.plugins.mock_telegram',
]
