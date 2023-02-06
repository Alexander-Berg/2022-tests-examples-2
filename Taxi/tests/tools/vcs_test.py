import functools
import typing as tp

import mock
import pytest

import tools.vcs
from tools.vcs.base import VCSError, VCSWrapper


@pytest.mark.parametrize(
    "changed_files, expected, ignored",
    [
        (set(), set(), []),
        ({"tools/vcs.py"}, {"tools"}, []),
        ({"tox.ini"}, {"."}, []),
        ({""}, {"."}, []),
        ({"tools/vcs.py"}, {"tools"}, ["ignored"]),
        ({"tools/vcs.py", "ignored/foo.py"}, {"tools"}, ["ignored"]),
        (
            {"tools/vcs.py", "ignored/foo.py", "tools/inner/changed.py"},
            {"tools"},
            ["ignored"],
        ),
        (
            {"tools/vcs.py", "ignored/foo.py", "dmp_suite/inner/changed.py"},
            {"tools", "dmp_suite"},
            ["ignored"],
        ),
    ],
)
def test_get_changed_dirs(changed_files, expected, ignored):
    actual = set(tools.vcs.get_changed_dirs(changed_files, ignored))
    assert actual == expected


class ValidVcs(VCSWrapper):
    def __init__(self, name):
        self._name = name

    def merge_base(
        self,
        rev: tp.Text,
        source: tp.Optional[tp.Text] = None,
    ) -> tp.Text:
        return self._name

    def changed_files(
        self,
        rev: tp.Text,
        base: tp.Text,
        no_renames: bool = False,
    ) -> tp.List[tp.Text]:
        return []

    def revision(
        self,
        path: tp.Text,
    ) -> tp.Text:
        return self._name

    def healthcheck(self) -> None:
        return

    def current_changed_files(self, base: tp.Optional[tp.Text] = None) -> tp.List[tp.Text]:
        return []


class InvalidVcs(VCSWrapper):
    def __init__(self, name):
        self._name = name

    def merge_base(
        self,
        rev: tp.Text,
        source: tp.Optional[tp.Text] = None,
    ) -> tp.Text:
        return self._name

    def changed_files(
        self,
        rev: tp.Text,
        base: tp.Text,
        no_renames: bool = False,
    ) -> tp.List[tp.Text]:
        return []

    def revision(
        self,
        path: tp.Text,
    ) -> tp.Text:
        return self._name

    def healthcheck(self) -> None:
        raise VCSError()

    def current_changed_files(self, base: tp.Optional[tp.Text] = None) -> tp.List[tp.Text]:
        return []


def ensure_empty_lru_cache(cached_function):

    def decorator(f):

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            cached_function.cache_clear()
            f(*args, **kwargs)
            cached_function.cache_clear()

        return wrapper

    return decorator


@ensure_empty_lru_cache(tools.vcs.get_vcs)
@mock.patch('tools.vcs.AVAILABLE_VCS_LIST', [ValidVcs('valid'), InvalidVcs('invalid')])
def test_check_vcs_selection_valid_first():
    actual = tools.vcs.revision('some_path')
    assert actual == 'valid'


@ensure_empty_lru_cache(tools.vcs.get_vcs)
@mock.patch('tools.vcs.AVAILABLE_VCS_LIST', [InvalidVcs('invalid'), ValidVcs('valid')])
def test_check_vcs_selection_invalid_first():
    actual = tools.vcs.revision('some_path')
    assert actual == 'valid'


@ensure_empty_lru_cache(tools.vcs.get_vcs)
@mock.patch('tools.vcs.AVAILABLE_VCS_LIST', [InvalidVcs('invalid')])
def test_check_vcs_selection_invalid_only():
    with pytest.raises(tools.vcs.VCSError):
        tools.vcs.revision('some_path')


@ensure_empty_lru_cache(tools.vcs.get_vcs)
@mock.patch('tools.vcs.AVAILABLE_VCS_LIST', [InvalidVcs('invalid1'), InvalidVcs('invalid2')])
def test_check_vcs_selection_several_invalid():
    with pytest.raises(tools.vcs.VCSError):
        tools.vcs.revision('some_path')


@ensure_empty_lru_cache(tools.vcs.get_vcs)
@mock.patch('tools.vcs.AVAILABLE_VCS_LIST', [ValidVcs('valid1'), ValidVcs('valid2')])
def test_check_vcs_selection_first_valid_is_selected():
    actual = tools.vcs.revision('some_path')
    assert actual == 'valid1'
