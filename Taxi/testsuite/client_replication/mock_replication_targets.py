# pylint: disable=no-member
import collections
import functools

import pytest

from testsuite.utils import yaml_util


@functools.lru_cache(maxsize=None)
def _read_config(testsuite_build_dir):
    config_path = testsuite_build_dir.joinpath('configs/service.yaml')
    with open(config_path, mode='r', encoding='utf-8') as file:
        return yaml_util.load(file.read())


@pytest.fixture
def mock_replication_targets(mockserver, testsuite_build_dir):
    @mockserver.json_handler('/replication/v3/state/targets_info/retrieve')
    def _mock_targets(request):
        config = _read_config(testsuite_build_dir)
        yaml_targets = config['components_manager']['components'][
            'replication-yt-targets-cache'
        ]['replication-targets']

        return {
            'target_info': [
                _make_target_info(target)
                for target in _parse_targets(yaml_targets)
            ],
        }

    return _mock_targets


def _make_target_info(target):
    target_info = {
        'target_name': target['name'],
        'target_type': 'target-type',
        'replication_state': {'overall_status': 'enabled'},
        'replication_settings': {'replication_type': 'queue'},
        'yt_state': {
            'full_path': '//home/testsuite/' + target['name'],
            'clusters_states': [],
        },
    }
    for cluster in target['clusters']:
        target_info['yt_state']['clusters_states'].append(
            {'cluster_name': cluster, 'status': 'enabled'},
        )
    if target['partitions']:
        target_info['yt_state']['partitions'] = ['part-1', 'part-2']
    return target_info


def _parse_targets(yaml_targets):
    targets_by_name = collections.defaultdict(list)
    for yaml_target in yaml_targets:
        targets_by_name[yaml_target['target-name']].append(yaml_target)

    response_targets = []
    for name, targets in targets_by_name.items():
        partitions = targets[0].get('partitions', False)
        clusters = []
        for target in targets:
            clusters.append(_get_cluster_by_type(target['cluster-type']))
            if target.get('partitions', False) != partitions:
                raise RuntimeError(
                    f'Different partitions settings for target {name}',
                )

        response_targets.append(
            {'name': name, 'clusters': clusters, 'partitions': partitions},
        )
    return response_targets


def _get_cluster_by_type(cluster_type):
    if cluster_type == 'map-reduce':
        return 'hahn'
    if cluster_type == 'runtime':
        return 'seneca-sas'
    raise RuntimeError(f'Undefined cluster type: {cluster_type}')
