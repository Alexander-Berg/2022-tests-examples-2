# coding: utf-8
from __future__ import absolute_import

import mock
import pytest

from sandbox.common import system
from sandbox.common import context


class TestTimer(object):

    def test__timer_hierarchy(self):
        timer = context.Timer()
        assert timer.current is timer
        assert timer.running is False
        with pytest.raises(KeyError):
            _ = timer["a"]  # noqa
        timer.start()
        assert timer.current is timer
        assert timer.running is True
        timer_a = timer["a"]
        assert timer.current is timer
        assert timer_a.current is timer
        assert timer_a.running is False
        timer_a.start()
        assert timer.current is timer_a
        assert timer.running is True
        assert timer_a.current is timer_a
        assert timer_a.running is True
        timer_b = timer["b"]
        assert timer.current is timer_a
        assert timer.running is True
        assert timer_a.current is timer_a
        assert timer_a.running is True
        assert timer_b.current is timer_a
        assert timer_b.running is False
        timer_b.start()
        assert timer.current is timer_b
        assert timer.running is True
        assert timer_a.current is timer_b
        assert timer_a.running is True
        assert timer_b.current is timer_b
        assert timer_b.running is True
        timer_b.stop()
        assert timer.current is timer_a
        assert timer.running is True
        assert timer_a.current is timer_a
        assert timer_a.running is True
        assert timer_b.current is timer_a
        assert timer_b.running is False
        timer_c = timer["c"]
        assert timer.current is timer_a
        assert timer.running is True
        assert timer_a.current is timer_a
        assert timer_a.running is True
        assert timer_b.current is timer_a
        assert timer_b.running is False
        assert timer_c.current is timer_a
        assert timer_c.running is False
        timer_c.start()
        assert timer.current is timer_c
        assert timer.running is True
        assert timer_a.current is timer_c
        assert timer_a.running is True
        assert timer_b.current is timer_c
        assert timer_b.running is False
        assert timer_c.current is timer_c
        assert timer_c.running is True
        timer_c.stop()
        assert timer.current is timer_a
        assert timer.running is True
        assert timer_a.current is timer_a
        assert timer_a.running is True
        assert timer_b.current is timer_a
        assert timer_b.running is False
        assert timer_c.current is timer_a
        assert timer_c.running is False
        timer_a.stop()
        assert timer.current is timer
        assert timer.running is True
        assert timer_a.current is timer
        assert timer_a.running is False
        assert timer_b.current is timer
        assert timer_b.running is False
        assert timer_c.current is timer
        assert timer_c.running is False
        timer_a.start()
        assert timer.current is timer_a
        assert timer.running is True
        assert timer_a.current is timer_a
        assert timer_a.running is True
        assert timer_b.current is timer_a
        assert timer_b.running is False
        assert timer_c.current is timer_a
        assert timer_c.running is False
        timer_a.stop()
        assert timer.current is timer
        assert timer.running is True
        assert timer_a.current is timer
        assert timer_a.running is False
        assert timer_b.current is timer
        assert timer_b.running is False
        assert timer_c.current is timer
        assert timer_c.running is False
        timer.stop()
        assert timer.current is timer
        assert timer.running is False
        assert timer_a.current is timer
        assert timer_a.running is False
        assert timer_b.current is timer
        assert timer_b.running is False
        assert timer_c.current is timer
        assert timer_c.running is False

        with context.Timer(1) as timer:
            assert timer.left

        with context.Timer(None) as timer:
            assert timer.left is None


@pytest.fixture()
def binary_mock(monkeypatch):
    def inner(is_binary):
        inside_the_binary = mock.Mock(return_value=is_binary)
        monkeypatch.setattr(system, "inside_the_binary", inside_the_binary)
    return inner


class TestSkipIfBinary(object):

    def test__skip(self, binary_mock):
        binary_mock(is_binary=True)

        with context.skip_if_binary("Test"):
            raise AssertionError("The code was expected to be skipped")

        @context.skip_if_binary("Test")
        def test():
            raise AssertionError("The code was expected to be skipped")

        test()

    def test__do_not_skip(self, binary_mock):
        binary_mock(is_binary=False)

        with pytest.raises(RuntimeError):
            with context.skip_if_binary("Test"):
                raise RuntimeError

        @context.skip_if_binary("Test")
        def test():
            raise RuntimeError

        with pytest.raises(RuntimeError):
            test()

    def test__skip_return_value(self, binary_mock):
        binary_mock(is_binary=True)

        @context.skip_if_binary("Test", return_value=42)
        def test():
            return 420

        assert test() == 42
