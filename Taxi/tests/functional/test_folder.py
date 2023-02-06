import os
import time
from datetime import timedelta

import pytest

from pahtest import typing as t
from pahtest import case
from pahtest.file import YmlFile
from pahtest.folder import Folder
from pahtest.results import Note, PlanResult, TapResult, TestResult

from .utils import create_folder


@pytest.fixture
def folder() -> Folder:
    return create_folder(
        path='tests/functional/assets/nested/', cli_options={}
    )


@pytest.fixture
def folder_plain() -> Folder:
    return create_folder(
        path='tests/functional/assets/plain/', cli_options={}
    )


def filter_by(
    container: t.Iterable, by_field: str = '', field_value: t.Any = None,
    type_: t.TypeVar = None
) -> t.List[TapResult]:
    return [
        r for r in container if (
            (not by_field or getattr(r, by_field, None) == field_value)
            and (not type_ or type(r) == type_)
        )
    ]


def test_folder_plan_result(folder):
    rr = list(folder.loop())
    # - has some plan results
    assert filter_by(rr, type_=PlanResult)
    # - but has no plan result for the root folder
    assert not filter_by(
        rr, by_field='test', field_value=folder, type_=PlanResult
    )
    # - root children has plan results
    for sub in folder.subtests:
        assert filter_by(
            rr, by_field='test', field_value=sub, type_=PlanResult
        ), rr


def test_async_with_folder():
    jobs = 4
    factor = 1.0
    dir_ = 'tests/functional/assets/async'
    nfile = len(list(os.scandir(dir_)))
    file = YmlFile(path=f'{dir_}/first.yaml')
    folder = Folder(
        path=dir_,
        cli_options={
            'screenshots': {'before': 'none', 'after': 'none'},
            'jobs': jobs,
        }
    )
    before = time.time()
    list(file.loop())
    file_delta = time.time() - before
    before = time.time()
    folder.run_and_print()
    folder_delta = time.time() - before
    # the folder contains four files, each of them sleeps for 1 sec
    assert folder_delta < nfile * (file_delta * factor)
    print(
        f'file took {timedelta(seconds=file_delta)}.\n'
        f'async: {jobs} processes for {nfile} files'
        f' took {timedelta(seconds=folder_delta)}'
    )


def test_folder_tap_line(folder):
    def results(test):
        return filter_by(
            rr, by_field='test', field_value=test, type_=TestResult
        )
    rr = list(folder.loop())
    # - folder with depth=-1 has no tap line (status+desc)
    r = results(folder)[0]
    assert r.description
    assert folder.path not in r.as_tap()
    # - check tap lines for non-root levels of the tree
    for sub in folder.subtests:
        if isinstance(sub, Folder):
            filtered = results(sub)
            assert len(filtered) == 1
            # - second tree level folders has no tap line
            assert not filtered[0].as_tap(), filtered[0].as_tap()
        for ssub in sub.subtests:
            if isinstance(ssub, Folder):
                filtered = results(ssub)
                assert len(filtered) == 1
                # - third tree level folders has tap line
                assert ssub.path in filtered[0].as_tap()


def test_folder_indent(folder):
    def results(test):
        return filter_by(
            rr, by_field='test', field_value=test, type_=PlanResult
        )
    rr = list(folder.loop())
    indent = '  '
    for sub in folder.subtests:
        r = results(sub)[0]
        # - tap plan for folder with depth=0 has no indents
        assert not r.as_tap().startswith(indent)
        for ssub in sub.subtests:
            if isinstance(ssub, Folder):
                r = results(ssub)[0]
                # - tap plan for folder with depth=1 has one indent
                assert r.as_tap().startswith(indent)


def test_print_options():
    """
    Folder on tests run should print
    the first options variant for the first file in the folder tests set.
    """
    folder = create_folder(
        path='tests/functional/assets/print_options.yml',
        cli_options={'print_options': True}
    )
    results = list(folder.loop())
    note = next((r for r in results if (
        isinstance(r, Note) and r.message.startswith('-- Options --\n')
    )), None)
    # - has the record with options
    assert note, note
    # - contains the main yaml records
    assert 'base_url: http://nginx' in note.message, note.message
    # - contains the first record from the list
    assert 'first: 1' in note.message, note.message
    # - does not contain the second record from the list
    assert 'second: 2' not in note.message, note.message


def test_print_options_cli_flag():
    """Folder does not print options with no flag."""
    folder = create_folder(
        path='tests/functional/assets/print_options.yml',
        cli_options={}
    )
    results = list(folder.loop())
    note = next((r for r in results if (
        isinstance(r, Note) and r.message.startswith('-- Options --\n')
    )), None)
    # - has no the record with options
    assert note is None, note


def test_maximize_cli_flag():
    """CLI option --maximize redefines the same one at the yml options."""
    # Redefines
    folder = create_folder(
        path='tests/functional/assets/maximize_cli_flag.yml',
        cli_options={'maximize': True}
    )
    browsers = [case.browser for file in folder.subtests for case in file.subtests]
    assert all([b.maximize for b in browsers])

    # Not redefines
    folder = create_folder(
        path='tests/functional/assets/maximize_cli_flag.yml',
        cli_options={'maximize': False}
    )
    browsers = [case.browser for file in folder.subtests for case in file.subtests]
    assert not any([b.maximize for b in browsers])


def test_devtools_cli_flag():
    """CLI option --devtools redefines the same one at the yml options."""
    # Redefines
    folder = create_folder(
        path='tests/functional/assets/devtools_cli_flag.yml',
        cli_options={'devtools': True}
    )
    browsers = [case.browser for file in folder.subtests for case in file.subtests]
    assert all([b.devtools for b in browsers])

    # Not redefines
    folder = create_folder(
        path='tests/functional/assets/devtools_cli_flag.yml',
        cli_options={'devtools': False}
    )
    browsers = [case.browser for file in folder.subtests for case in file.subtests]
    assert not any([b.devtools for b in browsers])


def test_passed_count_plain():
    """Plain loop prints passed count."""
    total = 4
    failed = 0
    folder = create_folder(path='tests/functional/assets/plain/')
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('PASSED') == total, messages
    for i in range(1, total+1):
        assert f'PASSED/FAILED/TOTAL {i}/{failed}/{total}' in messages


def test_passed_count_parallel():
    """Plain loop prints passed count."""
    total = 4
    failed = 0
    folder = create_folder(
        path='tests/functional/assets/plain/',
        cli_options=dict(jobs=2)
    )
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('PASSED') == total, messages
    for i in range(1, total+1):
        assert f'PASSED/FAILED/TOTAL {i}/{failed}/{total}' in messages


def test_total_parallel_nested():
    """Parallel loop with nested folders prints total count."""
    total = 4
    failed = 0
    folder = create_folder(
        path = 'tests/functional/assets/nested_simple',
        cli_options=dict(jobs=2)
    )
    folder.run_and_print()
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('PASSED') == total, messages
    for i in range(1, total+1):
        assert f'PASSED/FAILED/TOTAL {i}/{failed}/{total}' in messages


@pytest.mark.skip
def test_failed_count_plain_zero():
    """Plain loop with every test passed prints zero errors."""
    total = 4
    folder = create_folder(path='tests/functional/assets/plain/')
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('FAILED') == 4, messages
    assert messages.count('FAILED 0') == total, messages


@pytest.mark.skip
def test_failed_count_parallel_zero():
    """Plain loop with every test passed prints zero errors."""
    total = 4
    folder = create_folder(
        path='tests/functional/assets/plain/',
        cli_options=dict(jobs=2)
    )
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('FAILED') == 4, messages
    assert messages.count('FAILED 0') == total, messages


@pytest.mark.skip
def test_failed_count_plain_common():
    """Plain loop with every test passed prints zero errors."""
    total = 4
    folder = create_folder(path='tests/functional/assets/plain_failed/')
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('FAILED') == 4, messages
    for i in range(1, total+1):
        assert f'FAILED {i}' in messages


@pytest.mark.skip
def test_failed_count_parallel_common():
    """Plain loop with every test passed prints zero errors."""
    total = 4
    folder = create_folder(
        path='tests/functional/assets/plain_failed/',
        cli_options=dict(jobs=2)
    )
    results = list(folder.loop())
    messages = '|'.join([r.message for r in results])
    assert messages.count('FAILED') == 4, messages
    for i in range(1, total+1):
        assert f'FAILED {i}' in messages


def test_procs_done_log():
    # - "done * of <total>" for two procs with four tests
    jobs = 2
    folder = create_folder(
        path='tests/functional/assets/plain/',
        cli_options=dict(jobs=jobs)
    )
    tap = folder.run_to_str()
    for i in range(1, jobs + 1):
        assert f'Procs done {i}/{jobs}' in tap, tap
    # - no "Procs done" for one proc
    jobs = 1
    folder = create_folder(
        path='tests/functional/assets/plain/',
        cli_options=dict(jobs=jobs)
    )
    tap = folder.run_to_str()
    assert 'Procs done' not in tap, tap


def test_logs_count_skipped_as_passed():
    """Skipped tests are counted well."""
    jobs = 2
    folder = create_folder(
        path='tests/functional/assets/with_skipped/',
        cli_options=dict(jobs=jobs)
    )
    tap = folder.run_to_str()
    assert case.SKIP_MESSAGE in tap, tap
    for i in range(1, jobs + 1):
        assert f'PASSED/FAILED/TOTAL {i}/0/4' in tap, tap
