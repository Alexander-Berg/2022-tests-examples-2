from __future__ import annotations

import threading
from typing import Union
from unittest import mock

from django import test
from django.db import connection

from .. import utils


def _call(fn, arg):
    try:
        return fn(arg)
    finally:
        connection.close()


class BaseTestCases:
    class _BaseTest(test.TestCase):
        decorator = None
        context_manager = None
        test_different_threads_decorator_result = None

        def setUp(self) -> None:
            self.assertIsNotNone(self.decorator)
            self.assertIsNotNone(self.context_manager)

            self.guarded_key: str = self.id()
            self.other_guard_key: str = f"another_{self.id()}"
            self.assertNotEqual(self.guarded_key, self.other_guard_key)
            self.called: set[Union[int, bool]] = set()

        def test_timeout_passed(self):
            with self.context_manager(self.guarded_key, 10) as res:
                self.assertTrue(res)

        def test_timeout_not_passed(self):
            with self.context_manager(self.guarded_key, 10) as res:
                self.assertTrue(res)
                with self.context_manager(self.guarded_key, 10) as inner_res:
                    self.assertFalse(inner_res)

        def test_timeout_passed_for_another(self):
            with self.context_manager(self.guarded_key, 100) as res:
                self.assertTrue(res)
                with mock.patch.object(self.context_manager, "_lock", mock.Mock(return_value=True)):
                    with self.context_manager(self.guarded_key, 10) as inner_res:
                        self.assertTrue(inner_res)

        def test_different_keys(self):
            with self.context_manager(self.guarded_key, 15) as res:
                self.assertTrue(res)
                with self.context_manager(self.other_guard_key, 15) as inner_res:
                    self.assertTrue(inner_res)

        def test_different_threads(self):
            b = threading.Barrier(3)

            def thread_function1(res):
                with self.context_manager(self.guarded_key, 10) as r:
                    b.wait(5)
                    res.add(r)

            def thread_function2(res):
                with self.context_manager(self.guarded_key, 10) as r:
                    b.wait(5)
                    res.add(r)

            first: threading.Thread = threading.Thread(target=_call, args=(thread_function1, self.called))
            second: threading.Thread = threading.Thread(target=_call, args=(thread_function2, self.called))
            first.start()
            second.start()
            b.wait(5)
            first.join()
            second.join()
            self.assertSetEqual({True, False}, self.called)

        def test_timeout_passed_decorator(self):
            @self.decorator(self.guarded_key, 10)
            def test_func(c):
                c.add(1)

            test_func(self.called)

            self.assertSetEqual({1}, self.called)

        def test_timeout_not_passed_decorator(self):
            @self.decorator(self.guarded_key, 10)
            def test_func(c):
                c.add(1)

            @self.decorator(self.guarded_key, 15)
            def test_another(c):
                c.add(2)
                test_func(c)

            test_another(self.called)

            self.assertSetEqual({2}, self.called)

        def test_timeout_passed_for_another_decorator(self):
            @self.decorator(self.guarded_key, 10)
            def test_func(c: list[int]):
                c.append(1)

            @self.decorator(self.guarded_key, 10)
            def test_another(c: list[int]):
                with mock.patch.object(self.decorator, "_lock", mock.Mock(return_value=True)):
                    c.append(2)
                    test_func(c)

            called: list[int] = []
            test_another(called)
            self.assertListEqual([2, 1], called)

        def test_different_keys_decorator(self):
            @self.decorator(self.guarded_key, 15)
            def test_func(c: list[int]):
                c.append(1)

            @self.decorator(self.other_guard_key, 15)
            def test_another(c: list[int]):
                c.append(2)
                test_func(c)

            called: list[int] = []
            test_another(called)

            self.assertListEqual([2, 1], called)

        def test_different_threads_decorator(self):
            b = threading.Barrier(2)

            # Так как барьер в конце функции, а убираем лок в декораторе - мы можем
            # попасть в момент когда барьер уже пройден, но лок ещё не отпущен.
            def test_func(c):
                @self.decorator(self.guarded_key, 300)
                def test_inner(c) -> None:
                    c.add(1)

                test_inner(c)
                pass_guard = b.wait(5)
                self.assertGreater(pass_guard, 0, "Verify that barrier arrived from inside of locked call")

            @self.decorator(self.guarded_key, 300)
            def test_another(c) -> None:
                c.add(2)

            first: threading.Thread = threading.Thread(target=_call, args=(test_func, self.called))
            second: threading.Thread = threading.Thread(target=_call, args=(test_another, self.called))
            first.start()
            pass_guard = b.wait(5)
            self.assertEqual(pass_guard, 0, "Verify that barrier arrived from outside of locked call")
            # Asserts that first invocation is successful
            self.assertEqual(self.called, {1})
            second.start()
            first.join(timeout=10)
            second.join(timeout=10)
            # Asserts that all threads are done
            self.assertFalse(first.isAlive())
            self.assertFalse(second.isAlive())

            # NOTE: due to diff in behaviour - after successful run - lock_for_execution
            # unlocks the lock and allows execution.
            self.assertSetEqual(self.test_different_threads_decorator_result, self.called)

        def test_raise_do_not_skip_decorator(self):
            @self.decorator(self.guarded_key, 15)
            def test_func(c):
                c.add(1)
                raise RuntimeError

            @utils.check_timeout_passed(self.guarded_key, 15)
            def test_another(c):
                c.add(2)

            with self.assertRaises(RuntimeError):
                test_func(self.called)
            test_another(self.called)

            self.assertSetEqual({1, 2}, self.called)


class TestCheckTimeoutPassed(BaseTestCases._BaseTest):
    decorator = utils.check_timeout_passed
    context_manager = utils.check_timeout_passed

    def setUp(self) -> None:
        super().setUp()
        self.test_different_threads_decorator_result = {1}


class TestLockForExecution(BaseTestCases._BaseTest):
    decorator = utils.lock_for_execution
    context_manager = utils.lock_for_execution

    def setUp(self) -> None:
        super().setUp()
        self.test_different_threads_decorator_result = {1, 2}
