import pytest

from pahtest.file import YmlFile
from . import utils


def test_selenium_launch(tap):
    tests = YmlFile('tests/functional/assets/selenium.yml')
    results = tests.loop()
    next(results)  # it's plan
    tap.ok(
        next(results).success,
        'Load browser page front test launched ok.'
    )


def test_skip():
    out = utils.check_with_yml(YmlFile('tests/functional/assets/skip/options_true.yml'))
    assert 'Fail if the whole case is not skipped' not in out
    out = utils.check_with_yml(YmlFile('tests/functional/assets/skip/options_false.yml'))
    assert 'Pass since test is not skipped' in out
    out = utils.check_with_yml(YmlFile('tests/functional/assets/skip/root_true.yml'))
    assert 'Fail if the whole case is not skipped' not in out
    out = utils.check_with_yml(YmlFile('tests/functional/assets/skip/root_false.yml'))
    assert 'Pass since test is not skipped' in out


def test_import_keyword():
    utils.check_with_yml(YmlFile('tests/functional/assets/import/base.yml'))


def test_corrupted():
    results = YmlFile('tests/functional/assets/corrupted/wrong_yml.yml').run()
    # - only Plan and Note with "not ok"
    from pahtest.results import Note, PlanResult
    assert 2 == len(results.list), results
    assert isinstance(results.list[0], PlanResult)
    assert isinstance(results.list[1], Note)
    # - assert Note provides clear ext
    assert 'parsing yaml' == results.list[1].description
    assert 'YAML file is corrupted.' in results.list[1].message
