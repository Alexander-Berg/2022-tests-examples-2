# pylint: disable=protected-access
import pytest

from replication.replication import classes

_TEST_SCOPE = 'test_api_basestamp'
_TEST_RULES_LIST = ['test_api_basestamp', 'test_map_data']
_ALL_TEST_API_BASESTAMP_RULES = [
    'api_replicate_by',
    'test_api_basestamp',
    'test_map_data',
    'test_errors_rule',
    'test_rule',
]


@pytest.mark.parametrize(
    'rule_scope, rule_names, check_rules, check_scope',
    [
        (None, _TEST_RULES_LIST, _TEST_RULES_LIST, None),
        (_TEST_SCOPE, None, _ALL_TEST_API_BASESTAMP_RULES, _TEST_SCOPE),
        (_TEST_SCOPE, _TEST_RULES_LIST, _TEST_RULES_LIST, _TEST_SCOPE),
    ],
)
def test_get_rules_list(
        replication_ctx, rule_scope, rule_names, check_rules, check_scope,
):
    rules_by_scope = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_scope=rule_scope, rule_names=rule_names,
    )
    if check_rules is not None:
        storage_rule_names = {rule.name for rule in rules_by_scope}
        assert storage_rule_names == set(check_rules)
    if check_scope is not None:
        for rule in rules_by_scope:
            assert rule.source.base_meta.rule_scope == check_scope


@pytest.mark.parametrize(
    'filters,expected',
    [
        ({'target_types': ['yt', 'queue_mongo']}, True),
        ({'target_types': ['yt'], 'responsible': None}, True),
        (
            {
                'target_types': None,
                'target_names': None,
                'target_unit_ids': None,
                'responsible': None,
            },
            True,
        ),
        (
            {
                'target_types': None,
                'target_names': ['test_rule_bson'],
                'target_unit_ids': None,
                'responsible': None,
            },
            True,
        ),
        (
            {
                'target_types': None,
                'target_unit_ids': ['arni'],
                'responsible': None,
            },
            True,
        ),
        (
            {
                'target_types': None,
                'target_unit_ids': ['arni'],
                'responsible': ['testsuite'],
            },
            True,
        ),
        (
            {
                'target_types': ['xxx'],
                'target_unit_ids': ['arni'],
                'responsible': ['testsuite'],
            },
            classes.UnknownTargetError,
        ),
        (
            {
                'target_types': None,
                'target_unit_ids': ['arni'],
                'responsible': ['testsuite'],
                'fail': [1, 2, 3],
            },
            classes.IncompatibleParamsError,
        ),
        (
            {
                'target_types': None,
                'target_unit_ids': ['arni'],
                'responsible': ['fail'],
            },
            False,
        ),
    ],
)
def test_generate_target_filters(replication_ctx, filters, expected):
    target = replication_ctx.rule_keeper.rules_storage.get_target(
        replication_id='queue_mongo-staging_test_rule-yt-test_rule_bson-arni',
    )
    if expected not in {True, False}:
        with pytest.raises(expected):
            classes._generate_target_filters(**filters)
    else:
        target_filter = classes._generate_target_filters(**filters)
        assert target_filter(target) is expected
