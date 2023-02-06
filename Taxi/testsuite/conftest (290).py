# root conftest for service eats-restapp-marketing
pytest_plugins = [
    'eats_restapp_marketing_plugins.pytest_plugins',
    'tests_eats_restapp_marketing.mock_services',
]
