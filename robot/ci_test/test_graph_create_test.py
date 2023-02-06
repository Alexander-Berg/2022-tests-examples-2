# coding: utf-8
from yatest import common


def test_graph_create_test():
    common.canonical_execute(
        common.binary_path("robot/selectionrank/sr_conduct_rules_experiment/sr_conduct_rules_experiment"),
        ['--test-mode', 'create-test', '--random-urls-count', '100000000'],
        env={'YT_PROXY': 'banach.yt.yandex.net'},
    )
