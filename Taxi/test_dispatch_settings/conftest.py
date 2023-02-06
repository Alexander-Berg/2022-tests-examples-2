# pylint: disable=redefined-outer-name
import dispatch_settings.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'dispatch_settings.generated.service.pytest_plugins',
    'test_dispatch_settings.web.plugins.mock_tariffs',
]
