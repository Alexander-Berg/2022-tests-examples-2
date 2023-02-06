# pylint: disable=redefined-outer-name
import example_service.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['example_service.generated.service.pytest_plugins']
