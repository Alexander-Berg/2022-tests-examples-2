import moment from 'moment';

import {DATE_SERVER_FORMAT} from '../../consts';
import {ModeRuleData, RuleModel} from '../../types';
import {prepareModeRuleToRuleView} from '../prepareModeRuleToRuleView';

describe('prepareModeRuleToRuleView', () => {
    test('empty', () => {
        const rule: ModeRuleData = {};
        const expected: RuleModel = {
            billingSettings: {
                modeRule: undefined,
                mode: undefined,
            },
            conditions: undefined,
            displaySettings: {
                mode: undefined,
                profile: undefined,
            },
            features: undefined,
            featuresSchemaVersion: undefined,
            offersGroup: undefined,
            startsAt: undefined,
            stopsAt: undefined,
            workMode: undefined,
        };
        const res = prepareModeRuleToRuleView(rule);
        expect(res).toEqual(expected);
    });

    test('filled', () => {
        const featuresVersion = 1;
        const rule: ModeRuleData = {
            work_mode: 'workMode',
            starts_at: '2010-10-10T20:00:00+04:00',
            stops_at: '2010-10-10T20:00:00+04:00',
            billing_settings: {
                mode: 'mode',
                mode_rule: 'modeRule',
            },
            display_settings: {
                mode: 'mode',
                profile: 'profile',
            },
            offers_group: 'offersGroup',
            conditions: {
                condition: {
                    all_of: ['tag'],
                },
            },
            features: [
                {
                    name: 'reposition',
                    settings: {
                        profile: 'profile',
                    },
                },
                {
                    name: 'unknown',
                },
            ],
        };
        const expected: RuleModel = {
            billingSettings: {
                modeRule: 'modeRule',
                mode: 'mode',
            },
            conditions: '{\n  "condition": {\n    "all_of": [\n      "tag"\n    ]\n  }\n}',
            displaySettings: {
                mode: 'mode',
                profile: 'profile',
            },
            features: [
                {
                    name: 'reposition',
                    settings: {profile: 'profile'},
                },
                {
                    name: 'unknown',
                },
            ],
            offersGroup: 'offersGroup',
            startsAt: {
                date: moment('2010-10-10T20:00:00+04:00', DATE_SERVER_FORMAT).startOf('day'),
                time: '20:00',
            },
            stopsAt: {
                date: moment('2010-10-10T20:00:00+04:00', DATE_SERVER_FORMAT).startOf('day'),
                time: '20:00',
            },
            workMode: 'workMode',
            featuresSchemaVersion: 1,
        };

        const res = prepareModeRuleToRuleView(rule, featuresVersion);
        expect(res).toEqual(expected);
    });
});
