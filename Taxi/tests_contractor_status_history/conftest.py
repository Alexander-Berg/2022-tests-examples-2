# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from contractor_status_history_plugins import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'fail_s3mds: s3 mds always fails with code and message specified ',
    )
