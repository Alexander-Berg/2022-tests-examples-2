import io
import os
import pytest
import re
import time
from contextlib import redirect_stderr, redirect_stdout

from easytap import Tap

from pahtest.file import File, YmlFile
from pahtest.results import ActionResult

from .. import config
from . import utils
from .utils import check_with_yml


def plugins_list():
    # [:-4] is to strip ".yml" file extension from filename
    dir = 'tests/functional/assets/plugins/'
    return [file.name[:-4] for file in os.scandir(dir)]


# https://docs.pytest.org/en/latest/example/parametrize.html#different-options-for-test-ids
@pytest.mark.parametrize('plugin', plugins_list(), ids=lambda p: f'test_{p}_plugin')
@pytest.mark.plugin
def test_every_plugin(plugin: str):
    """
    Launch yaml sided plugin tests.

    You can launch separated test for a single plugin with it's id.
    See "Launch tests for plugin" docs section for details.
    """
    check_with_yml(
        plugin=plugin,
        tests=YmlFile(f'tests/functional/assets/plugins/{plugin}.yml')
    )


def get_tests_for_wait():
    dir_with_wait_files = 'tests/functional/assets/wait/'
    return list(os.scandir(dir_with_wait_files))


@pytest.mark.parametrize('file', get_tests_for_wait(),
                         ids=lambda file: 'test_wait_' + file.name[:-4])
def test_wait_carefully(file: os.DirEntry):
    """
    Launch yaml sided plugin tests.

    You can launch separated test for a single plugin with it's id.
    See "Launch tests for plugin" docs section for details.
    """
    check_with_yml(
        plugin='wait',
        tests=YmlFile(file.path)
    )


def test_result_check_pairs():
    """Result-check pairs should be consistent."""
    buffer = io.StringIO()
    tests = YmlFile('tests/functional/assets/plugins.yml')
    with redirect_stdout(buffer), redirect_stderr(buffer):
        try:
            check_with_yml(plugin='plugins', tests=tests)
        except RuntimeError as e:
            if not str(e) == 'Failed tests':
                raise e

    tap = Tap()
    value = buffer.getvalue()
    succeed = [
        'Inside plugin.',
        'After pah test.',
        'Short form with tap desc.',
        'Failed pah test.',
        'Desc hoisted from plugin.',
        'Passed check by description.',
        'Passed check by message.',
    ]
    failed = [
        'Failed check by description.',
        'Failed check by message.',
    ]
    for msg in succeed:
        tap.ok(bool(re.search('\n' + 'ok [0-9]+ - ' + msg, value)), msg)
    for msg in failed:
        tap.ok(bool(re.search('\n' + 'not ok [0-9]+ - ' + msg, value)), msg)
    tap()


def test_wrong_structure():
    utils.check_with_yml(YmlFile('tests/functional/assets/wrong_structure.yml'))


def test_get_ok_url():
    # - wrong base_url
    file = File(code={
        'options': {'selenium_hub_url': config.CHROME_HUB, 'base_url': ''},
        'tests': [{'get_ok': '/base.html'}]
    })
    results = file.run()
    result = results.list[1]
    assert isinstance(result, ActionResult)
    assert not result.success
    assert 'Check base_url option.' in result.message


def test_fill_ok_gap():
    """Fill_ok really has gap."""
    tests = YmlFile('tests/functional/assets/fill_ok_with_gap.yml')
    before = time.time()
    list(tests.loop())
    delta = time.time() - before
    assert delta > 0.4
