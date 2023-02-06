import pytest

from replication_core import load
from replication_core.rules import classes
from replication_core.rules import flaky_config


@pytest.mark.parametrize(
    'main,partial', [(True, False), (False, True), (True, True)],
)
def test_load_simple(
        replication_core_rules, load_core_rules_yaml, main, partial,
):
    rules_scopes_storage = replication_core_rules.load(
        main=main, partial=partial,
    )
    if main:
        assert 'example_rule_scope' in rules_scopes_storage.rule_scopes
        assert rules_scopes_storage.plugins == [
            'core_test_rule_scopes.plugins.__init__',
        ]
        _test_example_rule(
            replication_core_rules, rules_scopes_storage.rule_scopes,
        )
    else:
        assert 'example_rule_scope' not in rules_scopes_storage.rule_scopes
        assert rules_scopes_storage.plugins == []


@pytest.mark.parametrize(
    'main,partial', [(True, False), (False, True), (True, True)],
)
def test_load_zero(
        replication_core_rules, load_core_rules_yaml, main, partial,
):
    rules_scopes_storage = replication_core_rules.load(
        main=main, partial=partial,
    )
    _test_zero_rule(
        replication_core_rules,
        load_core_rules_yaml,
        rules_scopes_storage,
        main=main,
        partial=partial,
    )


def test_partial_rule_error(replication_core_rules, load_core_rules_yaml):
    rules_scopes_storage: classes.RuleScopesStorage
    rules_scopes_storage = replication_core_rules.load(main=True, partial=True)
    errors = rules_scopes_storage.parse_errors
    invalid_partial_rule_name = 'zero'
    assert errors
    assert len(errors) == 1
    assert errors[0] == classes.ParseErrorInfo(
        origin=classes.ParseErrorOrigin.evolve,
        rule_name=invalid_partial_rule_name,
        message=(
            f'Cannot evolve rule \'{invalid_partial_rule_name}\'. There are '
            'duplicate mapper paths: {\'zero_mapper\'}'
        ),
    )

    # make sure that after attempting to merge invalid partial rule the
    # original rule is still present in the storage
    rule_scope_name = 'scope_zero'
    original_rule = rules_scopes_storage.rule_scopes[rule_scope_name].rules[
        invalid_partial_rule_name
    ]
    assert original_rule


def _test_example_rule(replication_core_rules, rule_scopes):
    rules_scope: load.RuleScope = rule_scopes['example_rule_scope']
    assert rules_scope.mappers_dict == {
        'me_mapper': {
            'columns': [
                {'input_column': 'foo', 'output_column': 'foo'},
                {'input_column': 'bar', 'output_column': 'bar'},
            ],
        },
    }
    assert rules_scope.rules == {
        'example': classes.RuleObj(
            raw={
                'name': 'example',
                'config': {
                    'test_flaky': {'value': '001', 'dct': {'value1': 'rule'}},
                },
                'destinations': [
                    {
                        'example_dst': {
                            'mapper': 'me_mapper',
                            'type': '{target_type_here}',
                            'config': {
                                'test_flaky': {'dct': {'value2': 'target'}},
                            },
                            'target': {'path': 'random/path/target'},
                        },
                        'example_dst_2': {
                            'type': '{target_type_here}',
                            'target': {'path': 'random/target_2'},
                        },
                    },
                ],
            },
            rule_name='example',
            flaky_config=flaky_config.FlakyDict(
                {'test_flaky': {'value': '001', 'dct': {'value1': 'rule'}}},
            ),
            targets={
                'example_dst': classes.TargetObj(
                    declaration={
                        'mapper': 'me_mapper',
                        'type': '{target_type_here}',
                        'target': {'path': 'random/path/target'},
                        'config': {
                            'test_flaky': {'dct': {'value2': 'target'}},
                        },
                    },
                    target_group_index=0,
                    target_name='example_dst',
                    target_type='{target_type_here}',
                    target_path='random/path/target',
                    target_doc={'target': 'data'},
                    mapper_path='me_mapper',
                    mapper_doc={
                        'columns': [
                            {'input_column': 'foo', 'output_column': 'foo'},
                            {'input_column': 'bar', 'output_column': 'bar'},
                        ],
                    },
                    mapper_testcase_full_path=(
                        replication_core_rules.make_main_path(
                            'example_rule_scope/mappers-tests/me_mapper',
                        )
                    ),
                    flaky_config=flaky_config.FlakyDict(
                        {
                            'test_flaky': {
                                'value': '001',
                                'dct': {'value2': 'target'},
                            },
                        },
                    ),
                ),
                'example_dst_2': classes.TargetObj(
                    declaration={
                        'type': '{target_type_here}',
                        'target': {'path': 'random/target_2'},
                    },
                    target_group_index=0,
                    target_name='example_dst_2',
                    target_type='{target_type_here}',
                    target_path='random/target_2',
                    target_doc={'target': 'data2'},
                    flaky_config=flaky_config.FlakyDict(
                        {
                            'test_flaky': {
                                'value': '001',
                                'dct': {'value1': 'rule'},
                            },
                        },
                    ),
                ),
            },
        ),
    }
    assert rules_scope.plugins == []


def _test_zero_rule(
        replication_core_rules, load_yaml, rules_scopes_storage, main, partial,
):
    rule_scopes = rules_scopes_storage.rule_scopes
    raw_zero_mapper = load_yaml('scope_zero/mappers/zero_mapper')
    raw_zero_mapper2 = load_yaml(
        'scope_zero_x/mappers/zero_mapper2', main=False,
    )
    raw_zero_rule = load_yaml('scope_zero/zero')
    raw_zero_rule_partial = load_yaml('scope_zero_x/partial_rule', main=False)

    zero_flaky_config = flaky_config.FlakyDict(
        {'test_flaky': {'value': '000', 'dct': {'value1': 'full'}}},
    )
    base_expected_targets = {
        'zero_dst_1_1': classes.TargetObj(
            declaration={
                'type': 'target_type_here',
                'target': {'path': 'abc/table_1_1'},
                'mapper': 'zero_mapper',
            },
            target_group_index=0,
            target_name='zero_dst_1_1',
            target_type='target_type_here',
            target_path='abc/table_1_1',
            target_doc=None,
            mapper_path='zero_mapper',
            mapper_doc=raw_zero_mapper,
            mapper_testcase_full_path=replication_core_rules.make_main_path(
                'scope_zero/mappers-tests/zero_mapper',
            ),
            flaky_config=zero_flaky_config,
        ),
        'zero_dst_1_2': classes.TargetObj(
            declaration={
                'type': 'target_type_here',
                'target': {'path': 'abc/table_1_2'},
                'mapper': 'zero_mapper',
            },
            target_group_index=0,
            target_name='zero_dst_1_2',
            target_type='target_type_here',
            target_path='abc/table_1_2',
            target_doc=None,
            mapper_path='zero_mapper',
            mapper_doc=raw_zero_mapper,
            mapper_testcase_full_path=replication_core_rules.make_main_path(
                'scope_zero/mappers-tests/zero_mapper',
            ),
            flaky_config=zero_flaky_config,
        ),
        'zero_dst_2_1': classes.TargetObj(
            declaration={
                'type': 'target_type_here',
                'target': {'path': 'abc/table_2_1'},
                'mapper': 'zero_mapper',
            },
            target_group_index=1,
            target_name='zero_dst_2_1',
            target_type='target_type_here',
            target_path='abc/table_2_1',
            target_doc=None,
            mapper_path='zero_mapper',
            mapper_doc=raw_zero_mapper,
            mapper_testcase_full_path=replication_core_rules.make_main_path(
                'scope_zero/mappers-tests/zero_mapper',
            ),
            flaky_config=zero_flaky_config,
        ),
    }
    partial_activation_type = (
        classes.TargetActivationType.plugged
        if main
        else classes.TargetActivationType.usual
    )

    zero_flaky_config_partial = flaky_config.FlakyDict(
        {'test_flaky': {'value': '456', 'dct': {'value2': 'partial'}}},
    )

    partial_expected_targets = {
        'zero_dst_1_3': classes.TargetObj(
            declaration={
                'type': 'target_type_here',
                'target': {'path': 'abc/table_1_3'},
                'mapper': 'zero_mapper2',
            },
            target_group_index=0,
            target_name='zero_dst_1_3',
            target_type='target_type_here',
            target_path='abc/table_1_3',
            target_doc=None,
            mapper_path='zero_mapper2',
            mapper_doc=raw_zero_mapper2,
            mapper_testcase_full_path=replication_core_rules.make_partial_path(
                'scope_zero_x/mappers-tests/zero_mapper2',
            ),
            activation_type=partial_activation_type,
            flaky_config=zero_flaky_config_partial,
        ),
        'zero_dst_3_1': classes.TargetObj(
            declaration={
                'type': 'target_type_here',
                'target': {'path': 'abc/table_3_1'},
                'mapper': 'zero_mapper2',
            },
            target_group_index=2,
            target_name='zero_dst_3_1',
            target_type='target_type_here',
            target_path='abc/table_3_1',
            target_doc=None,
            mapper_path='zero_mapper2',
            mapper_doc=raw_zero_mapper2,
            mapper_testcase_full_path=replication_core_rules.make_partial_path(
                'scope_zero_x/mappers-tests/zero_mapper2',
            ),
            activation_type=partial_activation_type,
            flaky_config=zero_flaky_config_partial,
        ),
    }
    expected_count_evolved_rules = {}
    if main:
        assert 'scope_zero_x' not in rule_scopes
        rules_scope: load.RuleScope = rule_scopes['scope_zero']
        expected_mappers = {'zero_mapper': raw_zero_mapper}
        expected_rules = {
            'zero': classes.RuleObj(
                raw=raw_zero_rule,
                rule_name='zero',
                targets=base_expected_targets,
                source={'full': True},
                flaky_config=flaky_config.FlakyDict(
                    {
                        'test_flaky': {
                            'value': '000',
                            'dct': {'value1': 'full'},
                        },
                    },
                ),
            ),
        }
        expected_plugins = [
            'core_test_rule_scopes.scope_zero.plugins.__init__',
        ]
        if partial:
            expected_mappers['zero_mapper2'] = raw_zero_mapper2
            expected_rules['zero'].targets.update(partial_expected_targets)
            expected_plugins.append(
                'core_test_partial.scope_zero_x.plugins.__init__',
            )
            expected_count_evolved_rules = {'zero': 2}
    else:
        assert 'scope_zero' not in rule_scopes
        rules_scope: load.RuleScope = rule_scopes['scope_zero_x']
        expected_mappers = {'zero_mapper2': raw_zero_mapper2}
        expected_rules = {
            'zero': classes.RuleObj(
                raw=raw_zero_rule_partial,
                rule_name='zero',
                targets=partial_expected_targets,
                flaky_config=flaky_config.FlakyDict(
                    {
                        'test_flaky': {
                            'value': '456',
                            'dct': {'value2': 'partial'},
                        },
                    },
                ),
            ),
        }
        expected_plugins = ['core_test_partial.scope_zero_x.plugins.__init__']

    assert rules_scope.mappers_dict == expected_mappers
    assert rules_scope.rules == expected_rules
    assert rules_scope.plugins == expected_plugins
    assert rules_scopes_storage.count_evolved_rules == (
        expected_count_evolved_rules
    )
