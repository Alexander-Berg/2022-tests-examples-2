import collections
import logging

from sandbox.projects.common.testenv_client import TEClient
from sandbox.projects.yabs.qa.brave_tests.common import TESTENV_TEST_NAMES, TestType


# https://yql.yandex-team.ru/Operations/YqIAbdJwbPy3vJBr5cmKqjY0xF0tTRc_15JAaBv_tKM=
COMMITS_TO_ARCADIA_PER_DAY = 5000
TE_DATABASE = 'yabs-2.0'


logger = logging.getLogger(__name__)


def get_green_revision_from_trunk(max_revision, test_type=TestType.FT):
    tests_to_pass = TESTENV_TEST_NAMES[test_type.value].values()
    tasks_on_revision = collections.defaultdict(dict)

    oldest_revision = max_revision - COMMITS_TO_ARCADIA_PER_DAY * 7
    for test_name in tests_to_pass:
        ok_tasks = TEClient.get_ok_test_tasks(TE_DATABASE, test_name, oldest_revision)

        for task in ok_tasks:
            # If task's attribute "new_resource_id" is not empty - this task is resource update task.
            # It means that there exists another task on that revision, which is prefered
            if (not max_revision or task["revision"] <= max_revision) and not task.get("new_resource_id"):
                tasks_on_revision[task["revision"]][test_name] = task["task_id"]
    logger.debug("tasks_on_revision: %s", tasks_on_revision)

    revisions_with_all_passed_tests = set()
    for revision, tests in tasks_on_revision.items():
        if len(tests) == len(tests_to_pass):
            revisions_with_all_passed_tests.add(revision)
    logger.debug("revisions_with_all_passed_tests: %s", revisions_with_all_passed_tests)

    green_revision = max(revisions_with_all_passed_tests)
    return green_revision, tasks_on_revision[green_revision]
