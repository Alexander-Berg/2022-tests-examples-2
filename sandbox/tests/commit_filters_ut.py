# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
import pytest
import re

import sandbox.projects.release_machine.changelogs as ch


class ArcanumApiMock(object):
    def get_dashboard(self, params):
        return {
            "reviews": [{"id": 123}],
        }

    def get_review_request(self, review_id):
        return {
            "id": 123,
            "commits": [
                {
                    "committedAtRevision": 12345,
                }
            ],
            "bugsClosed": [
                {
                    "name": "RMDEV-1",
                    "link": "https://st.yandex-team.ru/RMDEV-1"
                },
                {
                    "name": "RMDEV-2",
                    "link": "https://st.yandex-team.ru/RMDEV-2"
                },
            ],
            "startrek_issues": ["RMDEV-1", "RMDEV-2"]
        }


class TEClientMock(object):
    @classmethod
    def get_te_problems(cls, te_db):
        return {
            "rows": [
                {
                    "test_diff/revision2": 1111,
                    "comment": "",
                    "resolve_comment": "",
                    "test_name": "",
                },
                {
                    "test_diff/revision2": 2222,
                    "comment": "disabled",
                    "resolve_comment": "",
                    "test_name": "",
                },
                {
                    "test_diff/revision2": 3333,
                    "comment": "diff is not stable:",
                    "resolve_comment": "",
                    "test_name": "",
                },
                {
                    "test_diff/revision2": 4444,
                    "comment": "valid comment",
                    "resolve_comment": "auto resolved: message",
                    "test_name": "",
                },
                {
                    "test_diff/revision2": 5555,
                    "comment": "valid comment",
                    "resolve_comment": "auto",
                    "test_name": "BASESEARCH_RESPONSES",
                },
            ],
        }


class TestCommitFilters(object):
    PATH_FILTER1 = ch.PathsFilter([
        (1, "arcadia/important/path1"),
        (1, "arcadia/important/path2"),
        (7, "arcadia/the/most/important/path"),
    ])
    PATH_FILTER2 = ch.PathsFilter([
        (1, "arcadia/important/path1"),
        (0, "arcadia/important/path1/not/important/subpath"),
        (7, "arcadia/fake/most/important/path"),
        (0, "arcadia/fake"),
    ])
    MARKER_FILTER = ch.MarkerFilter([
        (1, re.compile(r"\bimportant1 *: *qqq", re.IGNORECASE)),
        (2, re.compile(r"\bimportant2 *: *pp", re.IGNORECASE)),
    ])

    @pytest.mark.parametrize(
        "path_filter, vcs_info, expected_importance",
        [
            (
                PATH_FILTER1,
                {
                    "paths": [
                        ("A", "/trunk/arcadia/not/important/path1"),
                        ("A", "/trunk/arcadia/not/important/path2"),
                    ]
                },
                0,
            ),
            (
                PATH_FILTER1,
                {
                    "paths": [
                        ("A", "/trunk/arcadia/important/path1butnotreally"),
                    ]
                },
                0,
            ),
            (
                PATH_FILTER1,
                {
                    "paths": [("A", "/trunk/arcadia/important/path1")]
                },
                1,
            ),
            (
                PATH_FILTER1,
                {
                    "paths": [("A", "/trunk/arcadia/important/path2/file.txt")]
                },
                1,
            ),
            (
                PATH_FILTER1,
                {
                    "paths": [
                        ("M", "/trunk/arcadia/important/path1"),
                        ("A", "/trunk/arcadia/important/path2"),
                    ]
                },
                1,
            ),
            (
                PATH_FILTER1,
                {
                    "paths": [
                        ("M", "/trunk/arcadia/not/important/path1"),
                        ("M", "/trunk/arcadia/important/path1"),
                        ("A", "/trunk/arcadia/the/most/important/path/file"),
                    ]
                },
                7,
            ),
            (
                PATH_FILTER2,
                {
                    "paths": [
                        ("M", "/trunk/arcadia/important/path1/not/important/subpath/file1.txt"),
                        ("D", "/trunk/arcadia/important/path1/qq/file2.txt"),
                    ]
                },
                1,
            ),
            (
                PATH_FILTER2,
                {
                    "paths": [
                        ("M", "/trunk/arcadia/important/path1/qq/pp/file.txt"),
                        ("M", "/trunk/arcadia/important/path1/not/important/subpath/file.txt"),
                    ]
                },
                1,
            ),
            (
                PATH_FILTER2,
                {
                    "paths": [
                        ("M", "/trunk/arcadia/important/path1/not/important/subpath/file1.txt"),
                        ("D", "/trunk/arcadia/important/path1/not/important/subpath/q/file2.txt"),
                    ]
                },
                0,
            ),
            (
                PATH_FILTER2,
                {
                    "paths": [
                        ("M", "/trunk/arcadia/fake/most/important/path/file.txt"),
                    ]
                },
                0,
            ),
        ]
    )
    def test__paths_filter(self, path_filter, vcs_info, expected_importance):
        assert path_filter.get_importance(vcs_info) == expected_importance

    @pytest.mark.parametrize(
        "marker_filter, vcs_info, expected_importance",
        [
            (
                MARKER_FILTER,
                {"msg": "Not important msg"},
                0,
            ),
            (
                MARKER_FILTER,
                {"msg": "Fake important msg. (important1:qq)"},
                0,
            ),
            (
                MARKER_FILTER,
                {"msg": "Really important msg1. [important1:qqq]"},
                1,
            ),
            (
                MARKER_FILTER,
                {"msg": "Really important msg2. [important1: qqq]"},
                1,
            ),
            (
                MARKER_FILTER,
                {"msg": "Really important msg3. [important2: pp]"},
                2,
            ),
            (
                MARKER_FILTER,
                {"msg": "VERY important msg. [Important1 : qqq][important2: pp]"},
                3,
            ),
        ],
    )
    def test__marker_filter(self, marker_filter, vcs_info, expected_importance):
        assert marker_filter.get_importance(vcs_info) == expected_importance

    def test__review_filter(self):
        from sandbox.projects.release_machine.helpers.arcanum_helper import ArcanumApi
        api_mock = ArcanumApiMock()
        with mock.patch.object(ArcanumApi, "get_dashboard", api_mock.get_dashboard):
            with mock.patch.object(ArcanumApi, "get_review_request", api_mock.get_review_request):
                with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
                    review_filter = ch.ReviewFilter(["release_machine"], 1, 2)
                    assert review_filter.get_importance({"revision": 12345}) == 1
                    assert review_filter.get_patch({"revision": 12345}) == {
                        "reviews": {123: ["RMDEV-1", "RMDEV-2"]}
                    }
                    assert review_filter.get_importance({"revision": 9}) == 0
                    with pytest.raises(KeyError):
                        assert review_filter.get_patch({"revision": 9})

    def test__testenv_filter(self):
        from sandbox.projects.common.testenv_client import TEClient
        with mock.patch.object(TEClient, "get_te_problems", TEClientMock.get_te_problems):
            te_filter = ch.TestenvFilter(["db1", "db2"])
            assert te_filter.get_importance({"revision": 1234}) == 0
            assert te_filter.get_importance({"revision": 1111}) == 2
            assert te_filter.get_importance({"revision": 2222}) == 0
            assert te_filter.get_importance({"revision": 3333}) == 0
            assert te_filter.get_importance({"revision": 4444}) == 0
            assert te_filter.get_importance({"revision": 5555}) == 3
