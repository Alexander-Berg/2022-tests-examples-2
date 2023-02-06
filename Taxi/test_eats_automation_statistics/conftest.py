# pylint: disable=redefined-outer-name
import eats_automation_statistics.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'eats_automation_statistics.generated.service.pytest_plugins',
]
