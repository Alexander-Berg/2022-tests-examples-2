# coding: utf-8
from yatest import common


def test_graph_test_jupiters_url_pools():
    common.canonical_execute(
        common.binary_path("robot/selectionrank/sr_conduct_rules_experiment/sr_conduct_rules_experiment"),
        ['--test-mode', 'test-jupiters-url-pools'],
        env={'YT_PROXY': 'banach.yt.yandex.net'},
    )
