import moment from 'moment';

import {TABLE_COMMISSION_DATE_FORMAT} from '../consts';
import {convertCommissionToTable} from '../converters';
import {CommissionType, DeprecatedCommissionType} from '../enums';
import {CommissionView, CorrectedCommissionContract} from '../types';

describe('convertCommissionToTable', () => {
    const invalidData: CorrectedCommissionContract = {
        id: '123',
        type: 'fixed_percent',
        begin: '2021-10-01T20:00:00',
        payment_type: 'payment_type',
        min_order_cost: 'min_order_cost',
        max_order_cost: 'max_order_cost',
        vat: 'vat',
        agent_percent: 'agent_percent',
        user_cancel_min_td: 0,
        user_cancel_max_td: 0,
        park_cancel_min_td: 0,
        park_cancel_max_td: 0,
        branding_discounts: [],
    };
    test('only required values with invalid data', () => {
        const expected: CommissionView = {
            id: '123',
            type: CommissionType.FixedPercent,
            begin: moment('2021-10-01T20:00:00', TABLE_COMMISSION_DATE_FORMAT),
            begin_time: '20:00',
            payment_type: 'payment_type',
            min_order_cost: undefined,
            max_order_cost: undefined,
            vat: 'NaN',
            agent_percent: 'NaN',
            user_cancel_min_td: 0,
            user_cancel_max_td: 0,
            park_cancel_min_td: 0,
            park_cancel_max_td: 0,
            branding_discounts: [],
            percent: undefined,
            asymp: undefined,
            tariff_classes: [],
            cancel_commission: undefined,
            cancel_percent: undefined,
            commission: undefined,
            cost_norm: undefined,
            end: undefined,
            end_time: undefined,
            expired_commission: undefined,
            expired_cost: undefined,
            expired_percent: undefined,
            max_commission_percent: undefined,
            numerator: undefined,
            unrealized_rate: undefined,
        };

        const res = convertCommissionToTable(invalidData);
        expect(res).toEqual(expected);
    });

    test('fullfilled values with invalid data', () => {
        const data: CorrectedCommissionContract = {
            ...invalidData,
            end: '2021-11-02T20:00:00',
            tariff_class: 'tariff_class',
            zone: 'zone',
            billable_cancel_distance: 0,
            tag: 'tag',
            pattern_id: 'pattern_id',
            is_editable: false,
            is_deletable: false,
            is_active: false,
            status: 'status',
            expired_percent: 'expired_percent',
            expired_cost: 'expired_cost',
            has_fixed_cancel_percent: false,
            cancel_percent: 'cancel_percent',
            percent: 'percent',
            cost_norm: 'cost_norm',
            numerator: 'numerator',
            asymp: 'asymp',
            max_commission_percent: 'max_commission_percent',
            min_rel_profit: 'min_rel_profit',
            ks: 'ks',
            kc: 'kc',
            max_diff: 'max_diff',
            commission: 'commission',
            cancel_commission: 'cancel_commission',
            expired_commission: 'expired_commission',
            log_count: 0,
        };
        const expected: CommissionView = {
            id: '123',
            type: CommissionType.FixedPercent,
            begin: moment('2021-10-01T20:00:00', TABLE_COMMISSION_DATE_FORMAT),
            begin_time: '20:00',
            billable_cancel_distance: 0,
            end: moment('2021-11-02T20:00:00', TABLE_COMMISSION_DATE_FORMAT),
            end_time: '20:00',
            payment_type: 'payment_type',
            min_order_cost: undefined,
            max_order_cost: undefined,
            vat: 'NaN',
            agent_percent: 'NaN',
            user_cancel_min_td: 0,
            user_cancel_max_td: 0,
            park_cancel_min_td: 0,
            park_cancel_max_td: 0,
            branding_discounts: [],
            asymp: undefined,
            tag: 'tag',
            zone: 'zone',
            tariff_class: 'tariff_class',
            tariff_classes: ['tariff_class'],
            cancel_commission: undefined,
            cancel_percent: 'NaN',
            commission: undefined,
            cost_norm: undefined,
            expired_commission: undefined,
            expired_cost: undefined,
            expired_percent: 'NaN',
            max_commission_percent: 'NaN',
            numerator: undefined,
            has_fixed_cancel_percent: false,
            ks: 'ks',
            kc: 'kc',
            max_diff: 'max_diff',
            min_rel_profit: 'min_rel_profit',
            pattern_id: 'pattern_id',
            percent: 'NaN',
        };

        const res = convertCommissionToTable(data);
        expect(res).toEqual(expected);
    });

    test('valid data', () => {
        const data: CorrectedCommissionContract = {
            id: '123',
            begin: '2021-10-01T20:00:00',
            payment_type: 'payment_type',
            user_cancel_min_td: 100,
            user_cancel_max_td: 100,
            park_cancel_min_td: 100,
            park_cancel_max_td: 100,
            branding_discounts: [
                {
                    marketing_level: ['level1', 'level2'],
                    value: '0.5',
                },
            ],
            asymp: '10',
            expired_commission: '10',
            commission: '10',
            cancel_commission: '10',
            expired_cost: '10',
            max_order_cost: '10',
            min_order_cost: '10',
            type: DeprecatedCommissionType.AsymptoticFormula,
            numerator: '10',
            cost_norm: '10',
            expired_percent: '0.1',
            cancel_percent: '0.1',
            vat: '1.0400',
            agent_percent: '0.1',
            percent: '0.1',
            max_commission_percent: '0.1',
        };
        const expected: CommissionView = {
            asymp: '10',
            expired_commission: '10',
            commission: '10',
            cancel_commission: '10',
            expired_cost: '10',
            max_order_cost: '10',
            min_order_cost: '10',
            numerator: 10,
            cost_norm: 10,
            expired_percent: '10',
            cancel_percent: '10',
            agent_percent: '10',
            percent: '10',
            max_commission_percent: '10',
            id: '123',
            type: CommissionType.AsymptoticFormula,
            begin: moment('2021-10-01T20:00:00', TABLE_COMMISSION_DATE_FORMAT),
            begin_time: '20:00',
            end: undefined,
            end_time: undefined,
            payment_type: 'payment_type',
            user_cancel_min_td: 1.67,
            user_cancel_max_td: 1.67,
            park_cancel_min_td: 1.67,
            park_cancel_max_td: 1.67,
            branding_discounts: [
                {
                    marketing_level: ['level1', 'level2'],
                    value: '50',
                },
            ],
            tariff_classes: [],
            vat: '4',
        };

        const res = convertCommissionToTable(data);
        expect(res).toEqual(expected);
    });
});
