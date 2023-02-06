import collections
import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.internal import maintenance
from taxi.internal.yt_replication import rules
from taxi.internal.yt_tools import replication_kit

NEW_LAST_UPDATED = datetime.datetime(2018, 6, 26, 10, 0, 0)
_DummyDestRule = collections.namedtuple(
    '_DummyDestRule', ['destination']
)
_DummyDest = collections.namedtuple(
    '_DummyDest', ['name', 'yt_table', 'yt_cluster_group', 'partial_update']
)

_DEST_RULES = {
    'dest_1': _DummyDestRule(
        _DummyDest('dest_1', 'yt_table_1', 'map_reduce', True)
    ),
    'dest_2': _DummyDestRule(
        _DummyDest('dest_2', 'yt_table_1', 'map_reduce', True)
    ),
    'dest_3': _DummyDestRule(
        _DummyDest('dest_3', 'yt_table_1', 'map_reduce', True)
    ),
    'dest_4': _DummyDestRule(
        _DummyDest('dest_4', 'yt_table_1', 'runtime', True)
    ),
    'dest_5': _DummyDestRule(
        _DummyDest('dest_5', 'yt_table_2', 'runtime', True)
    ),
    'dest_6': _DummyDestRule(
        _DummyDest('dest_6', 'yt_table_2', 'runtime', True)
    ),
}


def _cast_rule(dest_name):
    destination = _DEST_RULES[dest_name].destination
    if destination.yt_cluster_group == 'map_reduce':
        rule_class = rules.ReplicationRule
    else:
        rule_class = rules.RuntimeReplicationRule
    return rule_class(destination.yt_table, None, dest_name)


_RULES = {dest_name: _cast_rule(dest_name) for dest_name in _DEST_RULES}


class DummyYtClient(object):
    def __init__(self, cluster):
        self.config = {'proxy': {'url': '%s.cluster' % cluster}}

    def set(self, *args, **kwargs):
        pass


class DummyLock(maintenance.DummyLock):
    def __init__(self, key):
        pass


@pytest.mark.parametrize(
    'dest_name,clusters,expected_dest_names,expected_enabled',
    [
        (
            'dest_1',
            ['hahn', 'arnold'],
            ('dest_1', 'dest_2', 'dest_3'),
            ['dest_1', 'dest_3'],
        ),
        (
            'dest_2',
            ['hahn', 'arnold'],
            ('dest_1', 'dest_2', 'dest_3'),
            ['dest_1', 'dest_3'],
        ),
        (
            'dest_3',
            ['hahn', 'arnold'],
            ('dest_1', 'dest_2', 'dest_3'),
            ['dest_1', 'dest_3'],
        ),
        (
            'dest_4',
            ['seneca-man', 'seneca-sas', 'seneca-vla'],
            ('dest_4',),
            ['dest_4'],
        ),
        (
            'dest_5',
            ['seneca-man', 'seneca-sas', 'seneca-vla'],
            ('dest_5', 'dest_6'),
            ['dest_5'],
        )
    ]
)
@pytest.mark.config(
    YT_REPLICATION_RUNTIME_CLUSTERS=['seneca-man', 'seneca-sas', 'seneca-vla']
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_replication_disabled(dest_name, clusters, expected_dest_names,
                              expected_enabled, patch, monkeypatch):
    _setup(patch, monkeypatch)
    monkeypatch.setattr(settings, 'YT_CLUSTER_GROUPS', {
        'runtime': ['seneca-sas', 'seneca-man', 'seneca-vla'],
        'map_reduce': ['hahn', 'arnold'],
    })
    replication_disabled = replication_kit.ReplicationDisabled(dest_name)
    with replication_disabled as replication_handler:
        for cluster in clusters:
            yield replication_handler.set_cluster_last_updated_for_initialized(
                DummyYtClient(cluster), NEW_LAST_UPDATED
            )
        yield replication_handler.set_last_updated(
            NEW_LAST_UPDATED, initialized=False
        )

    assert expected_dest_names == replication_disabled._handler.dest_names

    enabled = []
    for dest_name in replication_disabled._handler.dest_names:
        replication_info = yield db.yt_replications.find_one(dest_name)
        if replication_info.get('enabled'):
            enabled.append(dest_name)
        clusters_info = replication_info['clusters_info']
        assert len(clusters_info) == len(clusters), (
            'number of clusters not matching for %s' % dest_name
        )
        for cluster_info in clusters_info:
            assert cluster_info['last_updated'] == NEW_LAST_UPDATED, (
                'last updated for cluster %s not matching for cluster %s' % (
                    cluster_info['name'], dest_name
                )
            )

    assert expected_enabled == enabled


def _setup(patch, monkeypatch):
    monkeypatch.setattr(
        rules, '_cached_dest_rules', _DEST_RULES
    )
    monkeypatch.setattr(
        maintenance, 'TaskLock', DummyLock
    )

    @patch('taxi.internal.yt_replication.rules.get_replication_rule')
    def get_replication_rule(rule_name, *args, **kwargs):
        return _RULES[rule_name]

    @patch('taxi.internal.yt_replication.rules.get_chain_by_rule_name')
    @async.inline_callbacks
    def get_chain_by_rule_name(dest_name):
        yield async.return_value(())

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(name, *args, **kwargs):
        return DummyYtClient(name)
