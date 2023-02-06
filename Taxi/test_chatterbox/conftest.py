import chatterbox.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'taxi.pytest_plugins.stq_agent',
    'chatterbox.generated.service.pytest_plugins',
    'test_chatterbox.plugins',
]
