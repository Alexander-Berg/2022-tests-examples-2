from metrika.admin.python.cms.frontend.cms.fsm import transitions


def test_unique_transitions_ok():
    assert sorted(transitions) == sorted(set(transitions)), 'Duplicate transitions!'
