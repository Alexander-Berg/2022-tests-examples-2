# coding: utf-8
from yatest import common


def test_graph_full_chain():
    kit_path = common.source_path('robot/selectionrank/sr_conduct_rules_experiment/kit_templates/default.json')
    common.canonical_execute(
        common.binary_path("robot/selectionrank/sr_conduct_rules_experiment/sr_conduct_rules_experiment"),
        ['--test-mode', 'full-chain', '--kits', kit_path, '--type', 'jupiter'],
        env={'YT_PROXY': 'banach.yt.yandex.net'},
    )
