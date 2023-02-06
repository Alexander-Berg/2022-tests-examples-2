import moment from 'moment';

import {driverFixRuleToModel} from '../converters';
import {DriverFixModel, DriverFixRule, SubventionType} from '../types';

const baseRule: DriverFixRule = {
    type: SubventionType.DriverFix,
    subvention_rule_id: 'subvention_rule_id',
    taxirate: 'taxirate',
    currency: 'currency',
    order_payment_type: 'order_payment_type',
    visible_to_driver: false,
    is_personal: false,
    cursor: 'cursor',
    hours: [1, 2],
    week_days: ['mon'],
    log: [],
    status: 'enabled',
    updated: '2019-10-10T15:30:00.000Z',
    start: '2019-10-10T15:30:00.000Z',
    end: '2020-10-10T20:00:00.000Z',
    tariff_zones: ['moscow', 'abakan'],
    commission_rate_if_fraud: '0.15',
    b2b_client_id: 'b2b_client_id',
    tags: ['tag1', 'tag2'],
    profile_payment_type_restrictions: 'cash',
    profile_tariff_classes: ['profile_tariff_classes'],
    geoareas: ['first', 'second'],
    time_zone: {
        id: 'id',
        offset: '+00:00'
    },
    rates: [
        {
            week_day: 'mon',
            start: '16:00',
            rate_per_minute: '5'
        }
    ]
};

describe('converters', () => {
    const expected: DriverFixModel = {
        commission_rate_if_fraud: '15',
        b2b_client_id: 'b2b_client_id',
        tag: 'tag1',
        begin_at: moment('2019-10-10T15:30:00.000Z').utcOffset('+00:00'),
        begin_at_time: '15:30',
        end_at: moment('2020-10-10T20:00:00.000Z').utcOffset('+00:00'),
        end_at_time: '20:00',
        zones: ['moscow'],
        profile_payment_type_restrictions: 'cash',
        profile_tariff_classes: ['profile_tariff_classes'],
        geoarea: 'first',
        time_zone: {
            id: 'id',
            offset: '+00:00'
        },
        rates: [
            {
                week_day: 'mon',
                start: '16:00',
                bonus_amount: '5'
            }
        ]
    };
    test('driverFixRuleToModel', () => {
        const rule: DriverFixRule = {
            ...baseRule
        };

        const res = driverFixRuleToModel(rule);
        expect(res).toEqual(expected);
    });

    test('driverFixRuleToModel with offset', () => {
        const rule: DriverFixRule = {
            ...baseRule,
            time_zone: {
                id: 'id',
                offset: '+03:00'
            }
        };
        const res = driverFixRuleToModel(rule);
        expect(res).toEqual({
            ...expected,
            begin_at: moment('2019-10-10T15:30:00.000Z').utcOffset('+03:00'),
            begin_at_time: '18:30',
            end_at: moment('2020-10-10T20:00:00.000Z').utcOffset('+03:00'),
            end_at_time: '23:00',
            time_zone: {
                id: 'id',
                offset: '+03:00'
            },
        });
    });
});
