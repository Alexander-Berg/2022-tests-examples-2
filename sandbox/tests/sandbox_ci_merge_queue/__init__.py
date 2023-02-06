# -*- coding: utf-8 -*-

import unittest
import mock
from sandbox.projects.sandbox_ci.tests import MagicMock, MemoizeStageMock
from sandbox.projects.sandbox_ci.sandbox_ci_merge_queue import SandboxCiMergeQueue
from sandbox.sdk2 import WaitTask
from sandbox.projects.sandbox_ci.tests import DotDict
from sandbox.common.types import task as ctt


class BeforeEach:
    class Context:
        profiler_actions = []
        project_git_base_commit = 1
        project_git_head_commit = 2
        project_git_tree_hash = 3
        project_task_id = 4
        arc_tree_hash = 5

    class Parameters:
        use_arc = False

    profiler = DotDict({
        'actions': DotDict({
            'run_required_checks': MagicMock(),
        }),
    })
    memoize_stage_on_base_commit = MemoizeStageMock()
    register_cache_waiting_action = MagicMock()
    get_project_task = MagicMock()
    get_cache_fail_reason = MagicMock()
    register_cache_task_miss = MagicMock()
    register_cache_task_hit = MagicMock()
    check_passed_required_checks = MagicMock(return_value=True)

    def use_arc(self):
        return False


class TestRunRequiredChecks(BeforeEach, unittest.TestCase):
    wait_project_task = MagicMock(side_effect=WaitTask(1, 2, 3))
    set_info = MagicMock()
    get_info_message_about_project_task = MagicMock()
    config = {
        'projectTask': {
            'type': 'PROJECT_TYPE'
        }
    }

    def test_cache_not_found(self):
        """Should run project task if cache task not found"""
        self.has_cache_been_used = MagicMock(return_value=False)
        self.find_project_task_cache = MagicMock(return_value=None)
        self.run_project_task = MagicMock(return_value={'id': 1})

        with self.assertRaises(WaitTask):
            SandboxCiMergeQueue.run_required_checks.im_func(self)

        self.wait_project_task.assert_called_with({'id': 1})

    def test_cache_found(self):
        """Should wait cache task if cache task found"""
        self.has_cache_been_used = MagicMock(return_value=True)
        self.find_project_task_cache = MagicMock(return_value={'id': 2})
        self.run_project_task = MagicMock(return_value={'id': 1})

        with self.assertRaises(WaitTask):
            SandboxCiMergeQueue.run_required_checks.im_func(self)

        self.wait_project_task.assert_called_with({'id': 2})


class TestPollRequiredChecks(BeforeEach, unittest.TestCase):
    poll_required_checks = MagicMock(return_value=None)
    config = {
        'poll': {
            'attemptDelay': 30000,
            'maxRetries': 60
        }
    }
    Context = DotDict({
        'project_git_head_commit': '<project_git_head_commit>'
    })

    def test_cache_not_found(self):
        """Should run poll_required_checks"""
        SandboxCiMergeQueue.run_required_checks.im_func(self)

        self.poll_required_checks.assert_called_with('<project_git_head_commit>')


class TestHasCachedBeenUsed(BeforeEach, unittest.TestCase):
    def test_if_not_task(self):
        """Should return False if cache task not found"""
        self.assertFalse(SandboxCiMergeQueue.has_cache_been_used.im_func(self, None))

    def test_if_task_failed(self):
        """Should return True if cache task is failed"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.EXCEPTION,
            'Parameters': DotDict({
                'project_tree_hash': 3,
                'use_arc': False
            }),
        })

        self.assertTrue(SandboxCiMergeQueue.has_cache_been_used.im_func(self, cache_task))

    def test_if_tree_hashes_differ(self):
        """Should return False if tree hashes differ"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.SUCCESS,
            'Parameters': DotDict({
                'project_tree_hash': 2,
                'use_arc': False
            }),
        })

        self.assertFalse(SandboxCiMergeQueue.has_cache_been_used.im_func(self, cache_task))

    def test_if_tree_hashes_are_the_same(self):
        """Should return True if success cache found with the same tree hash"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.SUCCESS,
            'Parameters': DotDict({
                'project_tree_hash': 3,
                'use_arc': False
            }),
        })

        self.assertTrue(SandboxCiMergeQueue.has_cache_been_used.im_func(self, cache_task))

    def test_required_checks_are_ok(self):
        """Should return False if check_passed_required_checks returns False"""
        self.check_passed_required_checks = MagicMock(return_value=False)
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.SUCCESS,
            'Parameters': DotDict({
                'project_tree_hash': 3,
                'use_arc': False
            }),
        })
        self.assertFalse(SandboxCiMergeQueue.has_cache_been_used.im_func(self, cache_task))


class TestPassedCacheRequiredChecks(BeforeEach, unittest.TestCase):
    config = {
        'requiredChecks': [u'привет, мир', u'bar'],
    }

    @mock.patch('sandbox.projects.sandbox_ci.sandbox_ci_merge_queue.logging')
    def test_all_required_checks_are_ok(self, mock_logging):
        """Should return True if all required checks passed"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.FAILURE,
            'Parameters': DotDict({
                'project_tree_hash': 3,
            }),
            'Context': DotDict({
                'github_statuses': [
                    {'state': 'success', 'context': u'привет, мир'},
                    {'state': 'success', 'context': u'bar'},
                ],
            }),
        })
        self.assertTrue(SandboxCiMergeQueue.check_passed_required_checks.im_func(self, cache_task))
        mock_logging.debug.assert_any_call('Got github statuses of cache_task: {}'.format(
            cache_task.Context.github_statuses,
        ))
        mock_logging.debug.assert_any_call('All required checks in cache task passed: {}'.format(
            self.config['requiredChecks'],
        ))

    @mock.patch('sandbox.projects.sandbox_ci.sandbox_ci_merge_queue.logging')
    def test_one_required_check_is_not_ok(self, mock_logging):
        """Should return False if one of the required checks failed"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.FAILURE,
            'Parameters': DotDict({
                'project_tree_hash': 3,
                'use_arc': False
            }),
            'Context': DotDict({
                'github_statuses': [
                    {'state': 'failed', 'context': u'привет, мир'},
                    {'state': 'success', 'context': u'bar'},
                ],
            }),
        })
        self.assertFalse(SandboxCiMergeQueue.check_passed_required_checks.im_func(self, cache_task))
        mock_logging.debug.assert_any_call('привет, мир is required to be success but failed found')

    def test_empty_required_checks(self):
        """Should return False in case of empty required checks"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.FAILURE,
            'Parameters': DotDict({
                'project_tree_hash': 3,
            }),
            'Context': DotDict({
                'github_statuses': [
                    {'state': 'failed', 'context': u'привет, мир'},
                    {'state': 'success', 'context': u'bar'},
                ],
            }),
        })
        self.config = {
            'requiredChecks': [],
        }
        self.assertFalse(SandboxCiMergeQueue.check_passed_required_checks.im_func(self, cache_task))

    def test_not_exist_github_statuses(self):
        """Should return False in case of not exist github statuses in Context"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.FAILURE,
            'Parameters': DotDict({
                'project_tree_hash': 3,
                'use_arc': False
            }),
            'Context': DotDict({}),
        })
        self.assertFalse(SandboxCiMergeQueue.check_passed_required_checks.im_func(self, cache_task))


class TestGetCacheFailReason(BeforeEach, unittest.TestCase):
    def test_if_not_task(self):
        """Should return 'Not found' if cache task not found"""
        expected = 'Not found'

        actual = SandboxCiMergeQueue.get_cache_fail_reason.im_func(self, None)

        self.assertEqual(actual, expected)

    def test_if_task_failed_with_statuses(self):
        """Should return 'Failed steps: []' if cache task is failed"""
        self.get_failed_github_statuses = MagicMock(return_value=[])

        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.FAILURE,
            'Context': DotDict({
                'github_statuses': [{'state': 'success', 'context': 'foo'}],
            }),
        })

        expected = 'Failed'

        actual = SandboxCiMergeQueue.get_cache_fail_reason.im_func(self, cache_task)

        self.assertEqual(actual, expected)

    def test_if_task_failed_without_statuses(self):
        """Should return 'Failed' if cache task is failed"""
        self.get_failed_github_statuses = MagicMock(return_value=['[Sandbox CI] Failed status'])

        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.FAILURE,
            'Context': DotDict({
                'github_statuses': [{'state': 'success', 'context': 'foo'}],
            }),
        })

        expected = 'Failed steps: [Sandbox CI] Failed status'

        actual = SandboxCiMergeQueue.get_cache_fail_reason.im_func(self, cache_task)

        self.assertEqual(actual, expected)

    def test_if_tree_hashes_differ(self):
        """Should return 'Tree hash does not match' if tree hashes differ"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.SUCCESS,
            'Parameters': DotDict({
                'project_tree_hash': 2,
                'use_arc': False
            }),
            'Context': DotDict({
                'github_statuses': [{'state': 'success', 'context': 'foo'}],
            }),
        })

        expected = 'Tree hash does not match'

        actual = SandboxCiMergeQueue.get_cache_fail_reason.im_func(self, cache_task)

        self.assertEqual(actual, expected)

    def test_broken(self):
        """Should return 'Broken' if reason is not revealed"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.EXCEPTION,
            'Parameters': DotDict({
                'project_tree_hash': 3,
                'use_arc': False
            }),
            'Context': DotDict({
                'github_statuses': [{'state': 'success', 'context': 'foo'}],
            }),
        })

        expected = 'Broken'

        actual = SandboxCiMergeQueue.get_cache_fail_reason.im_func(self, cache_task)

        self.assertEqual(actual, expected)

    def test_if_task_failed_without_github_statuses(self):
        """Should return 'Failed' if cache task has no github statuses in Context"""
        cache_task = DotDict({
            'id': 1,
            'status': ctt.Status.SUCCESS,
            'Context': DotDict({}),
        })

        expected = 'There is no github statuses in cache task'

        actual = SandboxCiMergeQueue.get_cache_fail_reason.im_func(self, cache_task)

        self.assertEqual(actual, expected)


class TestSetInfoCacheMessage(BeforeEach, unittest.TestCase):
    wait_project_task = MagicMock(side_effect=WaitTask(1, 2, 3))
    run_project_task = MagicMock(return_value={'id': 1})
    config = {
        'projectTask': {
            'type': 'PROJECT_TYPE'
        }
    }

    def test_cache_found(self):
        """Should call set_info if cache found"""
        self.has_cache_been_used = MagicMock(return_value=True)
        self.find_project_task_cache = MagicMock(return_value={'id': 1})
        self.set_info = MagicMock()
        self.get_info_message_about_project_task = MagicMock(return_value="foo")

        with self.assertRaises(WaitTask):
            SandboxCiMergeQueue.run_required_checks.im_func(self)

        self.get_info_message_about_project_task.assert_called_with(1, True)
        self.set_info.assert_called_with("foo", do_escape=False)

    def test_cache_not_found(self):
        """Should not call set_info if cache not found"""
        self.has_cache_been_used = MagicMock(return_value=False)
        self.find_project_task_cache = MagicMock(return_value=None)
        self.set_info = MagicMock()
        self.get_info_message_about_project_task = MagicMock(return_value="bar")

        with self.assertRaises(WaitTask):
            SandboxCiMergeQueue.run_required_checks.im_func(self)

        self.get_info_message_about_project_task.assert_called_with(1, False)
        self.set_info.assert_called_with("bar", do_escape=False)
