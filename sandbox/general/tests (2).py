import logging
import time
from collections import namedtuple
from dateutil import parser

from sandbox.sdk2.vcs.svn import Arcadia
from sandbox.projects.common.testenv_client import TEClient


logger = logging.getLogger(__name__)
TestMonitoringResult = namedtuple("TestMonitoringResult", ("test_name", "is_on", "timestamp"))


def get_tests(database):
    jobs = TEClient.get_all_jobs(db=database)
    return {test['name']: test['is_on'] for test in jobs}


def get_test_last_succeeded_rev(database, test_names):
    sandbox_tasks = TEClient.get_last_sandbox_task_ids(database, test_names, success=True)
    return {sandbox_task['job_name']: sandbox_task['revision'] for sandbox_task in sandbox_tasks}


def get_test_last_checked_rev(database, test_name):
    intervals = TEClient.get_checked_intervals_chunk(database, test_name)
    return max(interval['revision'] for interval in intervals if interval['is_checked'] is True) if intervals else None


def get_rev_timestamp(rev):
    arc_url = Arcadia.trunk_url(revision=rev)
    commit_date = Arcadia.info(arc_url)['date']
    commit_dt = parser.parse(commit_date).replace(tzinfo=None)
    return time.mktime(commit_dt.timetuple())


def get_tests_sensors(database):
    current_timestamp = time.time()
    tests = get_tests(database=database)
    sensors_data = []

    last_succeeded_revs = get_test_last_succeeded_rev(database=database, test_names=tests.keys())
    for test_name, revision in last_succeeded_revs.items():
        sensors_data.append({
            'labels': {
                'sensor': 'last_succeeded_check',
                'test_name': test_name,
                'is_on': tests[test_name],
            },
            'ts': current_timestamp,
            'value': current_timestamp - get_rev_timestamp(revision),
        })
    for test_name, is_on in tests.items():
        last_checked_rev = get_test_last_checked_rev(database=database, test_name=test_name)
        if last_checked_rev:
            sensors_data.append({
                'labels': {
                    'sensor': 'test_delay_sec',
                    'test_name': test_name,
                    'is_on': is_on,
                },
                'ts': current_timestamp,
                'value': current_timestamp - get_rev_timestamp(last_checked_rev),
            })

    return sensors_data
