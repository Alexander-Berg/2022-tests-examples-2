import pytest

from noc.grad.grad.lib.pipeline_lib import Functions
from noc.grad.grad.lib.structures import FrozenDict


def _echo(*args, **kwargs):
    return args, kwargs


def _echo_with_job(*args, job, **kwargs):
    return args, job, kwargs


def test_functions_init():
    fn = Functions()
    fn.add(_echo)
    assert fn.get("_echo") is _echo

    # dup
    with pytest.raises(Exception):
        fn.add(_echo)

    assert fn.get("nope") is None


def test_functions_binding():
    fn = Functions()
    fn.add(_echo)
    fn.add(_echo_with_job)
    assert fn.get("_echo")() == ((), {})
    fn.bind("test", arg="olo")
    arg = FrozenDict({"filter": FrozenDict({"index": "component"})})
    # check Map args
    assert fn.bind("_echo", **arg)() == ((), {"filter": {"index": "component"}})
    # check auto_args bind
    assert fn.bind("_echo_with_job", "olo", some="some", auto_args={"job": "jobarg"})() == (
        ("olo",),
        "jobarg",
        {"some": "some"},
    )
