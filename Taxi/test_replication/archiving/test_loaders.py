from replication.archiving import classes
from replication.archiving import loaders


async def test_get_from_replication_rules(replication_ctx):
    rules = await loaders.get_from_replication_rules(replication_ctx)
    assert 'queue_mongo-staging_test_rule' in rules
    for rule_name, rule in rules.items():
        assert isinstance(rule, classes.BaseArchiver), rule_name
