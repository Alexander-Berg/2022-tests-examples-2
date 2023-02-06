# pylint: disable=redefined-outer-name
import supportai_telephony_integration.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'supportai_telephony_integration.generated.service.pytest_plugins',
]
