import os

import pytest

pytest_plugins = [
    'tests.plugins.arc',
    'tests.plugins.bitbucket',
    'tests.plugins.commands',
    'tests.plugins.common',
    'tests.plugins.configs_admin',
    'tests.plugins.github',
    'tests.plugins.sandbox',
    'tests.plugins.staff',
    'tests.plugins.startrek',
    'tests.plugins.teamcity',
    'tests.plugins.telegram',
]

if os.getenv('ARCADIA_BUILD'):
    pytest_plugins.append('tests.plugins.arcadia')


def pytest_configure(config):
    config.addinivalue_line('markers', 'arc')


def pytest_collection_modifyitems(config, items):
    try:
        import yatest  # noqa
    except ImportError:
        for item in items:
            if 'arc' in item.keywords:
                item.add_marker(pytest.mark.skip())
    else:
        for item in items:
            if 'arc' not in item.keywords:
                item.add_marker(pytest.mark.skip())
