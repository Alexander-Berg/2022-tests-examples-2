from hamcrest import equal_to, has_entry, only_contains

import metrika.core.test_framework.utils.wait as wait


def test_ping(steps):
    wait.wait_for(predicate=lambda: steps.input.ping())


def test_status(steps):
    wait.wait_for(predicate=lambda: has_entry("message", has_entry("slaves", only_contains(has_entry("is_alive", equal_to(True))))).matches(steps.input.status()))
