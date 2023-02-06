# pylint: disable=redefined-outer-name
import business_alerts.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'business_alerts.generated.service.pytest_plugins',
    'business_alerts.generated.service.clients.pytest_plugin',
]
