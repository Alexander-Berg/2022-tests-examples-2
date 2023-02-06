import logging

import http_proxy.generated.pytest_init  # noqa: F401,E501 pylint: disable=unused-import

logger = logging.getLogger(__name__)

pytest_plugins = [
    'http_proxy.pytest_plugin',
    'http_proxy.generated.pytest_plugins',
]
