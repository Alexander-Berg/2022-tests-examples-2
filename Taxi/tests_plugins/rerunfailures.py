import logging
import os
import re

from _pytest import main
from _pytest import runner
import requests


FLAP_LIST_URL = 'https://s3.mds.yandex.net/common/flap_tests'


logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    group = parser.getgroup(
        'rerunfailures', 're-run failing tests to eliminate flaky failures',
    )
    group.addoption(
        '--reruns',
        action='store',
        dest='reruns',
        type=int,
        default=0,
        help='number of times to re-run failed tests. defaults to 0.',
    )
    group.addoption(
        '--skip-flaps',
        action='store_true',
        dest='skip_flaps',
        help='ignore failures of tests witch marked as \'flapping\' onto S3',
    )


def pytest_configure(config):
    if config.option.reruns:
        config.pluginmanager.register(Session())


class Session:
    def __init__(self):
        self.failures = 0
        self.flaps_tests = set()

    def pytest_collectreport(self, report):
        if not report.passed:
            self.failures += 1

    def pytest_runtest_logreport(self, report):
        if (
                report.failed
                and not hasattr(report, 'wasxfail')
                and not hasattr(report, 'ignore_fail')
        ):
            self.failures += 1

    def pytest_runtest_protocol(self, item, nextitem):
        reruns = item.session.config.option.reruns
        full_test_name = _get_full_test_name(item)
        if (
                not reruns
                or item.get_marker('xfail') is not None
                or item.get_marker('skipif')
                or item.get_marker('skip')
                or item.get_marker('norerun')
        ):
            # Plugin not used
            return

        for num in range(reruns + 1):
            # Run test
            item.ihook.pytest_runtest_logstart(
                nodeid=item.nodeid, location=item.location,
            )
            reports = runner.runtestprotocol(
                item, nextitem=nextitem, log=False,
            )
            # setup, call, teardown
            if all(report.passed for report in reports):
                for report in reports:
                    report.sections = []
                    item.ihook.pytest_runtest_logreport(report=report)
                return True
            ignore_fail = full_test_name in self.flaps_tests or num < reruns
            for report in reports:
                if ignore_fail:
                    # mark failed test as ignored
                    report.ignore_fail = True
                item.ihook.pytest_runtest_logreport(report=report)
            if full_test_name in self.flaps_tests:
                return True

        # Test not passed
        self.failures += 1
        return True

    def pytest_sessionstart(self, session):
        if session.config.option.skip_flaps:
            self.flaps_tests = _get_flaps_tests()

    def pytest_sessionfinish(self, session):
        if session.exitstatus == main.EXIT_TESTSFAILED and self.failures == 0:
            session.exitstatus = main.EXIT_OK


def _get_flaps_tests():
    flaps = set()
    try:
        response = requests.get(
            FLAP_LIST_URL, headers={'Accept': 'application/json'},
        )
        response.raise_for_status()
        flaps = set(response.json())
    except Exception as exc:
        logger.warning(
            'Failed to get flapping tests from S3 with error: %s', exc,
        )
    return flaps


def _get_full_test_name(item):
    filename = item.location[0]
    testname = item.location[2]

    filename = re.sub(r'\.pyc?$', '', filename)
    filename = filename.replace(os.sep, '.').replace('/', '.')

    testname = testname.split('[', 1)[0]

    return '.'.join((filename, testname))
