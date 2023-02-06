import pytest

from taxi.conf import settings
from taxi.internal.yt_replication import rules
from taxi.internal.data_manager import consts
from taxi.internal.yt_replication.rules import rule_names
from taxi.internal.yt_replication.rules import rules as rules_instances


MULTIPLE_CLUSTER_GROUPS_TABLES = frozenset([
    'replica/mongo/struct/orders_full',
    'replica/mongo/struct/feedbacks',
    'private/mongo/bson/order_proc',
    'private/mongo/bson/orders',
])


@pytest.inline_callbacks
def test_build_replication_chains(monkeypatch):
    _patch_rules(monkeypatch)

    chains = yield rules.build_replication_chains()
    assert tuple(sorted(chains)) == (
        ('dest1', 'dest2', 'dest3'), ('dest4',), ('dest5',)
    )


@pytest.mark.parametrize('rule_name,expected', [
    (
        'dest1',
        ('dest1', 'dest2', 'dest3'),
    ),
    (
        'dest2',
        ('dest1', 'dest2', 'dest3'),
    ),
    (
        'dest3',
        ('dest1', 'dest2', 'dest3'),
    ),
    (
        'dest4',
        ('dest4',),
    ),
    (
        'dest5',
        ('dest5',),
    ),
    (
        'dest_excluded',
        None,
    ),
])
@pytest.inline_callbacks
def test_get_chain_by_rule_name(monkeypatch, rule_name, expected):
    _patch_rules(monkeypatch)

    if expected:
        assert (yield rules.get_chain_by_rule_name(rule_name)) == expected
    else:
        with pytest.raises(rules.ChainNotFoundError):
            yield rules.get_chain_by_rule_name(rule_name)


def _patch_rules(monkeypatch):

    def _get_replication_rule(rule_name, *args, **kwargs):
        class _DummyRule(object):
            collection_type = 'mongo'

        return _DummyRule()

    monkeypatch.setattr(
        rules, 'get_replication_rule', _get_replication_rule
    )


def test_try_get_dest_names_by_table(monkeypatch, patch):
    @patch('taxi.external.yt_wrapper.get_local_yt_table_path')
    def get_local_yt_table_path(yt_client, path):
        return path

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(*args, **kwargs):
        pass

    dest_rules = rules.get_dest_rules()
    groups = settings.YT_CLUSTER_GROUPS.keys()

    tables_by_groups = {}
    yt_table_getter_rules = set()
    for dest_name, dest_rule in dest_rules.iteritems():
        table = dest_rule.destination.yt_table
        tables_by_groups[table] = set()
        for group in groups:
            try:
                rules.try_get_dest_names_by_table(
                    table, group
                )
            except rules.UnknownReplicationRule:
                pass
            else:
                tables_by_groups[table].add(group)

        if dest_rule.destination.yt_table_getter:
            yt_table_getter_rules.add(dest_name)
            groups_count = 0
            for group in groups:
                try:
                    rules.try_get_dest_names_by_table(
                        table + '/01.01', group
                    )
                except rules.UnknownReplicationRule:
                    pass
                else:
                    groups_count += 1
            assert groups_count == 1, (
                'unexpected rule with table getter on more than '
                'one cluster group: %s' % dest_name
            )

    for table, groups in tables_by_groups.iteritems():
        if len(groups) == 2:
            assert table in MULTIPLE_CLUSTER_GROUPS_TABLES
        else:
            assert len(groups) == 1, (
                'more than one cluster group for %s table' % table
            )


@pytest.mark.filldb(_fill=False)
def test_only_external_rules_instances():
    for maybe_rule in vars(rules_instances).values():
        if not isinstance(maybe_rule, rules.ReplicationRule):
            continue
        assert maybe_rule.collection_type == consts.COLLECTION_TYPE_EXTERNAL, (
            'Do not create instances of not collection_type==external rules '
            '(name={}). '
            'Use taxi.internal.replication and '
            'taxi.internal.yt_replication.rule_names instead of it'.format(
                maybe_rule.name,
            )
        )


@pytest.mark.filldb(_fill=False)
def test_not_external_rule_names():
    for rule_name in vars(rule_names).values():
        if not isinstance(rule_name, basestring):
            continue
        try:
            rule = rules.get_replication_rule(rule_name)
        except rules.UnknownReplicationRule:
            continue
        assert rule.collection_type != consts.COLLECTION_TYPE_EXTERNAL, (
            'Do not add rule names with collection_type==external '
            '(name={}). '
            'Use taxi.internal.yt_replication.rules instead of it'.format(
                rule_name,
            )
        )
