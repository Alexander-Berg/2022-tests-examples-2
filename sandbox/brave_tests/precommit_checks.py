import collections
import datetime
import logging

from sandbox.projects.yabs.qa.brave_tests.common import TESTENV_TEST_NAMES, TestType


logger = logging.getLogger(__name__)


def get_svn_revision_from_server_resource(task, sandbox_client):
    try:
        server_resource_id = task["input_parameters"]["meta_server_resource"]
    except KeyError as e:
        logger.error("Failed to get 'meta_server_resource' parameter from task %s: %s", task, e)

    return int(sandbox_client.resource[server_resource_id].read()["attributes"]["svn_revision"])


def get_precommit_tasks(test_name, sandbox_client):
    now = datetime.datetime.now()
    created_from = (now - datetime.timedelta(hours=24)).isoformat()
    created_to = now.isoformat()

    tags = [
        "TESTENV-PRECOMMIT-CHECK",
        "TESTENV-JOB-{}".format(test_name),
        "WITHOUT-PATCH"
    ]
    params = {
        "type": "YABS_SERVER_B2B_FUNC_SHOOT_2",
        "status": "SUCCESS",
        "tags": tags,
        "all_tags": True,
        "author": "robot-testenv",
        "created": "{}..{}".format(created_from, created_to),
        "hidden": True,
    }

    limit = 100
    offset = 0
    precommit_tasks = []
    while True:
        response = sandbox_client.task.read(limit=limit, offset=offset, **params)
        precommit_tasks += response["items"]
        logger.debug("Precommit tasks: %s", {"total": response["total"], "recieved": len(precommit_tasks)})
        if len(response["items"]) < limit or len(precommit_tasks) == response["total"]:
            break
        offset += limit

    return precommit_tasks


def get_green_revision_from_precommit_checks(sandbox_client, test_type=TestType.FT, max_revision=None):
    tasks_on_revision = collections.defaultdict(dict)
    tests_to_pass = TESTENV_TEST_NAMES[test_type.value].values()

    for test_name in tests_to_pass:
        tasks = get_precommit_tasks(test_name, sandbox_client)
        if not tasks:
            logger.warning("No tasks found for test %s", test_name)
            return 0, {}

        for task in tasks:
            svn_revision = get_svn_revision_from_server_resource(task, sandbox_client)

            if max_revision and svn_revision > max_revision:
                logger.debug("Skip SVN revision: r%d is greater than max_revision r%d", svn_revision, max_revision)
                continue

            tasks_on_revision[svn_revision][test_name] = task["id"]
            te_base = task["hints"][0].lower()
            logger.debug({
                "test_name": test_name,
                "revision": svn_revision,
                "task_id": task["id"],
                "testenv_base": te_base,
            })

    logger.debug("tasks_on_revision: %s", tasks_on_revision)
    candidates = filter(
        lambda dict_item: len(dict_item[1]) == len(tests_to_pass),
        tasks_on_revision.items()
    )
    if not candidates:
        return 0, {}

    return max(candidates, key=lambda pair: pair[0])
