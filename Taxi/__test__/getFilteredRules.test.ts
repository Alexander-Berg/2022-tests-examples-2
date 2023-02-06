import {RuleStateViewModel, ScopeFiltersModel} from '../types';
import {getFilteredRules} from '../utils';

const RULES: RuleStateViewModel[] = [
    {
        name: 'rule_1',
        global_state: 'enabled',
        source_description: {
            source_type: ''
        },
        destinations: [
            {
                name: 'rule_1_destination_1',
                state: 'enabled',
                alert_status: 'ok',
                diagnostics: [],
                meta: {
                    source_type: 'foo',
                    target_type: ''
                },
                raw_meta: {},
                extra_filters: []
            },
            {
                name: 'rule_1_destination_2',
                state: 'enabled',
                alert_status: 'ok',
                diagnostics: [],
                meta: {
                    source_type: '',
                    target_type: 'foo'
                },
                raw_meta: {},
                extra_filters: []
            }
        ]
    },
    {
        name: 'rule_2',
        global_state: 'enabled',
        source_description: {
            source_type: ''
        },
        destinations: [
            {
                name: 'rule_2_destination_1',
                state: 'disabled',
                alert_status: 'ok',
                diagnostics: [],
                meta: {
                    source_type: '',
                    target_type: ''
                },
                raw_meta: {},
                extra_filters: []
            },
            {
                name: 'rule_2_destination_2',
                state: 'enabled',
                alert_status: 'ok',
                diagnostics: [
                    {
                        name: 'bar_disgnostics_name',
                        link: 'bar_disgnostics_link',
                        alert_status: 'crit'
                    }
                ],
                meta: {
                    source_type: '',
                    target_type: ''
                },
                raw_meta: {},
                extra_filters: []
            }
        ]
    },
    {
        name: 'rule_3',
        global_state: 'enabled',
        source_description: {
            source_type: ''
        },
        destinations: [
            {
                name: 'rule_3_destination_1',
                state: 'enabled',
                alert_status: 'ok',
                diagnostics: [],
                meta: {
                    source_type: 'any',
                    target_type: ''
                },
                raw_meta: {},
                extra_filters: [{name: 'extra', value: 'baz_value'}]
            },
            {
                name: 'rule_3_destination_2',
                state: 'enabled',
                alert_status: 'ok',
                diagnostics: [],
                meta: {
                    source_type: 'any',
                    target_type: 'any'
                },
                raw_meta: {},
                extra_filters: [{name: 'extra', values: ['baz_values']}]
            }
        ]
    }
];

describe('getFilteredRules', () => {
    test('При остутствии фильтров возвращает изначальный список правил', () => {
        const filters: ScopeFiltersModel = {};
        const rules = getFilteredRules(RULES, filters);
        expect(rules).toStrictEqual(RULES);
    });

    test('Корректно находит правила по rule_name', () => {
        const filters: ScopeFiltersModel = {
            rule_name: 'rule_1'
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [RULES[0]];

        expect(actual).toStrictEqual(expected);
    });

    test('Если в найденных правилах по rule_name нет значений, то они игнорируются', () => {
        const filters: ScopeFiltersModel = {
            rule_name: 'rule_1',
            source_types: ['baz']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected: RuleStateViewModel[] = [];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по rule_names', () => {
        const filters: ScopeFiltersModel = {
            rule_names: ['rule_2']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [RULES[1]];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по target_name', () => {
        const filters: ScopeFiltersModel = {
            target_name: 'rule_1_destination_1'
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[0], destinations: [RULES[0].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по source_types', () => {
        const filters: ScopeFiltersModel = {
            source_types: ['foo']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[0], destinations: [RULES[0].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по target_types', () => {
        const filters: ScopeFiltersModel = {
            target_types: ['foo']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[0], destinations: [RULES[0].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по statuses', () => {
        const filters: ScopeFiltersModel = {
            statuses: ['disabled']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[1], destinations: [RULES[1].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по only_critical', () => {
        const filters: ScopeFiltersModel = {
            only_critical: true
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[1], destinations: [RULES[1].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по extra_filters c единственным значением', () => {
        const filters: ScopeFiltersModel = {
            extra_filters: [['extra', ['baz_value']]]
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[2], destinations: [RULES[2].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корректно находит правила по extra_filters c множественным значением', () => {
        const filters: ScopeFiltersModel = {
            extra_filters: [['extra', ['baz_values']]]
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[2], destinations: [RULES[2].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Корретно находит правила с фильтром по нескольким полям', () => {
        const filters: ScopeFiltersModel = {
            source_types: ['any'],
            target_types: ['any']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[2], destinations: [RULES[2].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('Если в правиле нет отфильтрованных таргетов, то оно не возвращается', () => {
        const filters: ScopeFiltersModel = {
            rule_name: 'rule_3',
            source_types: ['foo']
        };

        const actual = getFilteredRules(RULES, filters);

        expect(actual).toStrictEqual([]);
    });
});
