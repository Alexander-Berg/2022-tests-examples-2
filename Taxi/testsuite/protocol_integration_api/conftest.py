from tests_plugins import fastcgi

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # local mocks
    'tests_plugins.config_service_defaults',
    'tests_plugins.load_graph',
    'tests_plugins.mock_blackbox',
    'tests_plugins.mock_cardstorage',
    'tests_plugins.mock_driver_authorizer',
    'tests_plugins.mock_discounts',
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_feedback',
    'tests_plugins.mock_geofence',
    'tests_plugins.mock_geotracks',
    'tests_plugins.mock_mds',
    'tests_plugins.mock_order_core',
    'tests_plugins.mock_order_offers',
    'tests_plugins.mock_parks',
    'tests_plugins.mock_personal_phones',
    'tests_plugins.mock_reposition',
    'tests_plugins.mock_solomon',
    'tests_plugins.mock_stq',
    'tests_plugins.mock_tags',
    'tests_plugins.mock_driver_ratings',
    'tests_plugins.mock_territories',
    'tests_plugins.mock_cars_catalog',
    'tests_plugins.mock_tracker',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mock_user_api',
    'tests_plugins.mock_vgw_api',
    'tests_plugins.mock_ya_translate',
    'tests_plugins.mock_yamaps',
    'tests_plugins.mock_virtual_tariffs',
    'tests_plugins.mock_yt',
    'tests_plugins.mock_pricing_data_preparer',
    'tests_plugins.mock_geoareas',
    # local fixtures
    'protocol.order_test_utils',
    'common_fixtures',
    'protocol_integration_api.whitelabel_utils',
]

taxi_integration = fastcgi.create_client_fixture(
    'taxi_protocol_integration_api',
)
