from metrika.admin.python.cms.judge.lib.decider.checks import check_temporary_unreachable_unknown_cluster
from metrika.admin.python.cms.judge.lib.decider.decision import Decision


def test_other_action(decider_mock):
    assert check_temporary_unreachable_unknown_cluster(decider_mock(walle_task={'walle_action': 'kek'})) is None


def test_in_allowlist(decider_mock):
    assert check_temporary_unreachable_unknown_cluster(decider_mock(
        walle_task={'walle_action': 'temporary-unreachable'},
        cluster='1',
        environment='1',
        temporary_unreachable_allowdict={'1': '1'}
    )) == Decision.OK


def test_cluster_not_in_allowlist(decider_mock):
    assert check_temporary_unreachable_unknown_cluster(decider_mock(
        walle_task={'walle_action': 'temporary-unreachable'},
        cluster='1',
        environment='1',
        temporary_unreachable_allowdict={}
    )) == Decision.IN_PROGRESS


def test_env_not_in_allowlist(decider_mock):
    assert check_temporary_unreachable_unknown_cluster(decider_mock(
        walle_task={'walle_action': 'temporary-unreachable'},
        cluster='1',
        environment='2',
        temporary_unreachable_allowdict={'1': '1'}
    )) == Decision.IN_PROGRESS
