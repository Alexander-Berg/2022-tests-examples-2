# -*- coding: utf-8 -*-

import mock
import pytest
import textwrap as tw

from sandbox.projects.release_machine.helpers import svn_helper


class MockArcadia(object):
    @classmethod
    def log_func_mock(cls, url, revision_from=None, *args, **kwargs):
        log = {
            "arcadia:/arc/tags/rtmr/stable-31-73": [
                {
                    "copies": [("/branches/rtmr/stable-31", "5900924")],
                }
            ],
            "arcadia:/arc/branches/rtmr/stable-31": [
                {
                    "copies": [("/branches/kikimr/stable-19-6", "5744830")],
                }
            ],
            "arcadia:/arc/branches/kikimr/stable-19-6": [
                {
                    "copies": [("/trunk", "5695521")],
                }
            ],
            "arcadia:/arc/branches/abt/stable-104": [
                {
                    "copies": [("/branches/user_sessions/stable-132", "5899807")],
                }
            ],
            "arcadia:/arc/branches/user_sessions/stable-132": [
                {
                    "copies": [("/trunk", "5891718")],
                }
            ],
            "arcadia:/arc/branches/release_machine/release_machine_ui/stable-140": [
                {
                    "copies": [("/trunk", "5879337")],
                }
            ],
            "arcadia:/robots/tags/dynamic_ranking_models/experiments/base/stable-339": [
                {
                    "copies": [("/branches/base/dynamic_ranking_models/experiment", "5458913")],
                }
            ],
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-7954": [
                {
                    "copies": [("/trunk", "6022746")],
                    "revision": "6022749",
                },
                {
                    "revision": "6022966",
                },
                {
                    "revision": "6023166",
                },
            ],
            "arcadia:/arc@6590335": [
                {
                    "revision": "6590335",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/infra/cores/app/helpers.py"
                        },
                    ],
                },
            ],
            "arcadia:/arc@6589562": [
                {
                    "revision": "6589562",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/infra/cores/app/const.py"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/infra/cores/app/core_gc.py"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/infra/cores/app/helpers.py"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/infra/cores/app/models.py"
                        },
                    ],
                },
            ],
            "arcadia:/arc@6589818": [
                {
                    "revision": "6589818",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/infra/cores/app/helpers.py"
                        },
                    ],
                },
            ],
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-11050@6765033": [
                {
                    "revision": "6765033",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": False,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app/helpers.py"
                        },
                    ],
                },
            ],
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-11050@6764996": [
                {
                    "revision": "6764996",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": False,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app/const.py"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app/core_gc.py"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app/helpers.py"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app/models.py"
                        },
                    ],
                },
            ],
            "arcadia:/arc@1093250": [
                {
                    "revision": "1093250",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/search/garden/sandbox-tasks/projects/WizardRuntimeBuild/__init__.py",
                        },
                    ]
                }
            ],
            "arcadia:/arc/branches/upple/stable-353@6668289": [
                {
                    "revision": "6668289",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": False,
                            "text": "/branches/upple/stable-353/arcadia"
                        },
                        {
                            "action": "M",
                            "text-mods": False,
                            "text": "/branches/upple/stable-353/arcadia/kernel"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/upple/stable-353/arcadia/kernel/blender/factor_storage/protos/storage.proto"
                        },
                        {
                            "action": "M",
                            "text-mods": False,
                            "text": "/branches/upple/stable-353/arcadia/yweb"
                        },
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/branches/upple/stable-353/arcadia/yweb/blender/lib/dynamic_factors/storage.cpp"
                        },
                    ]
                }
            ],
            "arcadia:/arc@6765117": [
                {
                    "revision": "6765117",
                    "paths": [
                        {
                            "action": "A",
                            "text-mods": False,
                            "text": "/trunk/arcadia/junk/glebov-da/test_bin"
                        },
                        {
                            "action": "A",
                            "text-mods": True,
                            "text": "/trunk/arcadia/junk/glebov-da/test_bin/sample.txt"
                        },
                    ]
                }
            ],
            "arcadia:/arc@6765122": [
                {
                    "revision": "6765122",
                    "paths": [
                        {
                            "action": "M",
                            "text-mods": True,
                            "text": "/trunk/arcadia/junk/glebov-da/test_bin/sample.txt"
                        },
                    ]
                }
            ]
        }
        if revision_from:
            return log.get("{url}@{rev}".format(url=url, rev=revision_from)) or log.get(url)
        return log.get(url)

    @classmethod
    def info_func_mock(cls, url, *args, **kwargs):
        info = {
            "arcadia:/arc/trunk/arcadia/infra/cores/app/helpers.py@6590335": {
                "entry_kind": "file",
            },
            "arcadia:/arc/trunk/arcadia/infra/cores/app@6589562": {
                "entry_kind": "dir",
            },
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app/helpers.py@6765033": {
                "entry_kind": "file",
            },
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-11050/arcadia/infra/cores/app@6764996": {
                "entry_kind": "dir",
            },
            "arcadia:/arc/trunk/arcadia/search/garden/sandbox-tasks/projects/WizardRuntimeBuild/__init__.py@1093250": {
                "entry_kind": "file",
            },
        }
        return info.get(url)


@pytest.mark.parametrize(
    "path, repo_base_url, trunk_url, expected",
    [
        ("arcadia:/arc/tags/rtmr/stable-31-73", "arcadia:/arc", "arcadia:/arc/trunk", 5695521),
        ("arcadia:/arc/branches/abt/stable-104", "arcadia:/arc", "arcadia:/arc/trunk", 5891718),
        (
            "arcadia:/arc/branches/release_machine/release_machine_ui/stable-140",
            "arcadia:/arc",
            "arcadia:/arc/trunk",
            5879337
        ),
        (
            "arcadia:/robots/tags/dynamic_ranking_models/experiments/base/stable-339",
            "arcadia:/robots",
            "arcadia:/robots/branches/base/dynamic_ranking_models/experiment",
            5458913
        ),
        ("arcadia:/arc/trunk/arcadia/sandbox", "arcadia:/arc", "arcadia:/arc/trunk", None),
    ]
)
def test__get_last_trunk_revision_before_branching(path, repo_base_url, trunk_url, expected):
    from sandbox.sdk2.vcs.svn import Arcadia
    with mock.patch.object(Arcadia, "log", MockArcadia.log_func_mock):
        result = svn_helper.SvnHelper.get_last_trunk_revision_before_copy(path, repo_base_url, trunk_url)
        assert result == expected


@pytest.mark.parametrize(
    "vcs_info, expected_revs",
    [
        (
            {
                "revision": "1234567",
                "msg": "Simple commit message"
            },
            [1234567],
        ),
        (
            {
                "revision": "5385495",
                "msg": tw.dedent("""
                    ------------------------------------------------------------------------
                    r5385495 | robot-srch-releaser | 2019-07-31 08:53:53 +0000 (Ср, 31 июл 2019) | 14 lines
                    Merge from trunk: r5385459
                     [diff-resolver:ulyanov]  [rm:beta] Sandbox task: https://sandbox.yandex-team.ru/task/477708510/view
                    Task author: ipa4lov@
                    Description: Merging revision(s) 5385459
                      > .................................................................
                      > INCLUDE: r5385459 | ulyanov | 2019-07-31 11:45:49 +0300 (Wed, 31 Jul 2019) | 4 lines
                      >
                      > [mergeto:middle] Add option for enabling bans cache
                      >
                      > REVIEW: 898150
                      > Note: mandatory check (NEED_CHECK) was skipped
                      > .................................................................
                    ------------------------------------------------------------------------
                """)
            },
            [5385459]
        ),
        (
            {
                "revision": "4733397",
                "msg": tw.dedent("""
                    ------------------------------------------------------------------------
                    r4733397 | eivanov89 | 2019-04-01 14:52:32 +0000 (Пн, 01 апр 2019) | 890 lines

                    merge from branches/kikimr/stable-19-2: 4631129,4660782,4662204,4662826,4733258

                      > .................................................................
                      > INCLUDE: r4631129 | galaxycrab | 2019-03-16 00:01:03 +0300 (Sat, 16 Mar 2019) | 1 line
                      >
                      > Merge features for YMQ beta launch __FORCE_COMMIT__
                      > .................................................................
                      > INCLUDE: r4660782 | ienkovich | 2019-03-18 16:17:58 +0300 (Mon, 18 Mar 2019) | 12 lines
                      >
                      > merge from trunk: 4660402
                      >
                      > > .................................................................
                      > > INCLUDE: r4660402 | ienkovich | 2019-03-18 14:52:02 +0300 (Mon, 18 Mar 2019) | 5 lines
                      > >
                      > > Improve error report for pool manipulations.
                      > >
                      > > Pull-request for branch users/ienkovich/local/2c526c2771
                      > >
                      > > REVIEW: 766996
                      > > .................................................................
                      > .................................................................
                      > INCLUDE: r4662204 | xenoxeno | 2019-03-18 21:39:35 +0300 (Mon, 18 Mar 2019) | 11 lines
                      >
                      > merge from trunk: 4662202
                      >
                      > > .................................................................
                      > > INCLUDE: r4662202 | xenoxeno | 2019-03-18 21:38:32 +0300 (Mon, 18 Mar 2019) | 4 lines
                      > >
                      > > fix typo KIKIMR-6673
                      > >
                      > > REVIEW: 769060
                      > > Note: mandatory check (NEED_CHECK) was skipped
                      > > .................................................................
                      > .................................................................
                      > INCLUDE: r4662826 | ienkovich | 2019-03-18 23:51:13 +0300 (Mon, 18 Mar 2019) | 12 lines
                      >
                      > merge from trunk: r4608288, r4609034
                      >
                      > > .................................................................
                      > > INCLUDE: r4608288 | alexvru | 2019-03-12 14:43:41 +0300 (Tue, 12 Mar 2019) | 5 lines
                      > >
                      > > Report latencies from aggregated buckets
                      > >
                      > > Pull-request for branch users/alexvru/bsdc/report-latencies-from-buckets
                      > >
                      > > REVIEW: 762155
                      > > .................................................................
                      > > INCLUDE: r4609034 | alexvru | 2019-03-12 17:21:35 +0300 (Tue, 12 Mar 2019) | 5 lines
                      > >
                      > > Separate put and get stats in latency reporting
                      > >
                      > > Pull-request for branch users/alexvru/bsdc/separate-put-and-get-stats
                      > >
                      > > REVIEW: 762209
                      > > .................................................................
                      > .................................................................
                      > INCLUDE: r4733258 | d1vanov | 2019-04-01 17:17:33 +0300 (Mon, 01 Apr 2019) | 12 lines
                      >
                      > merge from trunk: 4733196
                      >
                      > > .................................................................
                      > > INCLUDE: r4733196 | d1vanov | 2019-04-01 17:10:25 +0300 (Mon, 01 Apr 2019) | 5 lines
                      > >
                      > > NBS-363: correct test
                      > >
                      > > ([arc::pullid] 22784084-20ec160f-b385cdaa-a98b3187)
                      > >
                      > > REVIEW: 782306
                      > > .................................................................
                      > .................................................................
                    ------------------------------------------------------------------------
                """),
            },
            [4631129, 4660402, 4662202, 4608288, 4609034, 4733196],
        ),
        (
            {
                "revision": "1234567",
                "msg": tw.dedent("""
                    ------------------------------------------------------------------------
                    r5345915 | robot-srch-releaser | 2019-07-23 18:35:21 +0000 (Вт, 23 июл 2019) | 1 line

                    [branch:middle] (r5345911, sandboxtask:472969179)
                    ------------------------------------------------------------------------
                """)
            },
            []
        ),
        (
            {
                "revision": "1234567",
                "msg": tw.dedent("""
                    ------------------------------------------------------------------------
                    r5345943 | robot-srch-releaser | 2019-07-23 18:43:30 +0000 (Вт, 23 июл 2019) | 2 lines

                    [tag:arcadia:/arc/tags/middle/stable-312-1] from branch arcadia:/arc/branches/middle/stable-312, sandboxtask:472972578, copy-revision:5345915.
                    . Created from Sandbox task https://sandbox.yandex-team.ru/task/472972578
                    ------------------------------------------------------------------------
                """)
            },
            []
        ),
        (
            {
                "revision": 5882981,
                "msg": tw.dedent("""
                    Rollback: r5857612, r5855226
                     [diff-resolver:gluk47]  Sandbox task: https://sandbox.yandex-team.ru/task/539511938/view
                    Task author: robot-srch-releaser@
                    Description: Run task ROLLBACK_COMMIT with mode release_machine for revisions 5855226, 5857612 for component begemot.
                    Task was created in Release Machine UI
                    [fix:begemot:5855226]

                    Note: mandatory review (NEED_REVIEW) was skipped
                """)
            },
            [-5857612, -5855226]
        ),
        (
            {
                "revision": 5983052,
                "msg": tw.dedent("""
                    Merge from trunk: r5983049
                     [diff-resolver:w0lfen]  Sandbox task: https://sandbox.yandex-team.ru/task/550571242/view
                     Task author: ageraab@
                     Description: rollback r5981624
                     [fix:begemot:5983049]

                       > .................................................................
                       > INCLUDE: r5983049 | robot-srch-releaser | 2019-11-18 18:55:13 +0300 (Mon, 18 Nov 2019) | 7 lines
                       >
                       > Rollback: r5981624
                       > [diff-resolver:w0lfen]  Sandbox task: https://sandbox.yandex-team.ru/task/550571242/view
                       > Task author: ageraab@
                       > Description: rollback r5981624
                       > [fix:begemot:5981624]
                       >
                       > Note: mandatory check (NEED_CHECK) was skipped
                       > .................................................................

                """)
            },
            [-5981624]
        )
    ]
)
def test__get_initial_revs(vcs_info, expected_revs):
    init_revs = svn_helper.SvnHelper.get_initial_revs(vcs_info)
    assert [i.rev for i in init_revs] == expected_revs


@pytest.mark.parametrize(
    "is_reversed", [(True,), (False,)]
)
def test_iter_tags_not_reversed(is_reversed):
    branch_name = "arcadia:/arc/branches/release_machine/release_machine_test/stable-7954"
    revision_to = None
    tags = [(2, "6022966"), (3, "6023166")]
    if is_reversed:
        tags.reverse()

    from sandbox.sdk2.vcs.svn import Arcadia
    with mock.patch.object(Arcadia, "log", MockArcadia.log_func_mock):
        assert tags == [tag for tag in svn_helper.SvnHelper.iter_tags(branch_name, revision_to, is_reversed)]


@pytest.mark.parametrize(
    "revs, full_branch_path, expected_common_path",
    [
        (
            [6590335],
            "arcadia:/arc",
            ["trunk", "arcadia", "infra", "cores", "app"],
        ),
        (
            [6589562, 6589818],
            "arcadia:/arc",
            ["trunk", "arcadia", "infra", "cores", "app"],
        ),
        (
            [6765033],
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-11050",
            ["branches", "release_machine", "release_machine_test", "stable-11050", "arcadia", "infra", "cores", "app"],
        ),
        (
            [6764996],
            "arcadia:/arc/branches/release_machine/release_machine_test/stable-11050",
            ["branches", "release_machine", "release_machine_test", "stable-11050", "arcadia", "infra", "cores", "app"],
        ),
        (
            [1093250],
            "arcadia:/arc",
            ["trunk", "arcadia", "search", "garden", "sandbox-tasks", "projects", "WizardRuntimeBuild"],
        )
    ]
)
def test_get_common_path(revs, full_branch_path, expected_common_path):
    from sandbox.sdk2.vcs.svn import Arcadia
    with mock.patch.object(Arcadia, "log", MockArcadia.log_func_mock):
        with mock.patch.object(Arcadia, "info", MockArcadia.info_func_mock):
            common_path = svn_helper.get_common_path(revs, full_branch_path)
            assert common_path == expected_common_path


@pytest.mark.parametrize(
    "full_branch_path, revs, expected_all_paths",
    [
        (
            "arcadia:/arc/branches/upple/stable-353",
            [6668289],
            [
                ("M", "/branches/upple/stable-353/arcadia/kernel/blender/factor_storage/protos/storage.proto"),
                ("M", "/branches/upple/stable-353/arcadia/yweb/blender/lib/dynamic_factors/storage.cpp"),
            ],
        ),
        (
            "arcadia:/arc",
            [6765117],
            [
                ("A", "/trunk/arcadia/junk/glebov-da/test_bin"),
                ("A", "/trunk/arcadia/junk/glebov-da/test_bin/sample.txt")
            ]
        ),
        (
            "arcadia:/arc",
            [6765122],
            [
                ("M", "/trunk/arcadia/junk/glebov-da/test_bin/sample.txt"),
            ]
        )
    ]
)
def test_get_paths_for_revisions(full_branch_path, revs, expected_all_paths):
    from sandbox.sdk2.vcs.svn import Arcadia
    with mock.patch.object(Arcadia, "log", MockArcadia.log_func_mock):
        all_paths = svn_helper.get_paths_for_revisions(full_branch_path, revs)
        for path, expected_path in zip(all_paths, expected_all_paths):
            assert path.operation == expected_path[0]
            assert path.path_list == expected_path[1].split("/")
