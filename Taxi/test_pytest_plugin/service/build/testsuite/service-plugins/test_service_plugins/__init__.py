# pylint: skip-file
# flake8: noqa
from tests_plugins import inject_fixtures


inject_fixtures.inject_fixtures(
__name__, [
    # Local package fixtures
    '.pytest_conftest_plugin',
    '.secdist_conftest_plugin',
    'plugin1',
    'plugin2',
    'plugin3',
], package=__name__)
