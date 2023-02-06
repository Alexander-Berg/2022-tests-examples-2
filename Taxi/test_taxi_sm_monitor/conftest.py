import taxi_sm_monitor.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = [
    'taxi.pytest_plugins.stq_agent',
    'taxi_sm_monitor.generated.service.pytest_plugins',
    'test_taxi_sm_monitor.plugins',
]
