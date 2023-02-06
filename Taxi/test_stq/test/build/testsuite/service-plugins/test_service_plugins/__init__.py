# pylint: skip-file
# flake8: noqa
from tests_plugins import inject_fixtures


inject_fixtures.inject_fixtures(
__name__, [
    # Local package fixtures
    '.mock_stq_conftest_plugin',
    '.pytest_conftest_plugin',
    '.secdist_conftest_plugin',
    '.stq_worker_conftest_plugin',
], package=__name__)
