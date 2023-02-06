# pylint: disable=redefined-outer-name
import contractor_merch_integration_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'contractor_merch_integration_api.generated.service.pytest_plugins',
]
