# pylint: disable=redefined-outer-name
import scooter_accumulator_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'scooter_accumulator_bot.generated.service.pytest_plugins',
    'test_scooter_accumulator_bot.plugins.mock_personal',
    'test_scooter_accumulator_bot.plugins.mock_profile',
    'test_scooter_accumulator_bot.plugins.mock_scooter_accumulator',
    'test_scooter_accumulator_bot.plugins.mock_scooters_misc',
    'test_scooter_accumulator_bot.plugins.mock_scooter_backend',
    'test_scooter_accumulator_bot.plugins.mock_scooters_ops_repair',
    'test_scooter_accumulator_bot.plugins.mock_experiments3',
]
