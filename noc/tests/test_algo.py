import json

from noc.susanin.internal.calculator.paths_calculator import run_algo
from noc.susanin.internal.calculator.zk import Topology, Settings, Snapshot

import yatest.common


def test_algo_dc():
    topology_path = yatest.common.source_path('noc/susanin/internal/calculator/tests/topology.json')
    settings_path = yatest.common.source_path('noc/susanin/internal/calculator/tests/settings.json')
    prev_snapshot_path = yatest.common.source_path('noc/susanin/internal/calculator/tests/prev_snapshot.json')

    with open(topology_path, 'r') as f:
        topology = Topology.from_dict(json.load(f))

    with open(settings_path, 'r') as f:
        settings = Settings.from_dict(json.load(f))

    with open(prev_snapshot_path, 'r') as f:
        prev_snapshot = Snapshot.from_dict(json.load(f))

    run_algo(topology, settings, prev_snapshot)
