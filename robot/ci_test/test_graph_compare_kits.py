# coding: utf-8
from yatest import common


def test_graph_compare_kits():
    common.canonical_execute(
        common.binary_path("robot/selectionrank/sr_conduct_rules_experiment/sr_conduct_rules_experiment"),
        ['--notification', 'first', 'second', '--test-mode', 'test-jupiters-url-pools', '-j', '20161217-214320', '20161219-122220', '20161215-130220'],
        env={'YT_PROXY': 'banach.yt.yandex.net'},
    )
