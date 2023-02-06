# pylint: disable=redefined-outer-name
import eats_contact_center_monitoring.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'eats_contact_center_monitoring.generated.service.pytest_plugins',
]
