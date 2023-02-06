from sandbox.projects.yabs.qa.brave_tests.precommit_checks import get_green_revision_from_precommit_checks
from sandbox.projects.yabs.qa.brave_tests.trunk import get_green_revision_from_trunk


def get_base_revision(test_type, sandbox_client, max_revision):
    trunk_base_revision, trunk_tasks = get_green_revision_from_trunk(max_revision, test_type)

    precommit_base_revision, precommit_tasks = get_green_revision_from_precommit_checks(sandbox_client, test_type, max_revision)

    if precommit_base_revision and precommit_base_revision > trunk_base_revision:
        return precommit_base_revision, precommit_tasks

    return trunk_base_revision, trunk_tasks
