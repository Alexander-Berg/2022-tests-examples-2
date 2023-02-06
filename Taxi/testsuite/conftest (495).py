# root conftest for service merchant-profiles
pytest_plugins = [
    'merchant_profiles_plugins.pytest_plugins',
    'tests_merchant_profiles.mocks.fleet_parks',
    'tests_merchant_profiles.mocks.parks_replica',
]
