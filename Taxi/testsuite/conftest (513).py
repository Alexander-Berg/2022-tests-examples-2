# root conftest for service order-takeout
pytest_plugins = [
    'order_takeout_plugins.pytest_plugins',
    'tests_order_takeout.mocks.order_archive',
    'tests_order_takeout.mocks.order_core',
]
