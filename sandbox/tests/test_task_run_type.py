import pytest

from sandbox.projects.yabs.qa.utils.task_run_type import (
    get_task_run_type,
    get_task_run_type_group,
    get_task_testenv_database,
    RunType,
    RunTypeGroup,
    SANDBOX_TASK_TAGS,
)


@pytest.mark.parametrize(('tags', 'run_type'), [
    ([], None),
    (['TAG'], None),
    (['TAG', SANDBOX_TASK_TAGS['oneshot_test']], RunType.ONESHOT_TEST),
    ([SANDBOX_TASK_TAGS['oneshot_test']], RunType.ONESHOT_TEST),
    ([SANDBOX_TASK_TAGS['content_system_settings_change_test']], RunType.CONTENT_SYSTEM_SETTINGS_CHANGE_TEST),
    ([SANDBOX_TASK_TAGS['create_oneshot_spec']], RunType.CREATE_ONESHOT_SPEC),
    ([SANDBOX_TASK_TAGS['precommit_check']], RunType.PRECOMMIT_CHECK),
    ([SANDBOX_TASK_TAGS['commit_check']], RunType.COMMIT_CHECK),
    ([SANDBOX_TASK_TAGS['precommit_check'], SANDBOX_TASK_TAGS['commit_check']], None),
])
def test_get_task_run_type(tags, run_type):
    assert get_task_run_type(tags) == run_type


@pytest.mark.parametrize(('tags', 'run_type_group'), [
    ([], None),
    (['TAG'], None),
    (['TAG', 'ONESHOT-TEST'], RunTypeGroup.ONESHOT),
    ([SANDBOX_TASK_TAGS['oneshot_test']], RunTypeGroup.ONESHOT),
    ([SANDBOX_TASK_TAGS['content_system_settings_change_test']], RunTypeGroup.ONESHOT),
    ([SANDBOX_TASK_TAGS['create_oneshot_spec']], RunTypeGroup.ONESHOT),
    ([SANDBOX_TASK_TAGS['precommit_check']], RunTypeGroup.TRUNK),
    ([SANDBOX_TASK_TAGS['commit_check']], RunTypeGroup.TRUNK),
    ([SANDBOX_TASK_TAGS['precommit_check'], SANDBOX_TASK_TAGS['commit_check']], None),
])
def test_get_task_run_type_group(tags, run_type_group):
    assert get_task_run_type_group(tags) == run_type_group


@pytest.mark.parametrize(('tags', 'database'), [
    (['TESTENV-DATABASE-YABS-2.0'], 'yabs-2.0'),
    (['TESTENV-DATABASE-YABS-2.0', 'TESTENV-COMMIT-CHECK'], 'yabs-2.0'),
    (['TESTENV-DATABASE'], None),
])
def test_get_task_testenv_database(tags, database):
    assert get_task_testenv_database(tags) == database
