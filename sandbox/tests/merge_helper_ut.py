# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.release_machine.helpers import merge_helper
from sandbox.projects.release_machine import arc_helper


class MergetoParserTests(unittest.TestCase):
    allowed_components = ['base', 'upper', 'release_machine_test']
    GOOD_CASES = [
        (
            '[mergeto:release_machine_test:100], [mergeto:base;upper]',
            {'release_machine_test': ['100'], 'base': [], 'upper': []}
        ),
        (
            '[mergeto:release_machine_test:100,200], [mergeto:base;upper:32]',
            {'release_machine_test': ['100', '200'], 'base': [], 'upper': ['32']}
        ),
        (
            '[mergeto:base]',
            {'base': []}
        ),
        (
            '[mergeto:base:100,+]',
            {'base': ['100', '+']}
        ),
        (
            '[mergeto:base:100,+;upper:200,+]',
            {'base': ['100', '+'], 'upper': ['200', '+']}
        ),
    ]

    def testGoodCases(self):
        for input_data, required_out in self.GOOD_CASES:
            out = merge_helper.parse_mergeto(input_data, self.allowed_components)
            out_keys = set(out.keys())
            required_out_keys = set(required_out.keys())
            self.assertFalse(
                out_keys ^ required_out_keys,
                "Different component names found: {} != {}".format(out_keys, required_out_keys)
            )
            for name, vals_list in out.iteritems():
                vals = set(vals_list)
                required_vals = set(required_out[name])
                self.assertFalse(
                    vals ^ required_vals,
                    "Different branches found for '{}': {} != {}".format(name, vals, required_vals)
                )

    @unittest.expectedFailure
    def testBadCase1(self):
        input_data = '[mergeto:100base]'
        result = merge_helper.parse_mergeto(input_data, self.allowed_components)
        print "\nInput data: '{}'. Unexpected success:".format(input_data)
        print result

    @unittest.expectedFailure
    def testBadCase2(self):
        input_data = '[mergeto:aaaaa]'
        result = merge_helper.parse_mergeto(input_data, self.allowed_components)
        print "\nInput data: '{}'. Unexpected success:".format(input_data)
        print result

    @unittest.expectedFailure
    def testBadCase3(self):
        input_data = '[mergeto:;base]'
        result = merge_helper.parse_mergeto(input_data, self.allowed_components)
        print "\nInput data: '{}'. Unexpected success:".format(input_data)
        print result

    @unittest.expectedFailure
    def testBadCase4(self):
        input_data = '[mergeto:base:120,+,1]'
        result = merge_helper.parse_mergeto(input_data, self.allowed_components)
        print "\nInput data: '{}'. Unexpected success:".format(input_data)
        print result

    @unittest.expectedFailure
    def testBadCase5(self):
        input_data = '[mergeto:base:+,+]'
        result = merge_helper.parse_mergeto(input_data, self.allowed_components)
        print "\nInput data: '{}'. Unexpected success:".format(input_data)
        print result


class CommonPathTests(unittest.TestCase):
    DIFF_PATHS = [
        ([
            ('M', '/trunk/arcadia/search/garden/sandbox-tasks/RollbackCommit/__init__.py'),
            ('M', '/trunk/arcadia/search/garden/sandbox-tasks/common/release_machine/const.py'),
            ('M', '/trunk/arcadia/search/garden/sandbox-tasks/release_machine_tasks/CreateBranchOrTag/__init__.py'),
            ('M', '/trunk/arcadia/search/garden/sandbox-tasks/release_machine_tasks/LogMergesInStartrek/__init__.py'),
            ('M', '/trunk/arcadia/search/garden/sandbox-tasks/release_machine_tasks/MergeToStable/__init__.py'),
        ], '/'.join(['', 'trunk', 'arcadia', 'search', 'garden', 'sandbox-tasks'])),
        ([
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/HaasDiscover'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/HaasDiscover/CMakeLists.txt'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/HaasDiscover/__init__.py'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/__init__.py'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/common'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/common/__init__.py'),
            ('A', '/trunk/arcadia/search/garden/sandbox-tasks/projects/Haas/common/clients.py'),
        ], '/'.join(['', 'trunk', 'arcadia', 'search', 'garden', 'sandbox-tasks', 'projects'])),
    ]

    def testMaxCommonPath(self):
        for paths, required_out in self.DIFF_PATHS:
            diff_items = merge_helper.prepare_diff_items(paths)
            max_common_path = '/'.join(merge_helper.get_max_common_path(diff_items))
            self.assertEqual(
                max_common_path, required_out,
                'Different paths: {} != {}'.format(max_common_path, required_out)
            )


class RevExtractingTests(unittest.TestCase):
    def testRevExtraction1(self):
        revs = "1000000, r2000000 , 3100000   4000000.3000000;6000000 @6661111"
        out = arc_helper.extract_revisions(revs, arc_client=None).result
        required_out = [1000000, 2000000, 3000000, 3100000, 4000000, 6000000, 6661111]
        self.assertEqual(out, required_out, "{} != {}".format(out, required_out))

    def testRevExtraction2(self):
        revs = u"1234567"
        out = arc_helper.extract_revisions(revs, arc_client=None).result
        required_out = [1234567]
        self.assertEqual(out, required_out, "{} != {}".format(out, required_out))

    @unittest.expectedFailure
    def testRevExtraction3(self):
        revs = u"1234фыв"
        self.assertTrue(arc_helper.extract_revisions(revs, arc_client=None).ok)

    @unittest.expectedFailure
    def testRevExtraction4(self):
        revs = "1234фыв"
        self.assertTrue(arc_helper.extract_revisions(revs, arc_client=None).ok)

    @unittest.expectedFailure
    def testRevExtraction5(self):
        revs = "1234, ast, 43"
        self.assertTrue(arc_helper.extract_revisions(revs, arc_client=None).ok)


class MessageParsingTest(unittest.TestCase):
    MERGE_MESSAGES = [
        # Message with single revision and prefix
        (
            """
            Merge from trunk: r3975947\n[] [diff-resolver:mesherin]\n\n
            Sandbox task: http://sandbox.yandex-team.ru/task/302760729/view\nTask author: robot-testenv@\n
            Description: noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/3975947 (3975947)
            """,
            [3975947],
        ),
        # Message with multiple revisions with prefixes
        (
            """
            Merge from trunk: r3953467, r3953481, r3953840, r3953867\n[] [diff-resolver:osidorkin]\n\n
            Sandbox task: http://sandbox.yandex-team.ru/task/299135311/view\nTask author: osidorkin@\n
            Description: Merge docfetcher fixes
            """,
            [3953467, 3953481, 3953840, 3953867],
        ),
        # Message with multiple revisions with prefixes
        (
            """
            Merge   from trunk: r3953467,   r3953481, r3953840,r3953867\n[] [diff-resolver:osidorkin]\n\n
            Sandbox task: http://sandbox.yandex-team.ru/task/299135311/view\nTask author: osidorkin@\n
            Description: Merge docfetcher fixes
            """,
            [3953467, 3953481, 3953840, 3953867],
        ),
        # Message with single revision without prefix
        (
            """
            Merge from trunk: 3961756\n\n  > .................................................................\n  >
            """,
            [3961756],
        ),
        # Message with multiple revisions without prefixes
        (
            """
            Merge from trunk: 3961756, 3953481\n\n  > ................................................\n  >
            """,
            [3961756, 3953481],
        ),
        # Message with multiple revisions without prefixes
        (
            """
            Merge from trunk  : 3961756,   3953481,3953484\n\n  > ................................................\n  >
            """,
            [3961756, 3953481, 3953484],
        ),
        # Message without merge info
        ("Change options", []),
    ]
    ROLLBACK_MESSAGES = [
        # Message with single revision and prefix
        (
            """
            Rollback: r3975947\n[] [diff-resolver:mesherin]\n\n
            Sandbox task: http://sandbox.yandex-team.ru/task/302760729/view\nTask author: robot-testenv@\n
            Description: noapacheupper-trunk: _UPPER_MERGE_TO_STABLE  https://a.yandex-team.ru/commit/3975947 (3975947)
            """,
            [3975947],
        ),
        # Message with multiple revisions with prefixes
        (
            """
            Rollback: r3953467, r3953481, r3953840, r3953867\n[] [diff-resolver:osidorkin]\n\n
            Sandbox task: http://sandbox.yandex-team.ru/task/299135311/view\nTask author: osidorkin@\n
            Description: Merge docfetcher fixes
            """,
            [3953467, 3953481, 3953840, 3953867],
        ),
        # Message with multiple revisions with prefixes
        (
            """
            Rollback  : r3953467,   r3953481, r3953840,r3953867\n[] [diff-resolver:osidorkin]\n\n
            Sandbox task: http://sandbox.yandex-team.ru/task/299135311/view\nTask author: osidorkin@\n
            Description: Merge docfetcher fixes
            """,
            [3953467, 3953481, 3953840, 3953867],
        ),
        # Message with single revision without prefix
        (
            """
            Rollback: 3961756\n\n  > .................................................................\n  >
            """,
            [3961756],
        ),
        # Message with multiple revisions without prefixes
        (
            """
            Rollback: 3961756, 3953481\n\n  > ................................................\n  >
            """,
            [3961756, 3953481],
        ),
        # Message with multiple revisions without prefixes
        (
            """
            Rollback   : 3961756,   3953481,3953485\n\n  > ................................................\n  >
            """,
            [3961756, 3953481, 3953485],
        ),
        # Message without merge info
        ("Change options", []),
    ]
    MERGE_MESSAGES_ARC = [
        # Message with single arc commit
        (
            """
            Merge from trunk: 01b48d21efbc775d2b8eaddd7598c23923d7db88\n\n  > ..............................\n  >
            """,
            ["01b48d21efbc775d2b8eaddd7598c23923d7db88"],
        ),
        # Message with multiple arc commits
        (
            """
            Merge from trunk: 01b48d21efbc775d2b8eaddd7598c23923d7db88, a7b15133e97fabe077e8c2aa46d52a257a455d81\n\n>\n>
            """,
            ["01b48d21efbc775d2b8eaddd7598c23923d7db88", "a7b15133e97fabe077e8c2aa46d52a257a455d81"],
        ),
        # Message with multiple arc commits
        (
            """
            Merge from trunk  : 01b48d21efbc775d2b8eaddd7598c23923d7db88,   a7b15133e97fabe077e8c2aa46d52a257a455d81\n\n
            """,
            ["01b48d21efbc775d2b8eaddd7598c23923d7db88", "a7b15133e97fabe077e8c2aa46d52a257a455d81"],
        ),
    ]
    ROLLBACK_MESSAGES_ARC = [
        # Message with single arc commit
        (
            """
            Rollback: a7b15133e97fabe077e8c2aa46d52a257a455d81\n\n  > ...................\n  >
            """,
            ["a7b15133e97fabe077e8c2aa46d52a257a455d81"],
        ),
        # Message with multiple arc commits
        (
            """
            Rollback: a7b15133e97fabe077e8c2aa46d52a257a455d81, 4189b018085a2a57bf4206f005b8f38aa1553198\n\n  > ...\n  >
            """,
            ["a7b15133e97fabe077e8c2aa46d52a257a455d81", "4189b018085a2a57bf4206f005b8f38aa1553198"],
        ),
        # Message with multiple arc commits
        (
            """
            Rollback   : 4189b018085a2a57bf4206f005b8f38aa1553198,   0b885321ca09be983a6b0e457f4d2d564096b7ca\n\n  > \n>
            """,
            ["4189b018085a2a57bf4206f005b8f38aa1553198", "0b885321ca09be983a6b0e457f4d2d564096b7ca"],
        ),
    ]
    CHERRY_PICK_MESSAGES_ARC = [
        (
            """
            Add functions for parsing commit messages with arc hashes [RMDEV-1634]\n\n
            REVIEW: 1271774\n\n(cherry picked from commit fc61e74cc4428630b76824372226a5a5ef9ac933)
            """,
            ["fc61e74cc4428630b76824372226a5a5ef9ac933"],
        )
    ]
    REVERT_MESSAGES_ARC = [
        (
            """
            Revert "Merge from trunk: fc61e74cc4428630"\n\nThis reverts commit 94f725a903fe0e0f72a1eb8ff2b507bee8261951.
            """,
            ["94f725a903fe0e0f72a1eb8ff2b507bee8261951"],
        )
    ]

    def testMergesParsing(self):
        for message, expected_answer in self.MERGE_MESSAGES:
            parsed_revisions = merge_helper.get_merges_from_commit_message(message)
            self.assertEqual(
                parsed_revisions,
                expected_answer,
                "Different parsed revisions: {} != {}".format(parsed_revisions, expected_answer),
            )

        for message, expected_answer in self.ROLLBACK_MESSAGES:
            parsed_revisions = merge_helper.get_rollbacks_from_commit_message(message)
            self.assertEqual(
                parsed_revisions,
                expected_answer,
                "Different parsed revisions: {} != {}".format(parsed_revisions, expected_answer),
            )

        for message, expected_answer in self.MERGE_MESSAGES_ARC:
            parsed_hashes = merge_helper.get_arc_merges_from_commit_message(message)
            self.assertEqual(
                parsed_hashes,
                expected_answer,
                "Different parsed arc hashes: {} != {}".format(parsed_hashes, expected_answer),
            )

        for message, expected_answer in self.ROLLBACK_MESSAGES_ARC:
            parsed_hashes = merge_helper.get_arc_rollbacks_from_commit_message(message)
            self.assertEqual(
                parsed_hashes,
                expected_answer,
                "Different parsed arc hashes: {} != {}".format(parsed_hashes, expected_answer),
            )

        for message, expected_answer in self.CHERRY_PICK_MESSAGES_ARC:
            parsed_hashes = merge_helper.get_arc_cherry_pick_from_commit_message(message)
            self.assertEqual(
                parsed_hashes,
                expected_answer,
                "Different parsed arc hashes: {} != {}".format(parsed_hashes, expected_answer),
            )

        for message, expected_answer in self.REVERT_MESSAGES_ARC:
            parsed_hashes = merge_helper.get_arc_revert_from_commit_message(message)
            self.assertEqual(
                parsed_hashes,
                expected_answer,
                "Different parsed arc hashes: {} != {}".format(parsed_hashes, expected_answer),
            )


CASE1 = """Merge from trunk: r3953467, r3953481, r3953840, r3953867
[diff-resolver:osidorkin]

Sandbox task: http://sandbox.yandex-team.ru/task/299135311/view
Task author: osidorkin@
Description: Merge docfetcher fixes"""

ANSWER1 = """Merged as: ((https://a.yandex-team.ru/arc/commit/3953900 3953900))
Merge from trunk: ((https://a.yandex-team.ru/arc/commit/3953467 3953467)), \
((https://a.yandex-team.ru/arc/commit/3953481 3953481)), \
((https://a.yandex-team.ru/arc/commit/3953840 3953840)), \
((https://a.yandex-team.ru/arc/commit/3953867 3953867))
[diff-resolver:osidorkin]

Sandbox task: http://sandbox.yandex-team.ru/task/299135311/view
Task author: osidorkin@
Description: Merge docfetcher fixes"""

CASE2 = """My merge"""

ANSWER2 = """\
Merged as: ((https://a.yandex-team.ru/arc/commit/3953900 3953900))
My merge"""

CASE3 = """\
Merge from trunk: r4999999
Fix"""

ANSWER3 = """\
Merged as: ((https://a.yandex-team.ru/arc/commit/5000000 5000000))
Merge from trunk: ((https://a.yandex-team.ru/arc/commit/4999999 4999999))
Fix"""


class CheckUpdateMessageTests(unittest.TestCase):
    CASES = [
        (
            [
                CASE1,
                3953900,
            ],
            ANSWER1,
        ),
        (
            [
                CASE2,
                3953900,
            ],
            ANSWER2,
        ),
        (
            [
                CASE3,
                5000000,
            ],
            ANSWER3,
        )

    ]

    def testGoodCases(self):
        for case, answer in self.CASES:
            self.assertMultiLineEqual(merge_helper.update_message(case[0], case[1])[0], answer)


class CheckGetMaxCommonPathTests(unittest.TestCase):
    replaced_paths = [
        ('R', '/trunk/arcadia/sandbox/projects/antiadblock/aab_monitoring'),
        ('A', '/trunk/arcadia/sandbox/projects/antiadblock/aab_monitoring/__init__.py'),
        ('A', '/trunk/arcadia/sandbox/projects/antiadblock/aab_monitoring/job.py'),
        ('A', '/trunk/arcadia/sandbox/projects/antiadblock/aab_monitoring/ya.make'),
    ]
    prepared_replaced_paths = merge_helper.prepare_diff_items(replaced_paths)
    prep_replaced_paths_answers = ['', 'trunk', 'arcadia', 'sandbox', 'projects', 'antiadblock']

    added_paths = [
        ('A', '/trunk/arcadia/sandbox/projects/antiadblock/aab_deploy_cryprox'),
        ('A', '/trunk/arcadia/sandbox/projects/antiadblock/aab_deploy_cryprox/__init__.py'),
        ('A', '/trunk/arcadia/sandbox/projects/antiadblock/aab_deploy_cryprox/ya.make'),
        ('A', '/trunk/arcadia/testenv/jobs/antiadblock_cryprox_docker/DeployCryprox.yaml'),
    ]

    prepared_added_paths = merge_helper.prepare_diff_items(added_paths)
    prep_added_paths_answers = ['', 'trunk', 'arcadia']

    CASES = [
        (prepared_replaced_paths, prep_replaced_paths_answers),
        (prepared_added_paths, prep_added_paths_answers),
    ]

    def testGoodCases(self):
        for case, answer in self.CASES:
            self.assertEqual(merge_helper.get_max_common_path(case), answer)


if __name__ == '__main__':
    unittest.main()
