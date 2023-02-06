# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import unittest

from sandbox.projects.release_machine.tests.test_component_info import TestComponent
from sandbox.projects.release_machine.helpers import wiki_helper
import sandbox.projects.release_machine.core.const as rm_const


FIRST_CHANGELOG = """
#|
||  | **Revision, Review** | **Commit author** | **Summary** ||
|| **BALANCER-1604** ||
||  | ((https://a.yandex-team.ru/arc/commit/4228991 4228991))
((https://a.yandex-team.ru/review/611196/files REVIEW: 611196)) | staff:velavokr | renamed Wait into Join in TMyCont ||
||  | ((https://a.yandex-team.ru/arc/commit/4192728 4192728))
((https://a.yandex-team.ru/review/604112/files REVIEW: 604112)) | staff:velavokr | %%BALANCER-1604%% JoinFrom -> Join in IFiber ||
||  | ((https://a.yandex-team.ru/arc/commit/4184796 4184796))
((https://a.yandex-team.ru/review/602836/files REVIEW: 602836)) | staff:smalukav | %%BALANCER-1604%%: Remove end event from TMyCont ||
|| **BALANCER-1632**
**BALANCER-1726** ||
||  | ((https://a.yandex-team.ru/arc/commit/4173249 4173249))
((https://a.yandex-team.ru/review/597302/files REVIEW: 597302)) | staff:xpahos | %%BALANCER-1726%% lost submodules stats for exp_static ||
|| **NO TRACKER ISSUE SPECIFIED** ||
||  | ((https://a.yandex-team.ru/arc/commit/4444444 4444444))
((https://a.yandex-team.ru/review/111111/files REVIEW: 111111)) | staff:pupkin | summary ||
|#
"""


class GroupChangesByTicketsTests(unittest.TestCase):
    maxDiff = None

    CASES = [(
        [
            {
                "te_problems": {},
                "startrek_tickets": [
                    "BALANCER-1604"
                ],
                "review_id": 611196,
                "commit_author": "velavokr",
                "revision_paths": [],
                "te_problem_owner": None,
                "summary": "renamed Wait into Join in TMyCont",
                "commit_importance": 2,
                "added": True,
                "revision": 4228991
            },
            {
                "te_problems": {},
                "startrek_tickets": [
                    "BALANCER-1604"
                ],
                "review_id": 604112,
                "commit_author": "velavokr",
                "revision_paths": [],
                "te_problem_owner": None,
                "summary": "%%BALANCER-1604%% JoinFrom -> Join in IFiber",
                "commit_importance": 2,
                "added": True,
                "revision": 4192728
            },
            {
                "te_problems": {},
                "startrek_tickets": [
                    "BALANCER-1604"
                ],
                "review_id": 602836,
                "commit_author": "smalukav",
                "revision_paths": [],
                "te_problem_owner": None,
                "summary": "%%BALANCER-1604%%: Remove end event from TMyCont",
                "commit_importance": 2,
                "added": True,
                "revision": 4184796
            },
            {
                "te_problems": {},
                "startrek_tickets": [
                    "BALANCER-1632",
                    "BALANCER-1726"
                ],
                "review_id": 597302,
                "commit_author": "xpahos",
                "revision_paths": [],
                "te_problem_owner": None,
                "summary": "%%BALANCER-1726%% lost submodules stats for exp_static",
                "commit_importance": 2,
                "added": True,
                "revision": 4173249
            },
            {
                "te_problems": {},
                "startrek_tickets": [],
                "review_id": 111111,
                "commit_author": "pupkin",
                "revision_paths": [],
                "te_problem_owner": None,
                "summary": "summary",
                "commit_importance": 2,
                "added": True,
                "revision": 4444444
            },
        ],
        FIRST_CHANGELOG,
    )]

    def testGoodCases(self):
        c_info = TestComponent()
        for changelog, answer in self.CASES:
            self.assertEqual(wiki_helper.group_changes_by_tickets(c_info, changelog), answer)


TABLE_BEFORE_1 = """\
|| **Tag** | **Revisions merged** | **Branch revision** | **Revision info** | **Merge task id** | **Action** ||
||  | ((https://a.yandex-team.ru/arc/commit/4266462 4266462)) |  |  | ((https://sandbox.yandex-team.ru/task/346143080/view 346143080)) | merge ||
|| 2 | ((https://a.yandex-team.ru/arc/commit/4266462 4266462)) | ((https://a.yandex-team.ru/arc/commit/4282396 4282396)) | Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4266462 4266462))
Result revision: ((https://a.yandex-team.ru/arc/commit/4282396 4282396))
[][][] [diff-resolver:ilyusha]

Sandbox task: https://sandbox.yandex-team.ru/task/346143080/view
Task author: ilyusha@
Description: Merge 4266462 to abt-15

  > .................................................................
  > INCLUDE: r4266462 ""|"" ilyusha ""|"" 2018-12-04 21:38:50 +0300 (Tue, 04 Dec 2018) ""|"" 5 lines
  >
  > [LSD] Replace metrics.json from code to sandbox
  >
  > USEREXP-5820
  >
  > REVIEW: 567522
  > ................................................................. |  |  ||
||  | ((https://a.yandex-team.ru/arc/commit/4268872 4268872)) |  |  | ((https://sandbox.yandex-team.ru/task/346179729/view 346179729)) | merge ||
|| 3 | ((https://a.yandex-team.ru/arc/commit/4268872 4268872)) | ((https://a.yandex-team.ru/arc/commit/4282763 4282763)) | Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4268872 4268872))
Result revision: ((https://a.yandex-team.ru/arc/commit/4282763 4282763))
[][][] [diff-resolver:ilyusha]

Sandbox task: https://sandbox.yandex-team.ru/task/346179729/view
Task author: ilyusha@
Description: Merge 4268872 to abt-15

  > .................................................................
  > INCLUDE: r4268872 ""|"" ilyusha ""|"" 2018-12-05 19:29:46 +0300 (Wed, 05 Dec 2018) ""|"" 5 lines
  >
  > [LSD] Delete lsd_to from settings and debian package
  >
  > USEREXP-5820
  >
  > REVIEW: 631059
  > ................................................................. |  |  ||
||  | ((https://a.yandex-team.ru/arc/commit/4268329 4268329)) |  |  | ((https://sandbox.yandex-team.ru/task/347271930/view 347271930)) | merge ||
"""

MESSAGE = """Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4268329 4268329))
Result revision: ((https://a.yandex-team.ru/arc/commit/4289261 4289261))
[][][] [diff-resolver:orepin]

Sandbox task: https://sandbox.yandex-team.ru/task/347271930/view
Task author: orepin@
Description: merge 4268329 to abt

  > .................................................................
  > INCLUDE: r4268329 | orepin | 2018-12-05 17:07:54 +0300 (Wed, 05 Dec 2018) | 3 lines
  >
  > Introduce rearrange rule for fast blender meta features (BLNDR-2939), related factors builder refactoring
  >
  > REVIEW: 629135
  > .................................................................\
"""

ROW_TO_ADD = [
    "4",
    "((https://a.yandex-team.ru/arc/commit/4268329 4268329))",
    "((https://a.yandex-team.ru/arc/commit/4289261 4289261))",
    MESSAGE,
    "",
    "",
]

TABLE_AFTER_1 = """\
|| **Tag** | **Revisions merged** | **Branch revision** | **Revision info** | **Merge task id** | **Action** ||
||  | ((https://a.yandex-team.ru/arc/commit/4266462 4266462)) |  |  | ((https://sandbox.yandex-team.ru/task/346143080/view 346143080)) | merge ||
|| 2 | ((https://a.yandex-team.ru/arc/commit/4266462 4266462)) | ((https://a.yandex-team.ru/arc/commit/4282396 4282396)) | Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4266462 4266462))
Result revision: ((https://a.yandex-team.ru/arc/commit/4282396 4282396))
[][][] [diff-resolver:ilyusha]

Sandbox task: https://sandbox.yandex-team.ru/task/346143080/view
Task author: ilyusha@
Description: Merge 4266462 to abt-15

  > .................................................................
  > INCLUDE: r4266462 ""|"" ilyusha ""|"" 2018-12-04 21:38:50 +0300 (Tue, 04 Dec 2018) ""|"" 5 lines
  >
  > [LSD] Replace metrics.json from code to sandbox
  >
  > USEREXP-5820
  >
  > REVIEW: 567522
  > ................................................................. |  |  ||
||  | ((https://a.yandex-team.ru/arc/commit/4268872 4268872)) |  |  | ((https://sandbox.yandex-team.ru/task/346179729/view 346179729)) | merge ||
|| 3 | ((https://a.yandex-team.ru/arc/commit/4268872 4268872)) | ((https://a.yandex-team.ru/arc/commit/4282763 4282763)) | Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4268872 4268872))
Result revision: ((https://a.yandex-team.ru/arc/commit/4282763 4282763))
[][][] [diff-resolver:ilyusha]

Sandbox task: https://sandbox.yandex-team.ru/task/346179729/view
Task author: ilyusha@
Description: Merge 4268872 to abt-15

  > .................................................................
  > INCLUDE: r4268872 ""|"" ilyusha ""|"" 2018-12-05 19:29:46 +0300 (Wed, 05 Dec 2018) ""|"" 5 lines
  >
  > [LSD] Delete lsd_to from settings and debian package
  >
  > USEREXP-5820
  >
  > REVIEW: 631059
  > ................................................................. |  |  ||
|| 4 | ((https://a.yandex-team.ru/arc/commit/4268329 4268329)) | ((https://a.yandex-team.ru/arc/commit/4289261 4289261)) | Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4268329 4268329))
Result revision: ((https://a.yandex-team.ru/arc/commit/4289261 4289261))
[][][] [diff-resolver:orepin]

Sandbox task: https://sandbox.yandex-team.ru/task/347271930/view
Task author: orepin@
Description: merge 4268329 to abt

  > .................................................................
  > INCLUDE: r4268329 ""|"" orepin ""|"" 2018-12-05 17:07:54 +0300 (Wed, 05 Dec 2018) ""|"" 3 lines
  >
  > Introduce rearrange rule for fast blender meta features (BLNDR-2939), related factors builder refactoring
  >
  > REVIEW: 629135
  > ................................................................. | ((https://sandbox.yandex-team.ru/task/347271930/view 347271930)) | merge ||\
"""


SampleComment = collections.namedtuple('SampleComment', ['before', 'after', 'header', 'rows'])

REPLACEMENT_SAMPLES = (
    SampleComment(
        before="====Merged revisions\n"
               "#|\n"
               "|| **Tag** | **Revisions merged** | **Branch revision** | **Revision info** | **Action** ||\n"
               "|| ((https://a.yandex-team.ru/arc/tags/upple/stable-250-1 stable-250-1)) |  | (("
               "https://a.yandex-team.ru/arc/commit/4388922 4388922)) | Merged as: (("
               "https://a.yandex-team.ru/arc/commit/4388922 4388922))\n "
               "[branch:upple] (r4388909, sandboxtask:370679507) | merge ||\n"
               "|| ((https://a.yandex-team.ru/arc/tags/upple/stable-250-2 stable-250-2)) | (("
               "https://a.yandex-team.ru/arc/commit/4389201 4389201)) | (("
               "https://a.yandex-team.ru/arc/commit/4389214 4389214)) | Merged as: (("
               "https://a.yandex-team.ru/arc/commit/4389214 4389214))\n "
               "Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4389201 4389201))\n"
               " [diff-resolver:panovav]\n"
               "Sandbox task: https://sandbox.yandex-team.ru/task/370717648/view\n"
               "Task author: robot-testenv@\n"
               "Description: noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/4389201 ("
               "4389201)   https://testenv.yandex-team.ru/?screen=job_history&amp;database=noapacheupper-trunk&amp"
               ";job_name=_UPPER_MERGE_TO_STABLE (TestEnv)\n "
               "  > .................................................................\n"
               "> INCLUDE: r4389201 \"\"|\"\" panovav \"\"|\"\" 2019-01-31 13:28:08 +0300 (Thu, 31 Jan 2019) "
               "\"\"|\"\" 3 lines\n "
               "  >\n"
               "  > [mergeto:upper]\n"
               "  >\n"
               "  > REVIEW: 696131\n"
               "  > ................................................................. | merge ||\n"
               "|#\n",
        after='====Merged revisions\n'
              '#|\n'
              '|| **Tag** | **Revisions merged** | **Branch revision** | **Revision info** | **Tickets** | **Action** ||'
              '\n'
              '|| ((https://a.yandex-team.ru/arc/tags/upple/stable-250-1 stable-250-1)) |  | (('
              'https://a.yandex-team.ru/arc/commit/4388922 4388922)) | Merged as: (('
              'https://a.yandex-team.ru/arc/commit/4388922 4388922))\n[branch:upple] (r4388909, '
              'sandboxtask:370679507) | RMDEV-1 | merge ||\n|| ((https://a.yandex-team.ru/arc/tags/upple/stable-250-2 '
              'stable-250-2)) | ((https://a.yandex-team.ru/arc/commit/4389201 4389201)) | (('
              'https://a.yandex-team.ru/arc/commit/4389214 4389214)) | Merged as: (('
              'https://a.yandex-team.ru/arc/commit/4389214 4389214))\nMerge from trunk: (('
              'https://a.yandex-team.ru/arc/commit/4389201 4389201))\n [diff-resolver:panovav]\nSandbox task: '
              'https://sandbox.yandex-team.ru/task/370717648/view\nTask author: robot-testenv@\nDescription: '
              'noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/4389201 (4389201)   '
              'https://testenv.yandex-team.ru/?screen=job_history&amp;database=noapacheupper-trunk&amp;job_name'
              '=_UPPER_MERGE_TO_STABLE (TestEnv)\n  > '
              '.................................................................\n  > INCLUDE: r4389201 "" | "" '
              'panovav "" | "" 2019-01-31 13:28:08 +0300 (Thu, 31 Jan 2019) "" | "" 3 lines\n  >\n  > ['
              'mergeto:upper]\n  >\n  > REVIEW: 696131\n  > '
              '................................................................. | RMDEV-11\nRMDEV-22 | merge ||\n|| (('
              'https://a.yandex-team.ru/arc/tags/upple/stable-250-3 stable-250-3)) | (('
              'https://a.yandex-team.ru/arc/commit/4389689 4389689)) | ((https://a.yandex-team.ru/arc/commit/4389704 '
              '4389704)) | Merged as: ((https://a.yandex-team.ru/arc/commit/4389704 4389704))\nMerge from trunk: (('
              'https://a.yandex-team.ru/arc/commit/4389689 4389689))\n [diff-resolver:platovd]\nSandbox task: '
              'https://sandbox.yandex-team.ru/task/370774057/view\nTask author: robot-testenv@\nDescription: '
              'noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/4389689 (4389689)   '
              'https://testenv.yandex-team.ru/?screen=job_history&amp;database=noapacheupper-trunk&amp;job_name'
              '=_UPPER_MERGE_TO_STABLE (TestEnv)\n  > '
              '.................................................................\n  > INCLUDE: r4389689 "" | "" '
              'platovd "" | "" 2019-01-31 15:10:32 +0300 (Thu, 31 Jan 2019) "" | "" 5 lines\n  >\n  > remove broken '
              'formulas from rd\n  >\n  > [mergeto:upper:250]\n  >\n  > REVIEW: 696723\n  > '
              '................................................................. |  | merge ||\n|#\n',
        header=rm_const.TicketGroups.TicketTableHeaders[rm_const.TicketGroups.MergedRevisions],
        rows=[
            [
                '((https://a.yandex-team.ru/arc/tags/upple/stable-250-1 stable-250-1))',
                '',
                '((https://a.yandex-team.ru/arc/commit/4388922 4388922))',
                'Merged as: ((https://a.yandex-team.ru/arc/commit/4388922 4388922))\n[branch:upple] (r4388909, '
                'sandboxtask:370679507)',
                'RMDEV-1',
                'merge',
            ],
            [
                '((https://a.yandex-team.ru/arc/tags/upple/stable-250-2 stable-250-2))',
                '((https://a.yandex-team.ru/arc/commit/4389201 4389201))',
                '((https://a.yandex-team.ru/arc/commit/4389214 4389214))',
                'Merged as: ((https://a.yandex-team.ru/arc/commit/4389214 4389214))\nMerge from trunk: (('
                'https://a.yandex-team.ru/arc/commit/4389201 4389201))\n [diff-resolver:panovav]\nSandbox task: '
                'https://sandbox.yandex-team.ru/task/370717648/view\nTask author: robot-testenv@\nDescription: '
                'noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/4389201 (4389201)   '
                'https://testenv.yandex-team.ru/?screen=job_history&amp;database=noapacheupper-trunk&amp;job_name'
                '=_UPPER_MERGE_TO_STABLE (TestEnv)\n  > '
                '.................................................................\n  > INCLUDE: r4389201 ""',
                '"" panovav ""',
                '"" 2019-01-31 13:28:08 +0300 (Thu, 31 Jan 2019) ""',
                '"" 3 lines\n  >\n  > [mergeto:upper]\n  >\n  > REVIEW: 696131\n  > '
                '.................................................................',
                'RMDEV-11\nRMDEV-22',
                'merge',
            ],
            [
                '((https://a.yandex-team.ru/arc/tags/upple/stable-250-3 stable-250-3))',
                '((https://a.yandex-team.ru/arc/commit/4389689 4389689))',
                '((https://a.yandex-team.ru/arc/commit/4389704 4389704))',
                'Merged as: ((https://a.yandex-team.ru/arc/commit/4389704 4389704))\nMerge from trunk: (('
                'https://a.yandex-team.ru/arc/commit/4389689 4389689))\n [diff-resolver:platovd]\nSandbox task: '
                'https://sandbox.yandex-team.ru/task/370774057/view\nTask author: robot-testenv@\nDescription: '
                'noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/4389689 (4389689)   '
                'https://testenv.yandex-team.ru/?screen=job_history&amp;database=noapacheupper-trunk&amp;job_name'
                '=_UPPER_MERGE_TO_STABLE (TestEnv)\n  > '
                '.................................................................\n  > INCLUDE: r4389689 ""',
                '"" platovd ""',
                '"" 2019-01-31 15:10:32 +0300 (Thu, 31 Jan 2019) ""',
                '"" 5 lines\n  >\n  > remove broken formulas from rd\n  >\n  > [mergeto:upper:250]\n  >\n  > REVIEW: '
                '696723\n  > .................................................................',
                '',
                'merge',
            ],
        ]
    ),
    SampleComment(
        before="Elephants\n",
        after="Elephants\n"
               "#|\n"
               "|| **My Elephants** ||\n"
               "|| Elephant 1 ||\n"
               "|| Elephant 2 ||\n"
               "|#",
        header=["My Elephants"],
        rows=[
            ["Elephant 1"],
            ["Elephant 2"],
        ],
    ),
    SampleComment(
        before="Elephants\n"
               "#|\n"
               "|| **My Elephants** ||\n"
               "|| Elephant 1 ||\n"
               "|| Elephant 2 ||\n"
               "|#",
        after="Elephants\n"
               "#|\n"
               "|| **My Elephants** ||\n"
               "|| John ||\n"
               "|| Paul ||\n"
               "|| George ||\n"
               "|| Ringo ||\n"
               "|#",
        header=["My Elephants"],
        rows=[
            ["John"],
            ["Paul"],
            ["George"],
            ["Ringo"],
        ],
    ),
)

APPEND_SAMPLES = (
    SampleComment(
        before="Elephants\n"
               "#|\n"
               "|| **My Elephants** ||\n"
               "|| Elephant 1 ||\n"
               "|| Elephant 2 ||\n"
               "|#",
        after="Elephants\n"
               "#|\n"
               "|| **My Elephants** ||\n"
               "|| Elephant 1 ||\n"
               "|| Elephant 2 ||\n"
               "|| Elephant 3 ||\n"
               "|| Elephant 4 ||\n"
               "|#",
        header=["My Elephants"],
        rows=[
            ["Elephant 3"],
            ["Elephant 4"],
        ],
    ),
)

UPDATE_ROWS_SAMPLES = (
    SampleComment(
        before="Elephants\n"
               "#|\n"
               "|| **ID** |  **Title** ||\n"
               "|| 1 | Elephant 1 ||\n"
               "|| 2 | Elephant 2 ||\n"
               "|#",
        after="Elephants\n"
               "#|\n"
               "|| **ID** |  **Title** ||\n"
               "|| 1 | First Elephant ||\n"
               "|| 2 | Second Elephant ||\n"
               "|#",
        header=["ID", "Title"],
        rows=[
            ["1", "First Elephant"],
            ["2", "Second Elephant"],
        ],
    ),
)


class UpdateGroupedTableTests(unittest.TestCase):
    CASES = [(
        TABLE_BEFORE_1,
        ROW_TO_ADD,
        TABLE_AFTER_1,
    )]

    def testGoodCases(self):
        for table_before, row, answer in self.CASES:
            self.assertEqual(wiki_helper.insert_or_update_row_in_table(table_before, row, 1), answer)

    def test_table_replacement_in_comment(self):
        for index, sample in enumerate(REPLACEMENT_SAMPLES):
            new_comment = wiki_helper.replace_table_in_text(sample.before, sample.header, sample.rows)
            self.assertEqual(
                sample.after,
                new_comment,
                "Table wasn't replaced correctly in sample #{}".format(index)
            )

    def test_table_rows_appending_in_comment(self):
        for index, sample in enumerate(APPEND_SAMPLES):
            new_comment = wiki_helper.append_table_rows_in_text(sample.before, sample.header, sample.rows)
            self.assertEqual(
                sample.after,
                new_comment,
                "Rows weren't appended correctly in sample #{}".format(index)
            )

    def test_split_and_update_table(self):
        for index, sample in enumerate(UPDATE_ROWS_SAMPLES):
            new_comment = wiki_helper.split_and_update_table(sample.before, sample.header, sample.rows, 0)
            self.assertEqual(
                sample.after,
                new_comment,
                "Table wasn't updated correctly in sample #{}".format(index)
            )


if __name__ == '__main__':
    unittest.main()
