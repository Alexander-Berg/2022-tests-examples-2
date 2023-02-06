import unittest

from dmp_suite.threading_utils import IteratingThread


class IteratingThreadTest(unittest.TestCase):
    def test_yields_same_items(self):
        sequence = [1, 2, 3]
        thread = IteratingThread(iter(sequence))

        thread.start()
        assert list(thread) == sequence

    def test_yields_no_items(self):
        sequence = []
        thread = IteratingThread(iter(sequence))

        thread.start()
        assert list(thread) == sequence

    def test_propagates_exceptions(self):
        class SomeError(Exception):
            pass

        def raising_generator():
            yield 1
            raise SomeError()

        thread = IteratingThread(raising_generator())
        thread.start()
        thread.join()  # To assure that an exception is raised in due time.

        assert next(thread) == 1
        with self.assertRaises(SomeError):
            next(thread)

    def test_fails_if_not_started(self):
        sequence = [1, 2, 3]
        thread = IteratingThread(iter(sequence))

        with self.assertRaises(RuntimeError):
            list(thread)
