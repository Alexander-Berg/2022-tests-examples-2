pytest_plugins = [
    'taxi_xdist.plugin',
    'eats_tests.plugins.catalog',
    'eats_tests.plugins.catalog_storage',
    'eats_tests.plugins.eats_cart',
    'eats_tests.plugins.picker',
    'eats_tests.plugins.core',
    'eats_tests.plugins.launch',
    'eats_tests.plugins.mysql',
    'eats_tests.plugins.payments',
    'eats_tests.plugins.stq',
    'eats_tests.plugins.cargo_claims',
    'eats_tests.plugins.list_payment_methods',
]
