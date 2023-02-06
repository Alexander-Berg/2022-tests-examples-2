# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import collections
import json
import mock
import os
import pytest
import re

import sandbox.projects.release_machine.changelogs as ch


REVIEW_INFO = {
    "id": 1025728,
    "commits": [
        {
            "committedAtRevision": 5924666,
        }
    ],
    "bugsClosed": [
        {
            "name": "MAILDLV-2945",
            "link": "https://st.yandex-team.ru/MAILDLV-2945",
        },
    ],
    "startrek_issues": ["MAILDLV-2945"]
}


class ArcanumApiMock(object):
    def get_review_request(self, rr_id):
        return REVIEW_INFO


class CLTestenvFilterMock(ch.TestenvFilter):
    def __init__(self, testenv_dbs):
        self._revisions = collections.defaultdict(list)
        self._revisions[5924681] = [{
            "comment": "1",
            "resolve_comment": "",
            "test_name": "",
            "test_diff_id": 777777,
            "is_resolved": "no",
            "owner": "pupkin",
        }, {
            "comment": "2",
            "resolve_comment": "auto resolved:qqq",
            "test_name": "",
            "test_diff_id": 888888,
            "is_resolved": "yes",
            "owner": "qq",
        }]


class ReviewFilterMock(ch.ReviewFilter):
    def get_revisions(self):
        return {5924666: REVIEW_INFO}


def get_test_data():
    import yatest.common

    path1 = os.path.join(
        os.path.dirname(yatest.common.test_source_path()),
        'tests', 'changelog_master_ut_data.json',
    )
    path2 = os.path.join(
        os.path.dirname(yatest.common.test_source_path()),
        'tests', 'changelog_master_ut_data2.json',
    )

    with open(path1) as f1, open(path2) as f2:
        data1 = json.load(f1)["logentries"]
        data2 = json.load(f2)["logentries"]
    return data1, data2


class TestChangeLogMaster(object):
    def setup(self):
        vcs_indexer_response1, vcs_indexer_response2 = get_test_data()

        def vsc_indexer_interval_info(start_revision, end_revision, **kwargs):
            return {
                5924692: vcs_indexer_response1,
                5924663: vcs_indexer_response2,
            }[end_revision]

        self._vsc_indexer_interval_info = vsc_indexer_interval_info

    @pytest.mark.parametrize(
        "first_rev, prod_released_path, prod_released_revision, candidate_path, candidate_revision, filters, expected",
        [
            (
                5924660,
                "/tags/release_machine/release_machine_test/stable-7601-1", 5924663,
                "/tags/release_machine/release_machine_test/stable-7602-1", 5924692,
                [
                    ch.MarkerFilter([(5, re.compile("committed from Sandbox task"))]),
                    ch.PathsFilter([(1, "arcadia/search/wizard/data/fresh/report/gzt/src")]),
                ],
                [
                    ch.ChangeLogEntry(
                        {
                            "revision": 5924682,
                            "author": "zomb-sandbox-rw",
                            "msg": (
                                "Update resource by sandbox task #548450480\n"
                                "(committed from Sandbox task #548450480)\n\n"
                                "Note: mandatory review (NEED_REVIEW) was skipped\n"
                                "Note: mandatory check (NEED_CHECK) was skipped"
                            ),
                            "paths": [("A", "")],  # real paths not needed for this test
                            "added": True,
                            "date": "2022-07-23T17:05:10Z",
                        },
                        importance=5,
                        reasons={ch.Reasons.MARKER}
                    ),
                    ch.ChangeLogEntry(
                        {
                            "revision": 5924674,
                            "author": "zomb-sandbox-rw",
                            "msg": (
                                "UPDATE_TV_FAST_DATA update tv data with new id:1212256660\n"
                                "https://sandbox.yandex-team.ru/task/548465508/view "
                                "(committed from Sandbox task #548465508)"
                            ),
                            "paths": [("A", "")],  # real paths not needed for this test
                            "added": True,
                            "date": "2022-07-23T17:05:10Z",
                        },
                        importance=5,
                        reasons={ch.Reasons.MARKER}
                    ),
                    ch.ChangeLogEntry(
                        {
                            "revision": 5924667,
                            "author": "zomb-sandbox-rw",
                            "msg": (
                                "Auto update report/gzt/src/biathlon.data\n"
                                "Sandbox task id: 548445379\n"
                                "(committed from Sandbox task #548445379)\n\n"
                                "Note: mandatory check (NEED_CHECK) was skipped"
                            ),
                            "paths": [
                                ("M", "/trunk/arcadia/search/wizard/data/fresh/report/gzt/src/biathlon.data"),
                                ("M", "/trunk/arcadia/search/wizard/data/fresh/report/gzt/ya.make"),
                            ],
                            "added": True,
                            "date": "2022-07-23T17:05:10Z",
                        },
                        importance=6,
                        reasons={ch.Reasons.MARKER, ch.Reasons.PATHS}
                    ),
                ],
            ),
            (
                5924660,
                "/tags/release_machine/release_machine_test/stable-7601-1", 5924663,
                "/tags/release_machine/release_machine_test/stable-7602-1", 5924692,
                [
                    ReviewFilterMock(["mproto"], 5924660, 5924692),
                    CLTestenvFilterMock(["testenv_db"]),
                ],
                [
                    ch.ChangeLogEntry(
                        {
                            "revision": 5924681,
                            "author": "robot-vcssync",
                            "msg": (
                                "[32400af] Merge pull request #30141 from web4/SERP-95116\n\n"
                                "SERP-95116: Обновить тесты и протестировать функционально "
                                "Замена звезд на цифры в рейтинге маркета в рекламе на десктопе - EXPERIMENTS-37414\n\n"
                                "Originally committed Fri Nov 15 03:14:08 2019 +0300 by ilyhryh "
                                "\u003Cilyhryh@yandex-team.ru\u003E\n\nNote: mandatory check (NEED_CHECK) was skipped"
                            ),
                            "paths": [("A", "")],  # real paths not needed for this test
                            "date": "2022-07-23T17:05:10Z",
                        },
                        importance=2,
                        reasons={ch.Reasons.TESTENV},
                        patches=[{
                            "problem_owners": ["pupkin", "qq"],
                            "problems": {
                                "!!empty!!": {
                                    "te_diff_id": 777777,
                                    "resolved": False,
                                },
                                "auto resolved:qqq": {
                                    "te_diff_id": 888888,
                                    "resolved": True,
                                },
                            }
                        }]
                    ),
                    ch.ChangeLogEntry(
                        {
                            "revision": 5924666,
                            "author": "alexandr21",
                            "msg": "[MAILDLV-2945] Update types module, add task info\n\nREVIEW: 1025728",
                            "paths": [("A", "")],  # real paths not needed for this test
                            "added": True,
                            "date": "2022-07-23T17:05:10Z",
                        },
                        importance=1,
                        reasons={ch.Reasons.REVIEW},
                        patches=[{"reviews": {1025728: ["MAILDLV-2945"]}}]
                    ),
                ],
            )
        ]
    )
    def test__get_changelog(
        self,
        first_rev,
        prod_released_path, prod_released_revision,
        candidate_path, candidate_revision,
        filters,
        expected,
    ):
        master = ch.ChangeLogMaster(
            first_rev,
            prod_released_path, prod_released_revision,
            candidate_path, candidate_revision,
            filters,
        )
        master._vcs_indexer.interval_info = self._vsc_indexer_interval_info
        changelog = master.get_changelog()
        assert isinstance(changelog, list)
        assert len(changelog) == len(expected)
        for got_item, expected_item in zip(sorted(changelog, reverse=True), expected):
            assert got_item.vcs_info["revision"] == expected_item.vcs_info["revision"]
            assert got_item.vcs_info["author"] == expected_item.vcs_info["author"]
            assert got_item.vcs_info["msg"] == expected_item.vcs_info["msg"]
            assert got_item.review_ids == expected_item.review_ids
            assert got_item.importance == expected_item.importance
            assert sorted(got_item.problems.keys()) == sorted(expected_item.problems.keys())
            assert got_item.problem_owners == expected_item.problem_owners
            assert got_item.reasons == expected_item.reasons
            assert got_item == expected_item

    def test__changelog_entry_dict(self):
        with mock.patch("sandbox.projects.release_machine.security.get_rm_token"):
            from sandbox.projects.release_machine.helpers.arcanum_helper import ArcanumApi
            arcanum_api_mock = ArcanumApiMock()
            with mock.patch.object(ArcanumApi, "get_review_request", arcanum_api_mock.get_review_request):
                self._test__changelog_entry_dict()

    @staticmethod
    def _test__changelog_entry_dict():
        # review requests and tickets from patch were parsed correctly
        assert ch.ChangeLogEntry(
            {
                "revision": 5924666,
                "author": "alexandr21",
                "msg": "[MAILDLV-2945] Update types module, add task info\n\nREVIEW: 1025728",
                "paths": [("A", "")],  # real paths not needed for this test
                "added": True,
                "date": "2022-07-23T17:05:10Z",
            },
            importance=1,
            reasons={ch.Reasons.REVIEW},
            patches=[{"reviews": {1025728: ["MAILDLV-2945"]}}]
        ).to_dict() == {
            "revision": 5924666,
            "review_ids": [1025728],
            "commit_author": "alexandr21",
            "commit_author_orig": "alexandr21",
            "startrek_tickets": ["MAILDLV-2945"],
            "summary": "[MAILDLV-2945] Update types module, add task info",
            "commit_message": "[MAILDLV-2945] Update types module, add task info\n\nREVIEW: 1025728",
            "te_problems": {},
            "te_problem_owner": [],
            "commit_importance": 1,
            "revision_paths": [("A", "")],
            "added": True,
            "reasons": ["REVIEW"],
            "date": "2022-07-23T17:05:10Z",
        }

        # ticket from review request was parsed correctly
        assert ch.ChangeLogEntry(
            {
                "revision": 5924666,
                "author": "alexandr21",
                "msg": "Message without review and ticket",
                "paths": [("M", "qq")],  # real paths not needed for this test
                "added": True,
                "date": "2022-07-23T17:05:10Z",
            },
            importance=1,
            reasons={ch.Reasons.REVIEW, ch.Reasons.PATHS},
            patches=[{"reviews": {1025728: ["MAILDLV-2945"]}}]
        ).to_dict() == {
            "revision": 5924666,
            "review_ids": [1025728],
            "commit_author": "alexandr21",
            "commit_author_orig": "alexandr21",
            "startrek_tickets": ["MAILDLV-2945"],
            "summary": "Message without review and ticket",
            "commit_message": "Message without review and ticket",
            "te_problems": {},
            "te_problem_owner": [],
            "commit_importance": 1,
            "revision_paths": [("M", "qq")],
            "added": True,
            "reasons": ["PATHS", "REVIEW"],
            "date": "2022-07-23T17:05:10Z",
        }

        # tickets from commit message were parsed correctly
        assert ch.ChangeLogEntry(
            {
                "revision": 5924666,
                "author": "alexandr21",
                "msg": "[MAILDLV-2945] Update types module, add task info\n",
                "paths": [("A", "")],  # real paths not needed for this test
                "added": True,
                "date": "2022-07-23T17:05:10Z",
            },
            importance=10,
            reasons={ch.Reasons.PATHS},
        ).to_dict() == {
            "revision": 5924666,
            "review_ids": [],
            "commit_author": "alexandr21",
            "commit_author_orig": "alexandr21",
            "startrek_tickets": ["MAILDLV-2945"],
            "summary": "[MAILDLV-2945] Update types module, add task info",
            "commit_message": "[MAILDLV-2945] Update types module, add task info\n",
            "te_problems": {},
            "te_problem_owner": [],
            "commit_importance": 10,
            "revision_paths": [("A", "")],
            "added": True,
            "reasons": ["PATHS"],
            "date": "2022-07-23T17:05:10Z",
        }

        # review requests and tickets from commit message were parsed correctly
        assert ch.ChangeLogEntry(
            {
                "revision": 5924666,
                "author": "alexandr21",
                "msg": "Update types module, add task info\n\nREVIEW: 1025728",
                "paths": [("A", "")],  # real paths not needed for this test
                "added": True,
                "date": "2022-07-23T17:05:10Z",
            },
            importance=1,
            reasons={ch.Reasons.PATHS},
        ).to_dict() == {
            "revision": 5924666,
            "review_ids": [1025728],
            "commit_author": "alexandr21",
            "commit_author_orig": "alexandr21",
            "startrek_tickets": ["MAILDLV-2945"],
            "summary": "Update types module, add task info",
            "commit_message": "Update types module, add task info\n\nREVIEW: 1025728",
            "te_problems": {},
            "te_problem_owner": [],
            "commit_importance": 1,
            "revision_paths": [("A", "")],
            "added": True,
            "reasons": ["PATHS"],
            "date": "2022-07-23T17:05:10Z",
        }

    @pytest.mark.parametrize(
        "changelog, expected",
        [
            ([], {})
        ]
    )
    def test__modify_changelog(self, changelog, expected):
        master = ch.ChangeLogMaster(0, "", 0, "", 0, None)
        assert master._modify_changelog(changelog) == expected

    @pytest.mark.parametrize(
        "prod_log, cand_log, expected",
        [
            (
                {
                    -111: {
                        "revision": 111,
                        "msg": "msg111",
                        "author": "author111",
                    },
                    -222: {
                        "revision": 222,
                        "msg": "msg222",
                        "author": "author222",
                    },
                    333: {
                        "revision": 333,
                        "msg": "msg333",
                        "author": "author333",
                    },
                    444: {
                        "revision": 444,
                        "msg": "msg444",
                        "author": "author444",
                    },
                },
                {
                    333: {
                        "revision": 333,
                        "msg": "msg333",
                        "author": "author333",
                    },
                    555: {
                        "revision": 555,
                        "msg": "msg555",
                        "author": "author555",
                    },
                },
                [
                    {
                        "revision": 111,
                        "msg": "msg111",
                        "author": "author111",
                        "added": True,
                    },
                    {
                        "revision": 222,
                        "msg": "msg222",
                        "author": "author222",
                        "added": True,
                    },
                    {
                        "revision": 444,
                        "msg": "msg444",
                        "author": "author444",
                        "added": False,
                    },
                    {
                        "revision": 555,
                        "msg": "msg555",
                        "author": "author555",
                        "added": True,
                    },
                ]
            ),
            (
                {}, {}, []
            ),
            (
                {},
                {
                    -12345: {
                        "revision": 12345,
                        "msg": "msg",
                    },
                },
                [{
                    "revision": 12345,
                    "msg": "msg",
                    "added": False,
                }]
            ),
        ]
    )
    def test__xor_log(self, prod_log, cand_log, expected):
        assert sorted(list(ch.ChangeLogMaster.xor_log(prod_log, cand_log)), key=lambda x: x["revision"]) == expected


COMMON_CHANGES = [
    {
        "added": True,
        "commit_author": "author1",
        "revision_paths": [
            ["M", "/trunk/arcadia/web/src_setup/lib/setup/shiny_discovery/setup.cpp"]
        ],
        "te_problem_owner": [],
        "commit_importance": 1,
        "review_ids": [1345416],
        "te_problems": {},
        "startrek_tickets": ["SHINYDISCOVERY-410"],
        "summary": "summary",
        "reasons": ["PATHS"],
        "commit_message": "commit_message",
        "revision": 7110918,
        "date": "2022-07-23T17:05:10Z",
    },
    {
        "added": True,
        "commit_author": "author2",
        "revision_paths": [
            ["M", "/trunk/arcadia/web/src_setup/lib/handler/extensions/ya.make"]
        ],
        "te_problem_owner": [],
        "commit_importance": 1,
        "review_ids": [],
        "te_problems": {},
        "startrek_tickets": [],
        "summary": "summary",
        "reasons": ["PATHS"],
        "commit_message": "commit_message",
        "revision": 7110758,
        "date": "2022-07-23T17:05:10Z",
    },
]
UNCOMMON_CHANGES = [
    {
        "added": True,
        "commit_author": "author1",
        "revision_paths": [
            ["M", "/trunk/arcadia/web/src_setup/lib/setup/shiny_discovery/setup.cpp"]
        ],
        "te_problem_owner": [],
        "commit_importance": 1,
        "review_ids": [1345416],
        "te_problems": {},
        "startrek_tickets": ["SHINYDISCOVERY-410"],
        "summary": "summary",
        "reasons": ["PATHS"],
        "commit_message": "commit_message",
        "revision": 7110918,
        "date": "2022-07-23T17:05:10Z",
    },
    {
        "added": True,
        "commit_author": "author2",
        "revision_paths": [
            ["M", "/trunk/arcadia/web/path/path.txt"]
        ],
        "te_problem_owner": [],
        "commit_importance": 1,
        "review_ids": [],
        "te_problems": {},
        "startrek_tickets": [],
        "summary": "summary",
        "reasons": ["PATHS"],
        "commit_message": "commit_message",
        "revision": 7111111,
        "date": "2022-07-23T17:05:10Z",
    },
]


@pytest.mark.parametrize(
    "all_changes, expected",
    [
        (
            [
                {
                    "release_item": None,
                    "changes": [
                        {"revision": 1234},
                    ]
                },
                {
                    "release_item": None,
                    "changes": [
                        {"revision": 1234},
                    ]
                },
            ],
            [
                {
                    "release_items": [
                        {"release_item": None},
                        {"release_item": None},
                    ],
                    "changes": [
                        {"revision": 1234},
                    ]
                }
            ]
        ),
        (
            [
                {
                    "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-4",
                    "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                    "release_item": {
                        "major_release": "266",
                        "resource_name": "resource_name1",
                        "timestamp": 1594687689,
                        "component": "src_setup",
                        "status": "stable",
                        "minor_release": "4",
                        "id": "1604153007"
                    },
                    "baseline_rev_trunk": 7091243,
                    "baseline_revision": 7100282,
                    "first_revision": 7091243,
                    "candidate_rev_trunk": 7110932,
                    "candidate_revision": 7110936,
                    "changes": COMMON_CHANGES
                },
                {
                    "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-4",
                    "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                    "release_item": {
                        "major_release": "266",
                        "resource_name": "resource_name2",
                        "timestamp": 1594687689,
                        "component": "src_setup",
                        "status": "stable",
                        "minor_release": "4",
                        "id": "1604364755"
                    },
                    "baseline_rev_trunk": 7091243,
                    "baseline_revision": 7100282,
                    "first_revision": 7091243,
                    "candidate_rev_trunk": 7110932,
                    "candidate_revision": 7110936,
                    "changes": COMMON_CHANGES
                },
                {
                    "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-1",
                    "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                    "release_item": {
                        "major_release": "266",
                        "resource_name": "resource_name3",
                        "timestamp": 1594687689,
                        "component": "src_setup",
                        "status": "stable",
                        "minor_release": "1",
                        "id": "1601111111"
                    },
                    "baseline_rev_trunk": 7090000,
                    "baseline_revision": 7090001,
                    "first_revision": 7091243,
                    "candidate_rev_trunk": 7110932,
                    "candidate_revision": 7110936,
                    "changes": COMMON_CHANGES
                },
                {
                    "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-4",
                    "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                    "release_item": {
                        "major_release": "266",
                        "resource_name": "resource_name4",
                        "timestamp": 1594687689,
                        "component": "src_setup",
                        "status": "stable",
                        "minor_release": "4",
                        "id": "1604153007"
                    },
                    "baseline_rev_trunk": 7091243,
                    "baseline_revision": 7100282,
                    "first_revision": 7091243,
                    "candidate_rev_trunk": 7110932,
                    "candidate_revision": 7110936,
                    "changes": UNCOMMON_CHANGES
                }
            ],
            [
                {
                    "release_items": [
                        {
                            "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-4",
                            "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                            "release_item": {
                                "major_release": "266",
                                "resource_name": "resource_name1",
                                "timestamp": 1594687689,
                                "component": "src_setup",
                                "status": "stable",
                                "minor_release": "4",
                                "id": "1604153007"
                            },
                            "baseline_rev_trunk": 7091243,
                            "baseline_revision": 7100282,
                            "first_revision": 7091243,
                            "candidate_rev_trunk": 7110932,
                            "candidate_revision": 7110936,
                        },
                        {
                            "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-4",
                            "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                            "release_item": {
                                "major_release": "266",
                                "resource_name": "resource_name2",
                                "timestamp": 1594687689,
                                "component": "src_setup",
                                "status": "stable",
                                "minor_release": "4",
                                "id": "1604364755"
                            },
                            "baseline_rev_trunk": 7091243,
                            "baseline_revision": 7100282,
                            "first_revision": 7091243,
                            "candidate_rev_trunk": 7110932,
                            "candidate_revision": 7110936,
                        },
                        {
                            "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-1",
                            "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                            "release_item": {
                                "major_release": "266",
                                "resource_name": "resource_name3",
                                "timestamp": 1594687689,
                                "component": "src_setup",
                                "status": "stable",
                                "minor_release": "1",
                                "id": "1601111111"
                            },
                            "baseline_rev_trunk": 7090000,
                            "baseline_revision": 7090001,
                            "first_revision": 7091243,
                            "candidate_rev_trunk": 7110932,
                            "candidate_revision": 7110936,
                        },
                    ],
                    "changes": COMMON_CHANGES,
                },
                {
                    "release_items": [
                        {
                            "baseline_path": "arcadia:/arc/tags/src_setup/stable-266-4",
                            "candidate_path": "arcadia:/arc/branches/src_setup/stable-268",
                            "release_item": {
                                "major_release": "266",
                                "resource_name": "resource_name4",
                                "timestamp": 1594687689,
                                "component": "src_setup",
                                "status": "stable",
                                "minor_release": "4",
                                "id": "1604153007"
                            },
                            "baseline_rev_trunk": 7091243,
                            "baseline_revision": 7100282,
                            "first_revision": 7091243,
                            "candidate_rev_trunk": 7110932,
                            "candidate_revision": 7110936,
                        }
                    ],
                    "changes": UNCOMMON_CHANGES,
                }
            ],
        )
    ]
)
def test__deduplicate_changelog_by_changes(all_changes, expected):
    assert ch.deduplicate_changelog_by_changes(all_changes) == expected
