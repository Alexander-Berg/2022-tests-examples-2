import os

from pahtest.action import BaseAction
from pahtest.case import Case
from pahtest.file import YmlFile
from pahtest.results import ActionResult

from .utils import check_with_yml, create_folder


def test_list():
    tests = YmlFile('tests/functional/assets/options/list.yml')
    results = tests.run()
    # pahtests set run once for every options instance
    assert len(results.list) == 10


def test_env():
    """Env vars with "env:" notation in yaml should work."""
    os.environ['SITE_URL'] = 'http://nginx'
    os.environ['SITE_WIDTH'] = '800'
    try:
        check_with_yml(YmlFile('tests/functional/assets/options/env.yml'))
    finally:
        os.environ.pop('SITE_URL')
        os.environ.pop('SITE_WIDTH')


def test_relative_url():
    check_with_yml(YmlFile('tests/functional/assets/options/url.yml'))


def test_type_casting():
    check_with_yml(YmlFile('tests/functional/assets/options/types.yml'))


def test_get_params():
    check_with_yml(YmlFile('tests/functional/assets/options/get_params.yml'))


def test_strict_mode_option():
    """The option goes down to the bottom of the test tree."""
    folder = create_folder(
        path='tests/functional/assets/nested/',
        cli_options={'strict_mode_file': True}
    )
    for file in folder.subtests:
        for case in file.subtests:
            if isinstance(case, Case):
                assert case.actions.strict_mode, case


def test_strict_mode_file_failed_stops():
    """Tests with enabled strict_mode_file option should stop after first failure."""
    tests = YmlFile(
        'tests/functional/assets/options/strict_mode_file/fail.yml',
        cli_options={'strict_mode_file': True}
    )
    action_tests = [
        t for t in tests.subtests[0].actions.subtests if isinstance(t, BaseAction)
    ]
    action_results = [r for r in tests.loop() if isinstance(r, ActionResult)]
    acts = len(action_tests)
    ress = len(action_results)
    # not all the tests was really launched
    assert acts > ress, f'Actions: {acts}, Results: {ress}'
    # the last result is the failed one
    assert action_results[-1].test.func_name == 'hasnt'


def test_strict_mode_file_succeed_goes():
    """Succeed tests with enabled strict_mode_file option should run all over the set."""
    tests = YmlFile(
        'tests/functional/assets/options/strict_mode_file/success.yml',
        cli_options={'strict_mode_file': True}
    )
    action_tests = [
        t for t in tests.subtests[0].actions.subtests if isinstance(t, BaseAction)
    ]
    action_results = [r for r in tests.loop() if isinstance(r, ActionResult)]
    acts = len(action_tests)
    ress = len(action_results)
    # all the tests was really launched
    assert acts == ress, f'Actions: {acts}, Results: {ress}'
    # the last result is the last one in a file
    assert action_results[-1].test.func_name == 'has'


def test_strict_mode_file_wait_failed_stops():
    """Failed test inside wait plugin stops file execution on the test."""
    tests = YmlFile(
        'tests/functional/assets/options/strict_mode_file/wait_failed.yml',
        cli_options={'strict_mode_file': True}
    )
    action_results = [r for r in tests.loop() if isinstance(r, ActionResult)]
    # the last result is related to the failed wait test
    assert action_results[-1].test.func_name == 'wait'


def test_strict_mode_file_wait_leading_failed_stops():
    """Wait is not launched after failed test in the strict file mode."""
    tests = YmlFile(
        'tests/functional/assets/options/strict_mode_file/wait_leading_failed.yml',
        cli_options={'strict_mode_file': True}
    )
    action_results = [r for r in tests.loop() if isinstance(r, ActionResult)]
    # the last result is related to the failed wait test
    assert action_results[-1].test.func_name == 'has'
