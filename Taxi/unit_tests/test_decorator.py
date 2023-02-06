import pytest
import uuid
import random
from time import sleep

from core.decorator import timer


def delay_value(from_=45, to=55):
    return random.randrange(from_, to)


def test_timer():
    timer_label = uuid.uuid4()

    class TestClass:
        def __init__(self, delay):
            self.delay = delay

        @timer(label=timer_label)
        def do_nothing(self):
            sleep(self.delay/1000.0)

    delay = delay_value()
    tc = TestClass(delay)
    tc.do_nothing()

    delay2 = delay_value()
    tc2 = TestClass(delay2)
    tc2.do_nothing()

    assert tc.timer_measurements[timer_label] == pytest.approx(delay, rel=1e-2)
    assert tc2.timer_measurements[timer_label] == pytest.approx(delay2, rel=1e-2)


def test_timer_wo_label():
    delay = delay_value()

    class TestClass:
        @timer()
        def timer_use_function_name(self):
            sleep(delay/1000.0)

    tc = TestClass()
    tc.timer_use_function_name()

    assert tc.timer_measurements['timer_use_function_name'] == pytest.approx(delay, rel=1e-2)
