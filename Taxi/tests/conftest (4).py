import os
import sys

import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT_DIR, 'submodules', 'dashboards'))

pytest_plugins = [
    'tests.plugins.common',
    'tests.plugins.plugin_manager',
    'tests.plugins.ref_comparer',
]


@pytest.fixture
def base_service():
    return {
        'debian': {
            'maintainer_name': 'Sergey Pomazanov',
            'maintainer_login': 'alberist',
            'source_package_name': 'test-package-name-source',
            'description': 'Test service description',
            'binary_package_name': 'test-package-name',
        },
    }
