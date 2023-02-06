# -*- coding: utf-8 -*-

import mock
import pytest
import textwrap as tw

from sandbox.projects.release_machine import arc_helper
import sandbox.projects.release_machine.core.const as rm_const


@pytest.mark.parametrize(
    "svn_branch_log, expected_filtered_branch_log",
    [
        (
            [
                {
                    "revision": 1234567,
                    "msg": "Simple commit message"
                },
                {
                    "revision": 1234767,
                    "msg": "One more commit message"
                },
                {
                    "revision": 1234867,
                    "msg": "Third commit message"
                },
            ],
            [1234567, 1234767, 1234867]
        ),
        (
            [
                {
                    "revision": 5385495,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:53:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5385595,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:55:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5385695,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:56:53 +0000 (Ср, 31 июл 2019) | 14 lines
                        __ignored__: r5385495
                    """)
                },
                {
                    "revision": 5385895,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:57:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
            ],
            [5385595, 5385895],
        ),
        (
            [
                {
                    "revision": 5385495,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:53:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5385595,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:55:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5385695,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:56:53 +0000 (Ср, 31 июл 2019) | 14 lines
                        __ignored__: r5385495, r5385595
                    """)
                },
                {
                    "revision": 5385895,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:57:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5485495,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:53:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5485595,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:55:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5485695,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:56:53 +0000 (Ср, 31 июл 2019) | 14 lines
                        __ignored__: 5485495
                    """)
                },
                {
                    "revision": 5485895,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:57:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
            ],
            [5385895, 5485595, 5485895],
        ),
    ]
)
def test_get_initial_revs(svn_branch_log, expected_filtered_branch_log):
    filtered_branch_log = arc_helper.filter_ignored_revisions(svn_branch_log)
    assert [i["revision"] for i in filtered_branch_log] == expected_filtered_branch_log


class ComponentInfoMock(object):
    pass


c_info = ComponentInfoMock()
c_info.full_branch_path = lambda branch_num: "arcadia:/arc/tags/rtmr/stable-{}".format(branch_num)


class MockArcadia(object):
    @classmethod
    def log_func_mock(cls, url, revision_from=None, *args, **kwargs):
        log = {
            "arcadia:/arc/tags/rtmr/stable-1": [
                {
                    "revision": 1234567,
                    "msg": "Merge from trunk: r123321\nSimple commit message\nSync arc commit: aaaa"
                },
                {
                    "revision": 1234767,
                    "msg": "Merge from trunk: r123351\nOne more commit message\nSync arc commit: aaaa"
                },
                {
                    "revision": 1234867,
                    "msg": "Merge from trunk: r123721\nThird commit message\nSync arc commit: aaaa"
                },
            ],
            "arcadia:/arc/tags/rtmr/stable-2": [
                {
                    "revision": 5385495,
                    "msg": "Merge from trunk: r123321\nSimple commit message\nSync arc commit: aaaa"
                },
                {
                    "revision": 5385595,
                    "msg": "Merge from trunk: r123421\nOne more commit message\nSync arc commit: aaaa"
                },
                {
                    "revision": 5385695,
                    "msg": tw.dedent("""
                        ------------------------------------------------------------------------
                        Rollback: r5385495\nOne more commit message\nSync arc commit: aaaa
                        __ignored__: r5385495
                    """)
                },
                {
                    "revision": 5385895,
                    "msg": "Merge from trunk: r123521\nOne more commit message\nSync arc commit: aaaa"
                },
            ],
            "arcadia:/arc/tags/rtmr/stable-3": [
                {
                    "revision": 5385495,
                    "msg": tw.dedent("""
                        Merge from trunk: r123421\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:53:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5385595,
                    "msg": tw.dedent("""
                        Merge from trunk: r123521\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:55:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5385695,
                    "msg": tw.dedent("""
                        Rollback: r5385495, r5385595\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:56:53 +0000 (Ср, 31 июл 2019) | 14 lines
                        __ignored__: 5385495, 5385595
                    """)
                },
                {
                    "revision": 5385895,
                    "msg": tw.dedent("""
                        Merge from trunk: r123721\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:57:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5485495,
                    "msg": tw.dedent("""
                        Merge from trunk: r123821\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:53:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5485595,
                    "msg": tw.dedent("""
                        Merge from trunk: r123921\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:55:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
                {
                    "revision": 5485695,
                    "msg": tw.dedent("""
                        Rollback: r5485495\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:56:53 +0000 (Ср, 31 июл 2019) | 14 lines
                        __ignored__: 5485495
                    """)
                },
                {
                    "revision": 5485895,
                    "msg": tw.dedent("""
                        Merge from trunk: r125421\nSync arc commit: aaaa
                        ------------------------------------------------------------------------
                        r5385495 | robot-srch-releaser | 2019-07-31 08:57:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    """)
                },
            ],
        }
        return log.get(url)


@pytest.mark.parametrize(
    "branch_num, expected_branch_commit_instances",
    [
        (
            1,
            [
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=1234567,
                    svn_revs=[[123321]],
                ),
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=1234767,
                    svn_revs=[[123351]],
                ),
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=1234867,
                    svn_revs=[[123721]],
                ),
            ]
        ),
        (
            2,
            [
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=5385595,
                    svn_revs=[[123421]],
                ),
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=5385895,
                    svn_revs=[[123521]],
                ),
            ]
        ),
        (
            3,
            [
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=5385895,
                    svn_revs=[[123721]],
                ),
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=5485595,
                    svn_revs=[[123921]],
                ),
                rm_const.BranchCommit(
                    action_type=rm_const.ActionType.MERGE,
                    current_hash="aaaa",
                    current_rev=5485895,
                    svn_revs=[[125421]],
                ),
            ]
        ),
    ]
)
def test_get_merges_to_svn_branch(branch_num, expected_branch_commit_instances):
    from sandbox.sdk2.vcs.svn import Arcadia
    with mock.patch.object(Arcadia, "log", MockArcadia.log_func_mock):
        branch_commit_instances = arc_helper._get_merges_to_svn_branch(c_info, branch_num)
        assert (
            [branch_commit_instance.action_type for branch_commit_instance in branch_commit_instances] ==
            [branch_commit_instance.action_type for branch_commit_instance in expected_branch_commit_instances]
        )
        assert (
            [branch_commit_instance.current_hash for branch_commit_instance in branch_commit_instances] ==
            [branch_commit_instance.current_hash for branch_commit_instance in expected_branch_commit_instances]
        )
        assert (
            [branch_commit_instance.current_rev for branch_commit_instance in branch_commit_instances] ==
            [branch_commit_instance.current_rev for branch_commit_instance in expected_branch_commit_instances]
        )
        assert (
            [branch_commit_instance.svn_revs for branch_commit_instance in branch_commit_instances] ==
            [branch_commit_instance.svn_revs for branch_commit_instance in expected_branch_commit_instances]
        )
