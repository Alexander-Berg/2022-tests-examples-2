import quality_control.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = [
    'quality_control.generated.service.pytest_plugins',
    'test_quality_control.plugins',
]
