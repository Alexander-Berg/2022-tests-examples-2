# pylint: disable=redefined-outer-name
import eats_supply_orders_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'eats_supply_orders_bot.generated.service.pytest_plugins',
    'test_eats_supply_orders_bot.plugins.mock_personal',
]
