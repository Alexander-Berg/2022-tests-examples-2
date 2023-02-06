import replication.generated.service.pytest_init  # noqa:F401

pytest_plugins = [
    'replication.generated.service.pytest_plugins',
    'replication.common.pytest.replication_entry_point_plugin',
]
