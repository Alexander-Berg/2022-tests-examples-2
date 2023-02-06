# pylint: disable=redefined-outer-name
import user_wallet.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'user_wallet.generated.pytest_plugins',
    'taxi.pytest_plugins.experiments3',
]
