# pylint: disable=redefined-outer-name
import parks_balances_info_notifier_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'parks_balances_info_notifier_bot.generated.service.pytest_plugins',
    'test_parks_balances_info_notifier_bot.plugins.mock_telegram',
]
