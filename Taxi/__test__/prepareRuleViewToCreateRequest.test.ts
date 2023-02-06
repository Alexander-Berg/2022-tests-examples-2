import moment from 'moment';

import {ModeRulesCreateRequest, RuleModel} from '../../types';
import {prepareRuleViewToCreateRequest} from '../prepareRuleViewToCreateRequest';

describe('prepareRuleViewToCreateRequest', () => {
    test('empty rule', () => {
        const ruleModel: RuleModel = {};
        const expected: ModeRulesCreateRequest = {
            rule: {
                conditions: undefined,
                starts_at: undefined,
                stops_at: undefined,
                billing_settings: {
                    mode_rule: undefined,
                    mode: undefined,
                },
                display_settings: {
                    mode: undefined,
                    profile: undefined,
                },
                offers_group: undefined,
                features: undefined,
                work_mode: undefined,
            },
            rules_to_close: undefined,
        };
        const res = prepareRuleViewToCreateRequest(ruleModel);
        expect(res).toEqual(expected);
    });

    test('filled rule', () => {
        const startDate = moment('10.10.2010', 'DD.MM.YYYY');
        const endDate = moment('10.10.2010', 'DD.MM.YYYY').add(1, 'days');
        const ruleModel: RuleModel = {
            startsAt: {
                date: startDate,
                time: '20:00',
            },
            stopsAt: {
                date: endDate,
                time: '21:00',
            },
            conditions: '{"condition":{"all_of":["tag1","tag2"]}}',
            workMode: 'workMode',
            billingSettings: {
                mode: 'mode',
                modeRule: 'modeRule',
            },
            displaySettings: {
                mode: 'mode',
                profile: 'profile',
            },
            offersGroup: 'offersGroup',
            features: [
                {
                    name: 'driver_fix',
                    settings: {roles: [{name: 'test_role'}]},
                },
                {
                    name: 'unknown',
                    settings: {},
                },
            ],
            $view: {
                oldRules: [{id: '123'}, {id: '234'}],
            },
        };
        const expected: ModeRulesCreateRequest = {
            rule: {
                conditions: {
                    condition: {
                        all_of: ['tag1', 'tag2'],
                    },
                },
                starts_at: '2010-10-10T20:00:00+04:00',
                stops_at: '2010-10-11T21:00:00+04:00',
                billing_settings: {
                    mode: 'mode',
                    mode_rule: 'modeRule',
                },
                display_settings: {
                    mode: 'mode',
                    profile: 'profile',
                },
                offers_group: 'offersGroup',
                features: [
                    {
                        name: 'driver_fix',
                        settings: {
                            roles: [{name: 'test_role'}],
                        },
                    },
                    {
                        name: 'unknown',
                        settings: {},
                    },
                ],
                work_mode: 'workMode',
            },
            rules_to_close: [{rule_id: '123'}, {rule_id: '234'}],
        };
        const res = prepareRuleViewToCreateRequest(ruleModel);
        expect(res).toEqual(expected);
    });
});
