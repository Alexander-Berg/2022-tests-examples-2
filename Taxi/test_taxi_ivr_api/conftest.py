import taxi_ivr_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'taxi_ivr_api.generated.service.pytest_plugins',
    'test_taxi_ivr_api.plugins',
]
