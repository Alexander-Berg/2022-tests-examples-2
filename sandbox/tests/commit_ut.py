# -*- coding: utf-8 -*-

import mock
import pytest
import os

from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.release_machine.helpers import svn_helper
from sandbox.projects.release_machine.helpers import commit


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (['trunk', 'arcadia', 'web', 'apphost'], 1),
        ([], -1),
        (['trunk'], -1),
        (['trunk', 'data'], 1),
        (['trunk', 'arcadia'], 1),
        (['trunk', 'arcadia_tests_data'], 1),
        (['tags', 'adfox'], -1),
        (['branches'], -1),
        (['branches', 'app_host', 'http_adapter', 'stable-12', 'arcadia'], 4),
        (['branches', 'app_host', 'http_adapter', 'stable-12', 'data'], 4),
        (['branches', 'app_host', 'http_adapter', 'stable-12'], -1)
    ]
)
def test_find_root_dir(input_data, expected):
    assert commit.find_root_dir(input_data) == expected


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (['arcadia', 'web', 'apphost'], 0),
        (['arcadia', 'web'], 3),
        ([], 5),
        (['data'], 4),
        (['arcadia'], 3),
        (['arcadia_tests_data'], 3),
    ]
)
def test__find_depth_to_checkout(input_data, expected):
    assert commit._find_depth_to_checkout(input_data) == expected


class MockArcadia(object):
    def __init__(self):
        self.checkouted_dirs = {}

    def checkout_func_mock(self, url, path, depth=None, revision=None, force=True):
        if path in self.checkouted_dirs:
            return
        self.checkouted_dirs[path] = {"depth": depth or "infinity", "revision": revision}

    def update_func_mock(self, path, revision=None, depth=None, set_depth=None):
        if path not in self.checkouted_dirs:
            self.checkouted_dirs[path] = {"depth": set_depth or "infinity", "revision": revision}
        if set_depth:
            self.checkouted_dirs[path]["depth"] = set_depth
        if revision:
            self.checkouted_dirs[path]["revision"] = revision

    def log_func_mock(self, url, revision_from=None, *args, **kwargs):
        log = {
            "arcadia:/arc/trunk@6842065": [
                {
                    "paths": [
                        ("A", "/trunk/arcadia/class_parser"),
                        ("A", "/trunk/arcadia/class_parser/class_parser.cpp"),
                        ("A", "/trunk/arcadia/class_parser/ya.make"),
                    ]
                },
            ],
            "arcadia:/arc/trunk@6037482": [
                {
                    "paths": [
                        ("M", "/trunk/arcadia/maps/config/ecstatic/testing/yandex-maps-perspoi-design.conf"),
                        ("M", "/trunk/arcadia/ya.make"),
                        ("M", "/trunk/arcadia/class_parser/ya.make"),
                    ]
                },
            ],
            "arcadia:/arc/trunk@6037483": [
                {
                    "paths": [
                        ("M", "/trunk/arcadia/maps/config/ecstatic/testing/yandex-maps-perspoi-design.conf"),
                        ("M", "/trunk/arcadia/ya.make"),
                        ("M", "/trunk/arcadia/class_parser/ya.make"),
                        ("M", "/trunk/arcadia_tests_data/nlp_test"),
                    ]
                },
            ],
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-12250@6037484": [
                {
                    "paths": [
                        ("M", "/branches/release_machine/release_machine_test/stable-12250/arcadia/maps/config"),
                        ("M", "/branches/release_machine/release_machine_test/stable-12250/arcadia/ya.make"),
                        (
                            "M",
                            "/branches/release_machine/release_machine_test/stable-12250/arcadia/class_parser/ya.make",
                        ),
                        (
                            "M",
                            "/branches/release_machine/release_machine_test/stable-12250/arcadia_tests_data/nlp_test",
                        ),
                    ]
                },
            ]
        }
        if revision_from:
            return log.get("{url}@{rev}".format(url=url, rev=revision_from)) or log.get(url)
        return log.get(url)

    def info_func_mock(self, url, *args, **kwargs):
        info = {
            "arcadia:/arc/trunk/arcadia/class_parser@6842065": {
                "entry_revision": 6842065,
                "entry_kind": "dir",
            },
            "local_branch_trunk": {
                "entry_revision": 6842065,
            },
            "local_branch_trunk/class_parser@6842065": {
                "entry_kind": "dir",
            },
            "local_branch_12240/arcadia": {
                "entry_revision": 6037482,
            },
            "arcadia:/arc/trunk/arcadia/ya.make@6037482": {
                "entry_revision": 6037482,
                "entry_kind": "file",
            },
            "local_branch_12240": {
                "entry_revision": 6037482,
            },
            "local_branch_12241/arcadia": {
                "entry_revision": 6037483,
            },
            "arcadia:/arc/trunk/arcadia/ya.make@6037483": {
                "entry_revision": 6037483,
                "entry_kind": "file",
            },
            "arcadia:/arc/trunk/arcadia_tests_data/nlp_test@6037483": {
                "entry_revision": 6037483,
                "entry_kind": "dir",
            },
            "local_branch_12241": {
                "entry_revision": 6037483,
            },
            "local_branch_12250/arcadia": {
                "entry_revision": 6037484,
            },
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-12250/arcadia/ya.make@6037484": {
                "entry_revision": 6037484,
                "entry_kind": "file",
            },
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-12250/arcadia_tests_data/nlp_test@6037484": {
                "entry_revision": 6037484,
                "entry_kind": "dir",
            },
            "local_branch_12250": {
                "entry_revision": 6037484,
            },
        }
        return info.get(url)

    def check_dirs_equality(self, true_checkouted_dirs):
        assert self.checkouted_dirs == true_checkouted_dirs


class MockOs(object):
    @classmethod
    def list_dir_mock_func(cls, path):
        dirs_for_paths = {
            "local_branch_trunk/class_parser": [],
            "local_branch_12240/maps": [],
            "local_branch_12240/class_parser": [],
            "local_branch_12240": ["maps", "class_parser"],
            "local_branch_12241": ["arcadia", "arcadia_tests_data"],
            "local_branch_12241/arcadia/maps": [],
            "local_branch_12241/arcadia/class_parser": [],
            "local_branch_12241/arcadia_tests_data/nlp_test": [],
            "local_branch_12250": ["arcadia", "arcadia_tests_data"],
            "local_branch_12250/arcadia/maps": [],
            "local_branch_12250/arcadia/class_parser": [],
            "local_branch_12250/arcadia_tests_data/nlp_test": [],
        }
        return dirs_for_paths[path]


@pytest.mark.parametrize(
    "merge_path, revs, common_path, expected",
    [
        (
            svn_helper.RollbackReleaseMachinePath(12250, rmc.COMPONENTS["release_machine_test"](), None),
            [6037484],
            [],
            {
                "local_branch_12250": {
                    "depth": "immediates",
                    "revision": 6037484,
                },
                "local_branch_12250/arcadia": {
                    "depth": "immediates",
                    "revision": 6037484,
                },
                "local_branch_12250/arcadia/maps": {
                    "depth": "infinity",
                    "revision": 6037484,
                },
                "local_branch_12250/arcadia/class_parser": {
                    "depth": "infinity",
                    "revision": 6037484,
                },
                "local_branch_12250/arcadia_tests_data/nlp_test": {
                    "depth": "infinity",
                    "revision": 6037484,
                },
                "local_branch_12250/arcadia_tests_data": {
                    "depth": "immediates",
                    "revision": 6037484,
                },
                "local_branch_12250/data": {
                    "depth": "immediates",
                    "revision": 6037484,
                },
            },
        ),
        (
            svn_helper.MergeReleaseMachinePath(12241, rmc.COMPONENTS["release_machine_test"](), None),
            [6037483],
            [],
            {
                "local_branch_12241": {
                    "depth": "immediates",
                    "revision": 6037483,
                },
                "local_branch_12241/arcadia": {
                    "depth": "immediates",
                    "revision": 6037483,
                },
                "local_branch_12241/arcadia/maps": {
                    "depth": "infinity",
                    "revision": 6037483,
                },
                "local_branch_12241/arcadia/class_parser": {
                    "depth": "infinity",
                    "revision": 6037483,
                },
                "local_branch_12241/arcadia_tests_data/nlp_test": {
                    "depth": "infinity",
                    "revision": 6037483,
                },
                "local_branch_12241/arcadia_tests_data": {
                    "depth": "immediates",
                    "revision": 6037483,
                },
                "local_branch_12241/data": {
                    "depth": "immediates",
                    "revision": 6037483,
                },
            },
        ),
        (
            svn_helper.MergeReleaseMachinePath(12240, rmc.COMPONENTS["release_machine_test"](), None),
            [6037482],
            ["arcadia"],
            {
                "local_branch_12240": {
                    "depth": "immediates",
                    "revision": 6037482,
                },
                "local_branch_12240/class_parser": {
                    "depth": "infinity",
                    "revision": 6037482,
                },
                "local_branch_12240/maps": {
                    "depth": "infinity",
                    "revision": 6037482,
                },
            },
        ),
        (
            svn_helper.RollbackTrunkPath(),
            [6842065],
            ["arcadia"],
            {
                "local_branch_trunk": {
                    "depth": "immediates",
                    "revision": 6842065,
                },
                "local_branch_trunk/class_parser": {
                    "depth": "infinity",
                    "revision": 6842065,
                },
            }
        ),
    ]
)
def test__try_partial_checkout(merge_path, revs, common_path, expected):
    from sandbox.sdk2.vcs import svn
    mock_arcadia = MockArcadia()
    with mock.patch.object(svn.Arcadia, "checkout", mock_arcadia.checkout_func_mock):
        with mock.patch.object(svn.Arcadia, "update", mock_arcadia.update_func_mock):
            with mock.patch.object(svn.Arcadia, "log", mock_arcadia.log_func_mock):
                with mock.patch.object(svn.Arcadia, "info", mock_arcadia.info_func_mock):
                    with mock.patch.object(os, "listdir", MockOs.list_dir_mock_func):
                        commit._try_partial_checkout(merge_path, revs, common_path)
                        mock_arcadia.check_dirs_equality(expected)
