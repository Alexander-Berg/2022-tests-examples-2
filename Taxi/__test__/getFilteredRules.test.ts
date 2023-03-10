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
    test('?????? ???????????????????? ???????????????? ???????????????????? ?????????????????????? ???????????? ????????????', () => {
        const filters: ScopeFiltersModel = {};
        const rules = getFilteredRules(RULES, filters);
        expect(rules).toStrictEqual(RULES);
    });

    test('?????????????????? ?????????????? ?????????????? ???? rule_name', () => {
        const filters: ScopeFiltersModel = {
            rule_name: 'rule_1'
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [RULES[0]];

        expect(actual).toStrictEqual(expected);
    });

    test('???????? ?? ?????????????????? ???????????????? ???? rule_name ?????? ????????????????, ???? ?????? ????????????????????????', () => {
        const filters: ScopeFiltersModel = {
            rule_name: 'rule_1',
            source_types: ['baz']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected: RuleStateViewModel[] = [];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? rule_names', () => {
        const filters: ScopeFiltersModel = {
            rule_names: ['rule_2']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [RULES[1]];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? target_name', () => {
        const filters: ScopeFiltersModel = {
            target_name: 'rule_1_destination_1'
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[0], destinations: [RULES[0].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? source_types', () => {
        const filters: ScopeFiltersModel = {
            source_types: ['foo']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[0], destinations: [RULES[0].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? target_types', () => {
        const filters: ScopeFiltersModel = {
            target_types: ['foo']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[0], destinations: [RULES[0].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? statuses', () => {
        const filters: ScopeFiltersModel = {
            statuses: ['disabled']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[1], destinations: [RULES[1].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? only_critical', () => {
        const filters: ScopeFiltersModel = {
            only_critical: true
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[1], destinations: [RULES[1].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? extra_filters c ???????????????????????? ??????????????????', () => {
        const filters: ScopeFiltersModel = {
            extra_filters: [['extra', ['baz_value']]]
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[2], destinations: [RULES[2].destinations[0]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('?????????????????? ?????????????? ?????????????? ???? extra_filters c ?????????????????????????? ??????????????????', () => {
        const filters: ScopeFiltersModel = {
            extra_filters: [['extra', ['baz_values']]]
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[2], destinations: [RULES[2].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('???????????????? ?????????????? ?????????????? ?? ???????????????? ???? ???????????????????? ??????????', () => {
        const filters: ScopeFiltersModel = {
            source_types: ['any'],
            target_types: ['any']
        };

        const actual = getFilteredRules(RULES, filters);
        const expected = [{...RULES[2], destinations: [RULES[2].destinations[1]]}];

        expect(actual).toStrictEqual(expected);
    });

    test('???????? ?? ?????????????? ?????? ?????????????????????????????? ????????????????, ???? ?????? ???? ????????????????????????', () => {
        const filters: ScopeFiltersModel = {
            rule_name: 'rule_3',
            source_types: ['foo']
        };

        const actual = getFilteredRules(RULES, filters);

        expect(actual).toStrictEqual([]);
    });
});
