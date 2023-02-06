import vgw_api_tasks.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = [
    'vgw_api_tasks.generated.service.pytest_plugins',
    'test_vgw_api_tasks.plugins',
]
